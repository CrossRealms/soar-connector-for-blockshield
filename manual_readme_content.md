## Configuration and Asset Setup

### Prerequisites

- A BlockShield account that is allowed to call the BlockShield API. The 'add bulk' actions
  write to the blocklist, so the account needs write access if you plan to use them.
- Network access from the Splunk SOAR instance (or the automation broker that runs the app) to
  the BlockShield API. See [Port Information](#port-information).

### Authentication

The app authenticates to the BlockShield API with HTTP Basic authentication, using the
**username** and **password** from the asset configuration on every request. The password is a
password field, so Splunk SOAR stores it encrypted and does not write it to action results.

### Create the Asset

1. In Splunk SOAR, open **Apps**, search for **BlockShield** and click **Configure New Asset**.
1. On the **Asset Info** tab, enter an **Asset name**, for example `blockshield`. Playbooks
   refer to the asset by this name, so pick a short, stable one.
1. On the **Asset Settings** tab, fill in the configuration parameters:

| PARAMETER | REQUIRED | DEFAULT | NOTES |
|-----------|----------|---------|-------|
| **base_url** | Yes | | Root of the BlockShield API including the scheme, for example `https://api.blockshield.example.com`. The app appends the `/v1/...` endpoint paths, so do not include them. A trailing `/` is ignored. |
| **username** | Yes | | BlockShield API user. |
| **password** | Yes | | Password for that user. |
| **verify_ssl** | No | Enabled | Keep enabled in production. Disable it only for a test instance with a self-signed certificate. |
| **timeout** | No | 30 | Maximum number of seconds each HTTP request may take. Must be a positive integer. |

4. Optional: on the **Approval Settings** tab, require approval before actions run. The 'add bulk'
   actions change the blocklist, so approval is a useful safeguard while you roll out new playbooks.
1. Optional: on the **Access Control** tab, limit which users and roles can run actions on the asset.
1. Click **Save**, then **Test Connectivity**. The app calls `GET /v1/health` and reports
   `Test Connectivity Passed` when the API answers with a 2xx status.

### Troubleshooting

| MESSAGE | CAUSE |
|---------|-------|
| `Missing required configuration parameters: 'base_url', 'username' or 'password'` | One of the required asset parameters is empty. |
| `Please provide a positive integer value for the 'timeout' configuration parameter` | **timeout** is zero, negative or not a number. |
| `Error from server. Status Code: 401...` | The BlockShield API rejected the **username** and **password**. |
| `Error from server. Status Code: 404...` | **base_url** is wrong, often because it already ends in an API path. |
| `Error making REST call: ...` | The request never got a response: DNS, proxy, firewall, TLS verification or timeout. The text after the colon gives the underlying error. |

## Actions

| ACTION | TYPE | WHAT IT DOES |
|--------|------|--------------|
| **test connectivity** | test | Checks the asset configuration against `GET /v1/health`. |
| **get ip info** | investigate | Looks up one IP address with `GET /v1/ipinfo/<ip>` and returns the BlockShield response as the action data. |
| **add bulk domains** | contain | Submits domains to the blocklist with `POST /v1/bulk_domains`. |
| **add bulk ips** | contain | Submits IP addresses to the blocklist with `POST /v1/bulk_ips`. |
| **add bulk urls** | contain | Submits URLs to the blocklist with `POST /v1/bulk_urls`. |

The three 'add bulk' actions share the same behavior:

- **domains**, **ips** and **urls** accept a single value or a comma-separated list, for example
  `198.51.100.7, 203.0.113.9`. The app trims whitespace and drops empty entries, so a trailing comma
  or line breaks between values are harmless.
- **source** is required and is sent to BlockShield as the origin of the indicators, for example
  `ThreatFeed` or `SOC`. **description** is optional.
- **add bulk ips** also accepts **subnet** (default `32`, a single host) and **reported_by**.
- The whole list is sent in one request, so the action either succeeds or fails as a whole. The
  summary reports how many indicators were submitted (`domains_added`, `ips_added` or `urls_added`).

## Using BlockShield in Playbooks

The app works with every way Splunk SOAR runs actions: visual playbooks, Python playbooks, and
manual runs. The examples below assume an asset named `blockshield`.

### Useful Data Paths

Action inputs usually come from artifact CEF fields, and later blocks read the action outputs.

| PURPOSE | DATA PATH |
|---------|-----------|
| IP address input | `artifact:*.cef.sourceAddress`, `artifact:*.cef.destinationAddress` |
| Domain input | `artifact:*.cef.destinationDnsDomain` |
| URL input | `artifact:*.cef.requestURL` |
| Did the action succeed? | `<block_name>:action_result.status` (`success` or `failed`) |
| Status or error text | `<block_name>:action_result.message` |
| BlockShield response | `<block_name>:action_result.data.*` |
| Number of indicators submitted | `<block_name>:action_result.summary.ips_added` (or `domains_added`, `urls_added`) |
| IP that was looked up | `<block_name>:action_result.parameter.ip` |

The parameters declare the `ip`, `domain` and `url` contains types, so the Visual Playbook Editor
suggests matching CEF fields when you pick a data path for them.

### Visual Playbook Editor

**Enrich an IP address**

1. Create or open a playbook and add an **Action** block.
1. Select the **get ip info** action and the `blockshield` asset.
1. Set **ip** to a data path such as `artifact:*.cef.sourceAddress`. The block runs the action once
   for each value the data path returns.
1. Connect a **Decision** block. Test `get_ip_info_1:action_result.status == success`, or compare a
   field of the BlockShield response, `get_ip_info_1:action_result.data.*.<field>`, against the
   threshold you want. Run the action once and open its results to see which fields BlockShield
   returns.

A common pattern chains the two kinds of action:

1. **get ip info** on `artifact:*.cef.sourceAddress`.
1. A **Filter** block that keeps the results where BlockShield reports the IP address as malicious.
1. Optionally, a **Prompt** block that asks an analyst to confirm.
1. **add bulk ips** with the IP addresses that passed. Use the filter block's data path, for
   example `filtered-data:filter_1:condition_1:get_ip_info_1:action_result.parameter.ip`, so only
   those IP addresses are submitted. To send them in one request, join them with a **Format**
   block first, as shown above.


### Running Actions Outside a Playbook

- **Investigation page:** open a container, click **Action**, choose a BlockShield action and asset,
  and enter the parameters.
- **Contextual actions:** in an artifact, open the menu next to an IP address, domain or URL value.
  Matching BlockShield actions are offered with that value pre-filled, based on the parameter
  contains types.
- **Automation:** playbooks that use the app can run automatically when containers arrive, for
  example from a SIEM or an email ingestion asset, or on a schedule through a timer asset.

## Port Information

The app uses HTTP/HTTPS to communicate with the BlockShield API. Below are the default ports used
by Splunk SOAR. If the **base_url** specifies a different port, that port must be open instead.

| SERVICE NAME | TRANSPORT PROTOCOL | PORT |
|--------------|--------------------|------|
| http | tcp | 80 |
| https | tcp | 443 |
