# Contribution validation

Each immediate contribution folder under `workflows`, `scripts`, `dashboards`,
`connectors`, or `API` must contain `README.md` and `manifest.json`.
The validator also checks the starter package in `templates/contribution`.

## Manifest

| Field | Requirement |
| --- | --- |
| `name` | Lowercase, hyphen-separated identifier matching the contribution folder |
| `displayName` | Nonempty human-readable name |
| `description` | Nonempty description of the contribution |
| `category` | `workflows`, `scripts`, `dashboards`, `connectors`, or `API` |
| `entryPoint` | Relative path to an existing file inside the contribution |
| `inputs` | Array of input definitions; use an empty array if none |

Each input needs a unique `name`, nonempty `description`, `type` (`string`,
`integer`, `number`, or `boolean`), and boolean `required` flag.
Paths must remain inside the contribution folder.
The template is exempt from folder-name matching and contains no runnable content.

Under `API`, folder names can preserve product casing. For example,
`API\Insomnia-collection` uses the lowercase manifest name `insomnia-collection`
and category `API`. Other categories retain exact lowercase folder-name matching.

## Automated checks

The validator uses only Python's standard library. It checks package files,
parseable JSON without duplicate keys, required metadata, category consistency,
entry-point containment, and input definitions. The workflow also tests the validator.

The same test command also checks the Graph Insomnia collection's import
structure, public routes, blank credentials, separate write authentication,
and request bodies. These checks make no network requests.

These are structural checks, not secret scanning, complete schema validation,
runtime input validation, deployment testing, or API compatibility verification.

## Approval and live validation

Maintainers review documentation, source, permission use, dependency licensing,
and contribution-specific tests. Configure secret scanning and required reviewer
approval in repository settings.

Live tenant validation is maintainer-controlled and separate from PR CI. Do not
give external PR workflows deployment credentials or execute their deployment
artifacts in a privileged environment. Record sanitized test evidence in the PR.
