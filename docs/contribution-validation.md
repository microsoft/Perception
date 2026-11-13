# Contribution validation

Each immediate contribution folder under `workflows`, `scripts`,
or `connectors` must contain `README.md` and `manifest.json`.
The starter package in `templates\contribution` is also checked.

## Manifest

| Field | Requirement |
| --- | --- |
| `name` | Lowercase, hyphen-separated identifier matching the contribution folder |
| `displayName` | Nonempty human-readable name |
| `description` | Nonempty description of the contribution |
| `category` | `workflows`, `scripts`, or `connectors` |
| `entryPoint` | Relative path to an existing file inside the contribution |
| `inputs` | Array of input definitions; use an empty array if none |

Each input needs a unique `name`, nonempty `description`, `type` (`string`,
`integer`, `number`, or `boolean`), and boolean `required` flag.
Paths must remain inside the contribution folder.
The template is exempt from folder-name matching and contains no runnable content.

## Automated checks

The validator uses only Python's standard library. It checks package files,
parseable JSON without duplicate keys, required metadata, category consistency,
entry-point containment, and input definitions. The workflow also tests the validator.

These are structural checks, not secret scanning, complete schema validation,
runtime input validation, deployment testing, or API compatibility verification.

## Approval and live validation

Maintainers review documentation, source, permission use, dependency licensing,
and contribution-specific tests. Configure secret scanning and required reviewer
approval in repository settings.

Live tenant validation is maintainer-controlled and separate from PR CI. Do not
give external PR workflows deployment credentials or execute their deployment
artifacts in a privileged environment. Record sanitized test evidence in the PR.
