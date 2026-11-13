# Start a playbook and track its session

This recipe starts the existing **Investigate an incident** playbook, polls its
session, and discovers its reports. It does not publish or modify playbook
definitions.

Complete the [common setup](README.md#setup-and-notation). In addition to Graph
read access, you need permission to start the selected playbook, an enabled
playbook/agent configuration, and an incident accessible in the selected tenant.
Starting a session performs real agent work and can incur usage charges.

## 1. Discover the playbook

```http
GET {graphBaseUrl}/playbookDefinitions?$select=id,uniqueName,displayName,acceptedInputTypes
Authorization: Bearer <access-token>
Accept: application/json
```

Follow every next link and select the item whose `uniqueName` is
`investigate-incident`. Do not assume a server-side catalog name filter is
supported or hard-code a definition ID from another tenant.

Illustrative item from the collection's `value` array:

```json
{
  "id": "<playbook-definition-id>",
  "uniqueName": "investigate-incident",
  "displayName": "Investigate an incident",
  "acceptedInputTypes": [
    "defenderIncidentId"
  ]
}
```

If the playbook is absent or does not accept `defenderIncidentId`, stop and
check the catalog and setup for your environment. The accepted-type list is
not a complete description of required slots, cardinality, or dependencies.
Confirm the selected playbook's input requirements in its current product
documentation before creating a session; do not infer them from this list alone.

Optionally read the selected definition directly:

```http
GET {graphBaseUrl}/playbookDefinitions('<playbook-definition-id>')?$select=id,uniqueName,displayName,acceptedInputTypes
Authorization: Bearer <access-token>
Accept: application/json
```

## 2. Start a session

Replace `<incident-id>` with the identifier of an incident in your tenant.
Replace `{graphBaseUrl}` in both the request URL and the JSON binding with
the same enabled Graph endpoint.

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions('<playbook-definition-id>')",
  "inputs": [
    {
      "kind": "defenderIncidentId",
      "value": "<incident-id>"
    }
  ]
}
```

The binding must be an absolute Microsoft Graph URL to the discovered
definition, not the playbook's slug or a new definition object. Inputs use
Graph's `kind` and `value` fields. Do not copy direct-service `sourceId`,
`sourceType`, or `type` fields into this request.

Expect `201 Created` with the created session and a `Location` header.
An illustrative body excerpt is:

```json
{
  "id": "<session-id>",
  "status": "notStarted"
}
```

The session may already have progressed to another state by the time creation
returns. Save the returned session ID and Location. `201` means creation was
accepted successfully, not that the investigation has completed.

Do not automatically retry this POST after a timeout: a session may already
have been created, and an unconditional retry can start duplicate work.
Reconcile against visible sessions before deciding whether to submit again.

## 3. Track progress

Read the created session using its returned ID, or use its trusted Graph
Location:

```http
GET {graphBaseUrl}/sessions('<session-id>')?$select=id,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

Use bounded polling, for example once every 30 seconds for up to five minutes,
and honor `Retry-After`. A polling deadline ends this client-side wait; it does
not cancel the session.

| Observed state | What to do |
| --- | --- |
| `notStarted` | Wait within the polling deadline. |
| `running`, with `waitingForInput` detail | Pause polling and surface the need for input. |
| `running`, with another or missing detail | Continue waiting within the deadline. |
| `succeeded` | Inspect available outputs. |
| `failed` | Inspect the detail, runs, and messages; this includes stopped/canceled sessions. |
| Unknown status or detail | Preserve it; do not infer success or poll without a deadline. |

Older deployments may use `pendingInput` for waiting and `canceled` for stopped
sessions. Do not treat status-detail strings as a closed enum. These examples do
not assume an API for supplying follow-up input.

Read available agent runs when you need more context:

```http
GET {graphBaseUrl}/sessions('<session-id>')/agentRuns?$select=id,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

## 4. Retrieve reports

Follow [Retrieve session reports](retrieve-session-reports.md) to list session
outputs and download a selected summary or artifact. A completed lifecycle does
not guarantee a particular report exists or is ready for download.

## Cleanup

If the session you just created is still active and you want to stop it, request
cancellation explicitly:

```http
POST {graphBaseUrl}/sessions('<session-id>')/cancel
Authorization: Bearer <access-token>
Accept: application/json
```

Send no request body. Expect `202 Accepted`, then poll the session to observe
the resulting state. Acceptance is not confirmation that the backend has fully
stopped. A stopped session can be represented as `failed` with `stopped` detail
(or `canceled` on an older deployment).

Cancel only the session created for this exercise. Cancellation does not delete
its history, reverse completed actions, or eliminate charges already incurred.
Remove downloaded reports and clear your HTTP client's token when finished.
