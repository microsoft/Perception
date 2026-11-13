# Retrieve session reports and other outputs

Discover outputs for an existing session, then retrieve their authenticated
content. Complete the [common setup](README.md#setup-and-notation) and obtain a
session ID from [session discovery](filter-sessions.md) or
[playbook creation](start-playbook.md). These requests are read-only.

## 1. List session outputs

```http
GET {graphBaseUrl}/sessions('<session-id>')/outputs?$select=id,kind
Authorization: Bearer <access-token>
Accept: application/json
```

Illustrative response excerpt:

```json
{
  "value": [
    {
      "id": "<summary-output-id>",
      "kind": "summary"
    },
    {
      "id": "<artifact-output-id>",
      "kind": "artifact"
    }
  ]
}
```

Follow any `@odata.nextLink` before assuming all outputs have been discovered.
Choose an ID from the selected session's response; do not construct one from a
filename or use an ID belonging to another session.

The `summary` kind identifies a natural-language summary. The `artifact` kind
can include reports and other produced files; not every artifact is necessarily
a report. These categories are not file formats. Preserve unknown future kinds.
Select by `kind` in the client rather than assuming output `$filter` support.

Reports are session outputs, not a separate `/reports` resource or an agent-run
output collection.

## 2. Read one output's metadata

```http
GET {graphBaseUrl}/sessions('<session-id>')/outputs('<output-id>')?$select=id,kind
Authorization: Bearer <access-token>
Accept: application/json
```

Illustrative response excerpt:

```json
{
  "id": "<output-id>",
  "kind": "artifact"
}
```

Expect `200 OK` and the selected output identity. Do not assume direct-service
properties such as `path`, `downloadUrl`, or `type` are exposed by Graph; this
recipe uses Graph's `kind` and authenticated content navigation.

## 3. Download the content

```http
GET {graphBaseUrl}/sessions('<session-id>')/outputs('<output-id>')/content
Authorization: Bearer <access-token>
Accept: */*
```

On success, the response body contains the stored bytes, not a JSON object with
a `content` property. Use the response's media type and any supplied download
metadata when saving or reading the file; do not assume every output is JSON,
Markdown, HTML, or PDF. An error response can still be a Graph JSON error.

The content operation requires authentication just like the metadata read.
An output ID is not a public download credential.

## Empty results and output readiness

`200 OK` with `"value": []` means no outputs are currently available to this
request. Even `status: succeeded` does not guarantee that a particular report has
been produced or is ready.

If waiting for output, use bounded polling, for example once every 30 seconds for
up to five minutes, and honor `Retry-After`. Stop when the desired output appears
or the deadline expires. Report "no output available within the wait window"
rather than claiming the playbook failed. For an inaccessible or missing output,
inspect the Graph error instead of saving it as a report.

## Verify and clean up

Verify the metadata ID matches the selected output and the content request
succeeded. Inspect the downloaded file using a tool appropriate to its media
type. These reads do not create or cancel sessions.

Delete downloaded tenant data when no longer needed and clear the token from
your HTTP client. See [common error handling](README.md#errors-costs-and-cleanup).
