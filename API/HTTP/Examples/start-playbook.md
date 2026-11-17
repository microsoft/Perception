# Start a playbook and track its session

Discover playbooks, start an agentic session with the matching inputs, monitor
progress, and retrieve outputs. These examples don't publish or modify playbook
definitions. See
[Use Perception in Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/agenticsecurity-apioverview?view=graph-rest-beta),
[Create session](https://learn.microsoft.com/en-us/graph/api/agenticsecurityroot-post-sessions?view=graph-rest-beta),
and [Work with playbooks](https://learn.microsoft.com/en-us/security/agentic-security/agentic-security-playbooks).

Complete the [common setup](README.md#setup-and-notation) with delegated
`Perception.Manage.All`. Confirm your user has **Run** access to every agent in
the selected playbook and access to its target resources.

**Caution:** Creating a session starts real agent work and can incur usage charges.

## 1. Discover the playbook

```http
GET {graphBaseUrl}/playbookDefinitions?$select=id,uniqueName,displayName,acceptedInputTypes
Authorization: Bearer <access-token>
Accept: application/json
```

Follow every next link and select by `uniqueName` in your client. The published
[list method](https://learn.microsoft.com/en-us/graph/api/agenticsecurityroot-list-playbookdefinitions?view=graph-rest-beta)
supports `$select`, not `$filter=uniqueName eq '...'`.

Illustrative item from the collection's `value` array:

```json
{
  "id": "732b84ae-26ad-4eb4-b4fb-f2f45d7571e6",
  "uniqueName": "investigate-incident",
  "displayName": "Investigate attack",
  "acceptedInputTypes": [
    "defenderIncidentId",
    "defenderAlertId"
  ]
}
```

Optionally inspect the selected definition by its returned `id`:

```http
GET {graphBaseUrl}/playbookDefinitions/<playbook-definition-id>?$select=id,uniqueName,displayName,acceptedInputTypes
Authorization: Bearer <access-token>
Accept: application/json
```

### Built-in catalog reference

The following catalog IDs are reference examples. Confirm the ID, availability,
and `acceptedInputTypes` against your tenant's catalog before binding directly;
this table isn't a cross-tenant stability guarantee. Use a returned `id`, never
`uniqueName`, in `playbookDefinition@odata.bind`.

| Playbook | `uniqueName` | Reference catalog `id` | Input `kind` |
| --- | --- | --- | --- |
| Investigate attack | `investigate-incident` | `732b84ae-26ad-4eb4-b4fb-f2f45d7571e6` | `defenderIncidentId` or `defenderAlertId` |
| Extract threat intelligence | `analyze-article` | `4471901f-118e-4254-8822-f141b8f9c5e7` | `defenderThreatIntelligenceId` |
| Plan for posture remediation | `prioritize-posture` | `ce8430cf-8ef6-44e9-8f4f-0148cd696495` | None (`"inputs": []`) |
| Identify attack paths | `run-reconnaissance` | `3f3abf8b-f489-4138-bb83-1f515cfc46f9` | `azureSubscriptionId` |
| Triage alert | `triage-security-copilot` | `96b4186f-b245-4e0d-a411-89087a0c4786` | `defenderAlertId` |
| Protect against a threat | `proactive-protection` | `73d114c7-2d25-45df-8e30-22671219b815` | `defenderThreatIntelligenceId` |
| Detect emerging threats | `detect-emerging-threats` | `cc7723fb-48b8-4224-b9ad-7fc892fd2864` | `defenderThreatIntelligenceId` |

The accepted-type list isn't a complete parameter schema or a requirement to
supply every listed kind. Confirm required inputs and cardinality in the
playbook's current documentation. If the definition or required input kind isn't
available, stop and check tenant setup.

## 2. Start a session

Use the same `{graphBaseUrl}` for the request and absolute
`playbookDefinition@odata.bind`. Replace each definition placeholder with the
corresponding catalog `id` confirmed above. Inputs contain only `kind` and
`value`; don't send service-generated fields or direct-service properties such
as `sourceId`, `sourceType`, or `type`.

**Caution:** Don't automatically retry `POST /sessions` after a timeout. The
session might already exist; an unconditional retry can start duplicate work.
Check visible sessions before deciding whether to submit again.

### Example A: Investigate a Defender incident

Select `investigate-incident` and supply an accessible incident ID:

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions/<investigation-definition-id>",
  "inputs": [
    {
      "kind": "defenderIncidentId",
      "value": "<incident-id>"
    }
  ]
}
```

### Example B: Investigate or triage a Defender alert

Select `investigate-incident` or `triage-security-copilot` with
`defenderAlertId` in its accepted inputs:

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions/<alert-definition-id>",
  "inputs": [
    {
      "kind": "defenderAlertId",
      "value": "<alert-id>"
    }
  ]
}
```

### Example C: Extract threat intelligence

Select `analyze-article` and supply an existing Defender Threat Intelligence
article ID:

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions/<threat-intelligence-definition-id>",
  "inputs": [
    {
      "kind": "defenderThreatIntelligenceId",
      "value": "<article-id>"
    }
  ]
}
```

### Example D: Start zero-input posture remediation planning

Select `prioritize-posture`, confirm it requires no inputs, and send an empty
array rather than inventing an input:

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions/<posture-definition-id>",
  "inputs": []
}
```

### Example E: Map Azure attack paths

Select `run-reconnaissance` and supply an Azure subscription ID you're
authorized to assess:

```http
POST {graphBaseUrl}/sessions
Authorization: Bearer <access-token>
Content-Type: application/json
Accept: application/json

{
  "playbookDefinition@odata.bind": "{graphBaseUrl}/playbookDefinitions/<reconnaissance-definition-id>",
  "inputs": [
    {
      "kind": "azureSubscriptionId",
      "value": "<subscription-id>"
    }
  ]
}
```

### Creation response

Expect `201 Created` with a `Location` header and the created session.
Illustrative excerpt:

```json
{
  "id": "<session-id>",
  "status": "running",
  "statusDetail": "inProgress"
}
```

Save the returned ID and Location. `201` means creation succeeded, not that
agent execution completed; use the actual returned state to monitor progress.

## 3. Track progress

Read the session by ID or use its trusted Graph Location:

```http
GET {graphBaseUrl}/sessions/<session-id>?$select=id,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

Use bounded polling, for example once every 60 seconds for up to one hour, and
wait longer when `Retry-After` requires it. This client-side deadline doesn't
cancel the session. See the published
[status mappings](https://learn.microsoft.com/en-us/graph/api/investigationsession-get?view=graph-rest-beta#session-status-and-status-details).

| Observed state | What to do |
| --- | --- |
| `notStarted` | Wait within the deadline; `completed` detail here is a missing-state fallback, not success. |
| `running` with `waitingForInput` | Stop polling and notify the operator. |
| `running` with `inProgress` or omitted detail | Continue within the deadline. |
| `succeeded` | Inspect available outputs. |
| `failed` | Stop polling and inspect details and runs; this includes canceled sessions. |
| Unknown status or detail | Preserve it and stop without assuming success. |

These examples don't assume an API for supplying follow-up input.
Read available agent runs when you need more context:

```http
GET {graphBaseUrl}/sessions/<session-id>/agentRuns?$select=id,agent,status,statusDetail
Authorization: Bearer <access-token>
Accept: application/json
```

Follow next links; see
[List agentRuns](https://learn.microsoft.com/en-us/graph/api/investigationsession-list-agentruns?view=graph-rest-beta).

## 4. Retrieve reports

Follow [Retrieve session reports](retrieve-session-reports.md) to list and
download summaries and artifacts. Success doesn't guarantee a particular file.

## Cleanup

If the session you created for testing is still active, request cancellation:

```http
POST {graphBaseUrl}/sessions/<session-id>/cancel
Authorization: Bearer <access-token>
Accept: application/json
```

Send no request body. `202 Accepted` means cancellation was requested, not
completed. Poll the session instead of repeatedly canceling it. Stopped sessions
report `status: failed` with `statusDetail: stopped`; see
[Cancel session](https://learn.microsoft.com/en-us/graph/api/investigationsession-cancel?view=graph-rest-beta).

Cancel only sessions you created for testing. Cancellation preserves history
and doesn't undo completed agent actions or charges already incurred. Delete
downloaded files and clear bearer tokens when finished.
