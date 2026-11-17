# Authentication

## Microsoft Graph: delegated access

The [Graph Insomnia sample](../API/Insomnia-collection/README.md) and
[Perception API examples](../API/HTTP/Examples/README.md) call
`https://graph.microsoft.com/beta/security/agenticSecurity`.
They demonstrate delegated access with a work or school account, not a
client-credentials or unattended sign-in flow. Personal Microsoft accounts
aren't supported.

| What you will do | Microsoft Graph delegated permission |
| --- | --- |
| Read the catalog, sessions, inputs, runs, and output content | `Perception.Read.All` |
| Create or cancel sessions, and read their resources | `Perception.Manage.All` |

Request only the permission your task needs. `Perception.Manage.All` also permits
reads; the create/cancel walkthrough doesn't require both permissions.

### Administrator consent

Before requesting a token with these permissions, ensure an authorized Microsoft
Entra administrator has granted **admin consent** for the required delegated
permission to the client application in the intended tenant. This is the
application used to obtain the token, such as Graph Explorer or your registered
application. Consent for one application doesn't cover another.

If that consent is already in place, it doesn't need to be granted again merely
because an access token expires. Follow your organization's approval process and
the [Microsoft Entra admin-consent guidance](https://learn.microsoft.com/entra/identity/enterprise-apps/grant-admin-consent)
when a new or changed grant is needed.

The signed-in user must separately have access to the Perception resources.
Admin consent authorizes the application; it doesn't assign workload roles or
override the service's access controls.

### Obtain a token for manual testing

Use your organization's approved delegated Microsoft Graph sign-in flow.
[Graph Explorer](https://developer.microsoft.com/graph/graph-explorer) is one
option for interactive testing:

1. Sign in with the intended work or school account and confirm the tenant.
2. Select **GET** and enter
   `https://graph.microsoft.com/beta/security/agenticSecurity/playbookDefinitions`.
3. Use **Modify permissions** to request the delegated permission above.
   If admin consent isn't already in place, have an authorized administrator
   complete the [consent process](#administrator-consent) before proceeding.
4. Copy the token from the **Access token** tab into your API client's private
   local environment. Copy only the token, without the `Bearer ` prefix.

If Graph Explorer doesn't offer the required permission or tenant consent is
unavailable, stop and work with your administrator. An approved application can
instead use the documented
[delegated authorization flow](https://learn.microsoft.com/graph/auth-v2-user)
after [application registration](https://learn.microsoft.com/graph/auth-register-app-v2).
Don't substitute another API's token or bypass a consent/access denial.

Tokens expire. Obtain a fresh token through the same approved flow when necessary;
these samples do not acquire or refresh tokens.

### Keep credentials and tenant data private

- Never put tokens, client secrets, or real tenant data in repository files,
  issues, screenshots, command-line arguments, or chat messages.
- Keep credentials in the client's private local environment. A masked
  "confidential" value is not necessarily encrypted or excluded from exports.
- Use local storage for requests and response history. Inspect exports before
  sharing, and clear sensitive local history when finished.
- Send a Graph token only to the intended Microsoft Graph HTTPS endpoint.
  Graph authentication is distinct from direct Perception API authentication;
  changing the hostname doesn't make their tokens or request contracts equivalent.

These samples intentionally cover delegated access only. Consult the current
[overview](https://learn.microsoft.com/graph/api/resources/agenticsecurity-apioverview?view=graph-rest-beta)
and the individual method's permission table for other authentication scenarios;
this guide does not validate app-only compatibility.

## Contribution-specific setup

Keep common endpoint and authentication instructions in shared docs. Each contribution should state only:

- Which API/authentication approach it uses, linking to the shared guide.
- Its required permissions and additional prerequisites.
- Any contribution-specific credential setup or cleanup.

Do not store access tokens or client secrets in source control. Use the identity
mechanism documented for the specific contribution, requesting only required access.

## Graph request examples

Complete the [delegated setup above](#microsoft-graph-delegated-access) before
using the [Perception API examples](../API/HTTP/Examples/README.md). Reads require
`Perception.Read.All`; creating or canceling sessions requires
`Perception.Manage.All`, which also permits reads. Confirm the API and selected
playbook are enabled in your tenant.

The optional `GET /v1.0/me` lookup in
[Filter sessions](../API/HTTP/Examples/filter-sessions.md) additionally requires delegated
`User.Read`. Skip it if you already know your user object ID.

For the API walkthrough and permission requirements, see
[Use Perception in Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/resources/agenticsecurity-apioverview?view=graph-rest-beta#authentication-and-permissions).
Use a Microsoft Graph token; direct Perception service tokens and scopes aren't
interchangeable. Do not grant extra permissions to work around an endpoint that
isn't enabled.
