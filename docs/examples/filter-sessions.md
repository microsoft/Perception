# Filter Perception sessions

Use these recipes to build a personal session view, a troubleshooting list, or
a queue of sessions requiring attention. Complete the [common setup](README.md#setup-and-notation)
first. All requests here are read-only.

## Find my sessions

In this Graph recipe, "mine" means the session's recorded
`initiatedBy.user.id` matches your Entra user object ID. It does not discover
every session where you participated. If that optional identity is absent,
the session cannot be classified as yours using this field alone.

If you do not already know your object ID, this optional request uses delegated
`User.Read`. Use the same signed-in user and tenant as the session requests.

```http
GET https://graph.microsoft.com/v1.0/me?$select=id
Authorization: Bearer <access-token>
Accept: application/json
```

Illustrative response:

```json
{
  "id": "<user-id>"
}
```

List visible sessions and request the identity needed for client-side selection:

```http
GET {graphBaseUrl}/sessions?$select=id,displayName,status,statusDetail,initiatedBy,createdDateTime&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

Illustrative item from the collection's `value` array:

```json
{
  "id": "<session-id>",
  "displayName": "Investigate an incident",
  "status": "running",
  "statusDetail": "waitingForInput",
  "initiatedBy": {
    "user": {
      "id": "<user-id>"
    }
  },
  "createdDateTime": "2026-11-01T10:00:00Z"
}
```

Follow all pages and retain items whose `initiatedBy.user.id` equals
`<user-id>`. Do not match on display name.

Do not send `$filter=initiator eq 'me'` to Graph based on the direct API's
documentation: that backend filter has participant semantics and is not
advertised by the Graph contract used here.

## Find failed sessions

Apply the supported status filter on the server:

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27failed%27&$select=id,displayName,status,statusDetail&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

A successful request returns `200 OK` with a collection. Follow every next link;
each returned item should have `status: failed`.

`failed` includes stopped/canceled sessions. It is not proof of an agent
execution error, and `statusDetail` is not a root-cause diagnostic. A stopped
session may expose `stopped`; older deployments may expose `canceled`.
Preserve unrecognized detail strings rather than treating them as a closed enum.

To inspect an individual session, read its agent runs and transcript:

```http
GET {graphBaseUrl}/sessions('<session-id>')/agentRuns?$select=id,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

```http
GET {graphBaseUrl}/sessions('<session-id>')/messages
Authorization: Bearer <access-token>
Accept: application/json
```

These reads provide available evidence; they do not guarantee a failure reason.
Both collections can be paged.

## Find sessions waiting for input

Waiting sessions have a running lifecycle status, so first narrow on the server:

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27running%27&$select=id,displayName,status,statusDetail&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

On every page, retain items whose `statusDetail` equals `waitingForInput`.
Older deployments may return `pendingInput`; include that value only when your
deployment uses that lifecycle vocabulary. Running sessions with another or
missing detail must not be assumed to need input.

This two-step selection intentionally avoids a server-side `statusDetail`
filter, which is not advertised by the Graph contract used here. The result is
an attention queue, not an instruction to submit a response: these examples do
not assume Graph exposes an operation for answering pending input.

## Combine criteria: my waiting sessions for a playbook and time window

Use the running-status filter and request all fields needed for local selection:

```http
GET {graphBaseUrl}/sessions?$filter=status%20eq%20%27running%27&$select=id,displayName,status,statusDetail,initiatedBy,createdDateTime&$top=20
Authorization: Bearer <access-token>
Accept: application/json
```

For every page, retain only sessions where:

1. `initiatedBy.user.id` matches `<user-id>`.
2. `statusDetail` indicates waiting for input using the vocabulary above.
3. `createdDateTime` is at or after `2026-11-01T00:00:00Z` and before
   `2026-11-08T00:00:00Z`, comparing timestamp instants rather than text.

For each remaining candidate, resolve its selected playbook:

```http
GET {graphBaseUrl}/sessions('<session-id>')/playbookDefinition?$select=id,uniqueName
Authorization: Bearer <access-token>
Accept: application/json
```

Keep the session if the returned definition's `id` matches the playbook you
selected from the [catalog](start-playbook.md#1-discover-the-playbook).
This adds one read per candidate; avoid making it for sessions already excluded
by the local criteria.

The resulting list is "my recorded-initiator sessions, currently waiting for
input, created in this interval, using this playbook." Its size is computed
locally after all pages, not obtained through `$count`. Session state can change
while you page; refresh a selected session before acting on it.

## Verify the result

Confirm each retained item meets the scenario's criteria. No matches is valid.
These requests create no resources and require no session cleanup; follow the
[common token and data cleanup guidance](README.md#errors-costs-and-cleanup).
