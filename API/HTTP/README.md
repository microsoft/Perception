# Perception HTTP examples

Use the [HTTP examples](Examples/README.md) to call the Perception APIs through
Microsoft Graph without an SDK. Recipes cover session filtering, report
retrieval, and starting, monitoring, and canceling playbook sessions.

## Prerequisites and permissions

Use an HTTP client such as Graph Explorer or Postman, a tenant with the API
enabled, and the [shared delegated authentication setup](../../docs/authentication.md#graph-request-examples).
Reads require `Perception.Read.All`; creating or canceling sessions requires
`Perception.Manage.All`, which also permits reads. Resource access and consent
requirements apply separately.

## Inputs and usage

Follow [Setup and notation](Examples/README.md#setup-and-notation) for endpoint,
token, and identifier placeholders. Each recipe documents its additional inputs.
Replace placeholders with values from your authorized tenant and API responses;
keep tokens in your client's local authentication settings, never in these files.

Run requests individually and inspect the response before continuing. These are
Markdown recipes, not executable scripts or an automatically running collection.
See the [Insomnia collection](../Insomnia-collection/README.md) for importable requests.

## Costs and cleanup

Reads don't create sessions. Starting a playbook runs real agent work and can
incur usage charges. Cancellation doesn't undo completed work or prior charges.
Follow the [playbook cleanup instructions](Examples/start-playbook.md#cleanup),
delete downloaded tenant data, and clear tokens when finished.

## Validation

Run the [repository checks](../../CONTRIBUTING.md#local-checks). Static validation
checks the package metadata, not live API behavior. The examples describe
response checks, paging, input selection, and bounded polling; validate these in
your own authorized environment before integrating them. Example responses are
illustrative, not evidence of live validation.
