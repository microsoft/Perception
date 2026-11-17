# Filter Perception sessions

Use these recipes for personal session views, troubleshooting, and attention
queues. Complete the [common setup](README.md#setup-and-notation) with delegated
`Perception.Read.All` (or `Perception.Manage.All`). All requests are read-only.
See [List sessions](https://learn.microsoft.com/en-us/graph/api/agenticsecurityroot-list-sessions?view=graph-rest-beta)
for supported query parameters.

## Understand status and status detail

The published [session lifecycle table](https://learn.microsoft.com/en-us/graph/api/investigationsession-get?view=graph-rest-beta#session-status-and-status-details)
maps lifecycle conditions to these five distinct combinations:

| `status` | `statusDetail` | Interpretation |
| --- | --- | --- |
| `running` | `inProgress` | Processing is in progress. |
| `running` | `waitingForInput` | The session requires input; repeated polling won't supply it. |
| `succeeded` | `completed` | Processing completed successfully. |
| `failed` | `stopped` | The session is stopping, stopped, or archived and reported as canceled. |
| `notStarted` | `completed` | Missing/unrecognized underlying state fallback, not success. |

Use `status` to determine success, not `statusDetail` or HTTP `200` alone.
Preserve unrecognized values without assuming completion.

## Find my sessions

Here, "mine" means the recorded initiator matches your Microsoft Entra user
object ID, not every session where you participated. If you don't know your ID,
this optional lookup requires delegated `User.Read`:

```http
GET https://graph.microsoft.com/v1.0/me?$select=id,displayName
Authorization: Bearer <access-token>
Accept: application/json
```

Use the same signed-in user and tenant for the session requests:

```http
GET {graphBaseUrl}/sessions?$select=id,displayName,status,statusDetail,initiatedBy,createdDateTime&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

Illustrative item from the collection's `value` array:

```json
{
  "id": "<session-id>",
  "displayName": "Investigate attack",
  "status": "running",
  "statusDetail": "waitingForInput",
  "initiatedBy": {
    "user": {
      "id": "<user-id>",
      "displayName": "Example User"
    }
  },
  "createdDateTime": "2026-11-01T10:00:00Z"
}
```

Follow all pages and retain items whose `initiatedBy.user.id` equals `<user-id>`.
You can search `initiatedBy.user.displayName` client-side for convenience, but
names can change and aren't unique; use IDs for definitive matching. If identity
fields are absent, they can't establish ownership.

Don't send the direct API's `$filter=initiator eq 'me'` to Graph; it isn't
advertised by the Graph method.

## Separate active work from sessions waiting for input

First narrow to running sessions on the server:

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27running%27&$select=id,displayName,status,statusDetail&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

On every page, retain `statusDetail: inProgress` for active work, or
`statusDetail: waitingForInput` for an attention queue. Another or missing detail
doesn't establish either condition. Don't send a server-side `statusDetail`
filter; it isn't supported by the published method.

These examples don't expose a way to answer pending input. Surface the session
to the operator rather than assuming more polling will resolve it.

## Review finished outcomes

Retrieve succeeded and failed sessions together using the supported `in` operator:

```http
GET {graphBaseUrl}/sessions?$filter=status%20in%20%28%27succeeded%27%2C%27failed%27%29&$select=id,displayName,status,statusDetail&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

Partition every page by `status`: `succeeded` indicates success, while `failed`
includes stopped/canceled sessions and isn't proof of an agent execution error.
To request only failures:

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27failed%27&$select=id,displayName,status,statusDetail&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

Inspect available agent runs for context:

```http
GET {graphBaseUrl}/sessions/<session-id>/agentRuns?$select=id,agent,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

Follow any next link. Neither session details nor agent runs guarantee a failure
reason; see [List agentRuns](https://learn.microsoft.com/en-us/graph/api/investigationsession-list-agentruns?view=graph-rest-beta).

## Combine criteria: my waiting sessions for a playbook and time window

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27running%27&$select=id,displayName,status,statusDetail,initiatedBy,createdDateTime&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

For every page, retain only sessions where:

1. `initiatedBy.user.id` matches `<user-id>`.
2. `statusDetail` equals `waitingForInput`.
3. `createdDateTime` is at or after `2026-11-01T00:00:00Z` and before
   `2026-11-08T00:00:00Z`, comparing timestamp instants rather than text.

For each remaining candidate, resolve its selected playbook:

```http
GET {graphBaseUrl}/sessions/<session-id>/playbookDefinition?$select=id,uniqueName
Authorization: Bearer <access-token>
Accept: application/json
```

Keep the session if the returned definition's `id` matches your
[catalog selection](start-playbook.md#1-discover-the-playbook).
Interactive sessions without a catalog binding can return `404 Not Found`;
exclude those from this playbook-specific result, while checking the Graph
error for other missing/inaccessible-resource causes.

This adds one read per candidate, so exclude other nonmatches first. Compute the
result size locally after all pages, not through `$count`. State can change
while paging; refresh a selected session before acting.

## Verify the result

Confirm each retained item meets the criteria. No matches is valid. These
requests create no resources; follow the
[common token and data cleanup guidance](README.md#errors-costs-and-cleanup).
