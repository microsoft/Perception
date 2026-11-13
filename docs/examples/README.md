# Microsoft Graph request examples

These HTTP recipes demonstrate common Perception tasks without requiring a
particular programming language or SDK.

| Scenario | Examples |
| --- | --- |
| [Filter sessions](filter-sessions.md) | Find your sessions, failed sessions, sessions waiting for input, and combine criteria. |
| [Retrieve session reports](retrieve-session-reports.md) | Discover summaries and artifacts, then download their content. |
| [Start a playbook](start-playbook.md) | Select a catalog definition, supply inputs, create a session, and track its progress. |

## Setup and notation

Use the [shared authentication guidance](../authentication.md#graph-request-examples)
before sending requests. Read-only recipes require access to the selected sessions;
starting or canceling a session also requires permission to operate playbooks.
The optional `/me` request requires delegated `User.Read`.

Replace these placeholders before running a request:

| Placeholder | Meaning |
| --- | --- |
| `{graphBaseUrl}` | The tenant-enabled Microsoft Graph endpoint through `security/agenticSecurity`, with no trailing slash. |
| `<access-token>` | A Microsoft Graph access token for the selected tenant and permitted operation. |
| `<user-id>` | Your Entra user object ID in that tenant. |
| `<session-id>` | A session ID returned by the service. |
| `<playbook-definition-id>` | The `id` of a playbook returned by catalog discovery. |
| `<output-id>` | An output ID returned for the selected session. |

For example, the standard beta URL shape is
`https://graph.microsoft.com/beta/security/agenticSecurity`. This is not a claim
that the API is enabled at that URL for every tenant. Confirm the endpoint,
availability, and permission names for your deployment before using these recipes.
Do not substitute a direct Perception service URL: its audience, wire names, and
capabilities differ from Microsoft Graph.

The recipes are documentation samples, not a record of live Graph validation.
Responses are synthetic excerpts; annotations and other properties are omitted.
Run the requests in an HTTP client such as Graph Explorer, where the endpoint is
available, or Postman. Configure the bearer token in the client's authentication
settings instead of saving it with the requests.

## Filtering and paging

These examples use server-side `$filter` only for `status`. They do not assume
that Graph exposes every filter implemented by the direct Perception API.
In particular, they use client-side selection for the recorded user,
`statusDetail`, creation time, and selected playbook.

URI-encode query parameter values when sending requests; the examples encode
spaces and string delimiters in `$filter`. Treat IDs as opaque strings. When
placing an ID inside an OData string key, double any apostrophe in it and
URI-encode as needed.

For every collection request, process `value` and follow each returned
`@odata.nextLink` until it is absent. Use the complete link unchanged, with the
same Graph authentication and only at a trusted Graph endpoint. Do not rebuild
continuation URLs or add filters to them. Client-side selection must process
every page, including pages with no matches.

Do not request `$count`, `$expand`, `$orderby`, or arbitrary filters in these
recipes. A page's item count is not the collection total. An empty `value` array
is a valid result, not a request failure.

## Errors, costs, and cleanup

For `400`, check property names, query support, and input kinds. For `401` or
`403`, check token audience, tenant access, consent, and operation permissions.
A `404` can indicate an unavailable endpoint or an inaccessible/missing resource.
For `429`, honor `Retry-After`; use bounded retries with backoff for transient
read failures. Capture the Graph error code and request ID for troubleshooting,
not the bearer token.

Read-only recipes create no sessions or infrastructure. They make API requests
and may download files. Playbook creation starts actual agent work and can incur
your environment's normal usage charges; polling and cancellation do not undo
work already performed. See the [playbook recipe](start-playbook.md#cleanup).
Remove downloaded tenant data when no longer needed, and clear tokens from the
HTTP client after testing.
