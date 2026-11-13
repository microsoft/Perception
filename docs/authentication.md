# Authentication

Detailed customer sign-in instructions must be checked against the public API
documentation before the first runnable contribution is published.

Keep common endpoint and authentication instructions in shared docs. Each contribution should state only:

- Which API/authentication approach it uses, linking to the shared guide.
- Its required permissions and additional prerequisites.
- Any contribution-specific credential setup or cleanup.

Do not store access tokens or client secrets in source control. Use the identity
mechanism documented for the specific contribution, requesting only required access.

## Graph request examples

The [HTTP examples](examples/README.md) use Microsoft Graph, not the direct
Perception service. Before running them:

1. Confirm that your tenant has access to the agentic security API and obtain
   the supported Graph host and version from its current API documentation.
2. Use an HTTP client with Microsoft Entra sign-in for that tenant and obtain
   a token whose audience is Microsoft Graph. A direct Perception service
   token is not interchangeable with a Graph token.
3. Request the documented Graph permissions for the operation and obtain
   administrator consent where required. Reads require session/catalog read
   access; starting and canceling sessions require the corresponding operating
   access. Also confirm your user has access to the selected tenant resources.
4. Configure the token as a bearer token in the HTTP client. Do not save it in
   example files, URLs, screenshots, or source control.

These examples do not establish the final Perception-specific Graph permission
names or application-only support. Check those against the current API
documentation for your enabled deployment rather than substituting direct API
scope names. The optional standard Graph `/me` request uses delegated `User.Read`;
it can be skipped if you already know your user object ID.

For general background, see [Microsoft Graph authentication and authorization](https://learn.microsoft.com/en-us/graph/auth/)
and [Graph Explorer](https://learn.microsoft.com/en-us/graph/graph-explorer/graph-explorer-overview).
Do not grant extra permissions to work around an endpoint that is not enabled.
