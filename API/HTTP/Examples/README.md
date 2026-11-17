# Perception API examples

Perception is Microsoft's multi-agent security system. It brings specialized AI
agents into security workflows while keeping critical decisions under human
control. See the [Perception documentation](https://learn.microsoft.com/en-us/security/agentic-security/)
for product concepts and capabilities.

Use the Perception APIs through Microsoft Graph to integrate agentic security
workflows into your applications. For the API reference and an end-to-end
walkthrough, see
[Use Perception in Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/agenticsecurity-apioverview?view=graph-rest-beta).

Choose a scenario to view language-neutral HTTP requests and sample responses:

| Scenario | Examples |
| --- | --- |
| [Filter sessions](filter-sessions.md) | Match your sessions, distinguish active work from input prompts, review finished outcomes, and combine criteria. |
| [Retrieve session reports](retrieve-session-reports.md) | List summaries and artifacts, then download their content. |
| [Start a playbook](start-playbook.md) | Select a catalog definition, supply inputs, create a session, and track its progress. |

## Setup and notation

Complete the [shared authentication setup](../../../docs/authentication.md#graph-request-examples)
before sending requests. Read-only recipes use delegated `Perception.Read.All`;
creating or canceling sessions requires `Perception.Manage.All`, which also
permits reads. The optional `/me` lookup requires delegated `User.Read`.

Replace these placeholders in your HTTP client, such as Graph Explorer or
Postman, and store bearer tokens only in the client's local authentication settings:

| Placeholder | Meaning |
| --- | --- |
| `{graphBaseUrl}` | Microsoft Graph agentic security base URL without a trailing slash: `https://graph.microsoft.com/beta/security/agenticSecurity`. Confirm tenant availability. |
| `<access-token>` | Delegated Microsoft Graph bearer token for the target tenant and operation. |
| `<user-id>` | Your Microsoft Entra user object ID in that tenant. |
| `<session-id>` | Session `id` returned by the API. |
| `<playbook-definition-id>` | Playbook definition `id` returned by catalog discovery. |
| `<output-id>` | Output `id` returned for the selected session. |

Direct Perception service URLs and tokens aren't interchangeable with Microsoft
Graph. Sample responses are illustrative excerpts, not live API captures.
Treat IDs as opaque strings and URI-encode each substituted path segment once.

## Filtering and paging

- **Server and client filtering:** These session examples apply `$filter` only
  to `status`. Match user, `statusDetail`, creation time, and playbook in your client.
- **Paging:** Follow each complete `@odata.nextLink` unchanged until absent,
  using Graph authentication only at a trusted Graph endpoint. Client-side checks
  must cover every page, including pages with no matches.
- **Supported query options:** Don't use `$count`, `$expand`, `$orderby`, or
  unverified filters. Check individual method pages in the
  [API reference](https://learn.microsoft.com/en-us/graph/api/resources/agenticsecurity-apioverview?view=graph-rest-beta).
  An empty collection is valid; a page's size isn't the collection total.

## Errors, costs, and cleanup

- **Errors and throttling:** Honor `Retry-After` for HTTP `429`; use bounded
  retries for transient read failures. Record the Graph error code and
  `request-id`, never the bearer token. See
  [Microsoft Graph error responses](https://learn.microsoft.com/en-us/graph/errors)
  for status codes and retry guidance.
- **Usage costs:** Reads don't create sessions. Starting a playbook runs real
  agent work and can incur usage charges. Canceling stops remaining work without
  undoing completed work; see [Start a playbook](start-playbook.md#cleanup).
- **Cleanup:** Delete downloaded tenant data when no longer needed and clear
  bearer tokens from your HTTP client after testing.
