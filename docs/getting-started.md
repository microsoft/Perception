# Getting started

This repository provides a home for community-built integrations and extensions
using Perception. Customers, partners, and Microsoft contributors can propose
content for others to review, deploy, and use in their own environments.

Community contributions are separate from the Perception product. This scaffold
does not include service implementation code, a standalone SDK, or runnable
scenario packages yet. The [HTTP examples](examples/README.md) demonstrate
Microsoft Graph requests for session filtering, report retrieval, and playbook
execution.

## Browse content

| Directory | Content |
| --- | --- |
| [HTTP examples](examples/README.md) | Language-neutral Microsoft Graph request recipes |
| [workflows](../workflows/README.md) | End-to-end processes using Perception, including Logic Apps |
| [scripts](../scripts/README.md) | Standalone API-driven utilities |
| [connectors](../connectors/README.md) | Reusable adapters and plugins connecting Perception to other systems |

Categories describe functionality, not contributor ownership; both Microsoft and
customer/partner contributions can belong in any category.

## Use a contribution

Once content is available:

1. Browse the categories and read the selected contribution's README.
2. Review permissions, dependencies, costs, and expected resource changes.
3. Choose its supported API entry point and follow its authentication instructions.
4. Review the source and deploy or run it in an environment you are authorized to use.
5. Verify expected results and follow its cleanup instructions.

Deployable integrations may orchestrate existing Perception playbooks; they do not
imply that Perception exposes an API for publishing new playbook definitions.

See [authentication](authentication.md), [deployment guidance](deployment-guide.md),
and the repository's [support guidance](../SUPPORT.md).

## Contribute

Start with [CONTRIBUTING.md](../CONTRIBUTING.md) and the
[contribution template](../templates/contribution/README.md).
Static checks and maintainer review are described in
[contribution validation](contribution-validation.md).

The content-category approach is inspired by the
[Microsoft Security Copilot community repository](https://github.com/Azure/Security-Copilot).
