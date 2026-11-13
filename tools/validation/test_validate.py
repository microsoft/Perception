import json
import tempfile
import unittest
from pathlib import Path

from validate import validate_package, validate_repository


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for category in ("workflows", "scripts", "connectors"):
            (self.root / category).mkdir()
        self.package = self.root / "scripts" / "example-script"
        self.package.mkdir()
        (self.package / "README.md").write_text("Example script", encoding="utf-8")
        (self.package / "run.py").write_text("print('example')", encoding="utf-8")
        self.manifest = {
            "name": "example-script",
            "displayName": "Example script",
            "description": "Illustrative API utility",
            "category": "scripts",
            "entryPoint": "run.py",
            "inputs": [
                {
                    "name": "targetUrl",
                    "description": "Authorized target URL",
                    "type": "string",
                    "required": True,
                }
            ],
        }
        self.save()

    def save(self):
        (self.package / "manifest.json").write_text(
            json.dumps(self.manifest), encoding="utf-8"
        )

    def test_valid_package(self):
        self.assertEqual(validate_package(self.package, "scripts"), [])

    def test_workflow_and_connector_packages(self):
        for category in ("workflows", "connectors"):
            with self.subTest(category=category):
                package = self.root / category / "example-script"
                package.mkdir(parents=True)
                for filename in ("README.md", "run.py"):
                    (package / filename).write_text(
                        (self.package / filename).read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                (package / "manifest.json").write_text(
                    json.dumps(dict(self.manifest, category=category)),
                    encoding="utf-8",
                )
                self.assertEqual(validate_package(package, category), [])

    def test_missing_readme_or_manifest_is_rejected(self):
        for filename in ("README.md", "manifest.json"):
            with self.subTest(filename=filename):
                path = self.package / filename
                content = path.read_text(encoding="utf-8")
                path.unlink()
                self.assertTrue(validate_package(self.package, "scripts"))
                path.write_text(content, encoding="utf-8")

    def test_metadata_and_category_must_match(self):
        self.manifest.update(
            name="other-script", category="workflows", description=""
        )
        self.save()
        errors = validate_package(self.package, "scripts")
        self.assertTrue(any("name must match" in error for error in errors))
        self.assertTrue(any("category must match" in error for error in errors))
        self.assertTrue(any("description must be" in error for error in errors))

    def test_entry_point_cannot_escape_or_be_missing(self):
        (self.package.parent / "outside.py").write_text("", encoding="utf-8")
        for entry in ("../outside.py", "..\\outside.py", str(self.package / "run.py")):
            with self.subTest(entry=entry):
                self.manifest["entryPoint"] = entry
                self.save()
                self.assertTrue(
                    any("stay inside" in error for error in validate_package(self.package))
                )
        self.manifest["entryPoint"] = "missing.py"
        self.save()
        self.assertTrue(
            any("existing file" in error for error in validate_package(self.package))
        )

    def test_input_definitions_reject_duplicates_and_invalid_types(self):
        self.manifest["inputs"].append(dict(self.manifest["inputs"][0]))
        self.manifest["inputs"][0].update(type="object", required="yes")
        self.save()
        errors = validate_package(self.package)
        self.assertTrue(any("must be unique" in error for error in errors))
        self.assertTrue(any(".type must be" in error for error in errors))
        self.assertTrue(any(".required must be" in error for error in errors))

    def test_malformed_manifest_is_reported(self):
        for text in ('{"name":', '{"name":"one","name":"two"}', "[]"):
            with self.subTest(text=text):
                (self.package / "manifest.json").write_text(text, encoding="utf-8")
                self.assertTrue(validate_package(self.package))

    def test_repository_checks_every_package(self):
        template = self.root / "templates" / "contribution"
        template.mkdir(parents=True)
        for filename in ("README.md", "manifest.json", "run.py"):
            (template / filename).write_text(
                (self.package / filename).read_text(encoding="utf-8"), encoding="utf-8"
            )
        self.assertEqual(validate_repository(self.root), [])
        (self.root / "scripts" / "undocumented").mkdir()
        errors = validate_repository(self.root)
        self.assertTrue(any("undocumented" in error for error in errors))

    def test_repository_requires_supported_category_directories(self):
        (self.root / "connectors").rmdir()
        self.assertIn(
            "connectors: category directory is missing",
            validate_repository(self.root),
        )

    def test_dashboard_manifest_category_is_rejected(self):
        self.manifest["category"] = "dashboards"
        self.save()
        self.assertIn(
            "category must be one of workflows, scripts, connectors",
            validate_package(self.package),
        )


if __name__ == "__main__":
    unittest.main()
