# BlockShield

Publisher: CrossRealms <br>
Connector Version: 1.0.1 <br>
Product Vendor: CrossRealms <br>
Product Name: BlockShield <br>
Minimum Product Version: 8.7.0.232

Retrieve threat intelligence about IP addresses and submit domains, IPs and URLs to the BlockShield blocklist

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

### Configuration variables

This table lists the configuration variables required to operate BlockShield. These variables are specified when configuring a BlockShield asset in Splunk SOAR.

VARIABLE | REQUIRED | TYPE | DESCRIPTION
-------- | -------- | ---- | -----------
**base_url** | required | string | Base URL of the BlockShield API (e.g. https://api.blockshield.example.com) |
**username** | required | string | Username for authentication |
**password** | required | password | Password for authentication |
**verify_ssl** | optional | boolean | Verify SSL certificates |
**timeout** | optional | numeric | Request timeout in seconds |

### Supported Actions

[test connectivity](#action-test-connectivity) - Validate the asset configuration for connectivity using supplied configuration <br>
[get ip info](#action-get-ip-info) - Retrieve threat intelligence information about an IP address <br>
[add bulk domains](#action-add-bulk-domains) - Submit a list of domains to the BlockShield blocklist <br>
[add bulk ips](#action-add-bulk-ips) - Submit a list of IP addresses to the BlockShield blocklist <br>
[add bulk urls](#action-add-bulk-urls) - Submit a list of URLs to the BlockShield blocklist

## action: 'test connectivity'

Validate the asset configuration for connectivity using supplied configuration

Type: **test** <br>
Read only: **True**

#### Action Parameters

No parameters are required for this action

#### Action Output

No Output

## action: 'get ip info'

Retrieve threat intelligence information about an IP address

Type: **investigate** <br>
Read only: **True**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ip** | required | IP address to look up | string | `ip` |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.ip | string | `ip` | 8.8.8.8 |
action_result.status | string | | success failed |
action_result.message | string | | Successfully retrieved info for IP 8.8.8.8 |
action_result.summary.ip | string | `ip` | 8.8.8.8 |
action_result.data.\*.isblocked | boolean | | True False |
action_result.data.\*.abuseipdb.info | string | | {"abuseConfidenceScore": 0, "countryCode": "US", "isp": "Google LLC", ...} |
action_result.data.\*.virustotal | string | | {"data": {"attributes": {"last_analysis_stats": {...}, "reputation": 543, ...}}} |
action_result.data.\*.bgpview | string | | {"status": "ok", "data": {"prefixes": [...], "rir_allocation": {...}, "ptr_record": "dns.google", ...}} |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'add bulk domains'

Submit a list of domains to the BlockShield blocklist

Type: **contain** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**domains** | required | Comma-separated list of domains to submit | string | `domain` |
**source** | required | Source of the domains (e.g. ThreatFeed, SOC) | string | |
**description** | optional | Optional description | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.domains | string | `domain` | example.com,example.org |
action_result.parameter.source | string | | ThreatFeed |
action_result.parameter.description | string | | Malicious domains reported by the SOC |
action_result.status | string | | success failed |
action_result.message | string | | Successfully added 5 domains |
action_result.summary.domains_added | numeric | | 5 |
action_result.data.\*.links | numeric | | 100 |
action_result.data.\*.domains | numeric | | 30 |
action_result.data.\*.duration | numeric | | 0.41873 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'add bulk ips'

Submit a list of IP addresses to the BlockShield blocklist

Type: **contain** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**ips** | required | Comma-separated list of IP addresses to submit | string | `ip` |
**source** | required | Source of the IP addresses (e.g. ThreatFeed, SOC) | string | |
**subnet** | optional | Subnet mask | numeric | |
**reported_by** | optional | Name of the person or system reporting | string | |
**description** | optional | Optional description | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.ips | string | `ip` | 192.0.2.10,198.51.100.20 |
action_result.parameter.source | string | | ThreatFeed |
action_result.parameter.subnet | numeric | | 32 |
action_result.parameter.reported_by | string | | SOC Analyst |
action_result.parameter.description | string | | Malicious IP addresses reported by the SOC |
action_result.status | string | | success failed |
action_result.message | string | | Successfully added 5 IPs |
action_result.summary.ips_added | numeric | | 5 |
action_result.data.\*.links | numeric | | 100 |
action_result.data.\*.ips | numeric | | 30 |
action_result.data.\*.duration | numeric | | 0.42 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

## action: 'add bulk urls'

Submit a list of URLs to the BlockShield blocklist

Type: **contain** <br>
Read only: **False**

#### Action Parameters

PARAMETER | REQUIRED | DESCRIPTION | TYPE | CONTAINS
--------- | -------- | ----------- | ---- | --------
**urls** | required | Comma-separated list of URLs to submit | string | `url` |
**source** | required | Source of the URLs (e.g. ThreatFeed, SOC) | string | |
**description** | optional | Optional description | string | |

#### Action Output

DATA PATH | TYPE | CONTAINS | EXAMPLE VALUES
--------- | ---- | -------- | --------------
action_result.parameter.urls | string | `url` | https://example.com/malware,https://example.org/phish |
action_result.parameter.source | string | | ThreatFeed |
action_result.parameter.description | string | | Malicious URLs reported by the SOC |
action_result.status | string | | success failed |
action_result.message | string | | Successfully added 5 URLs |
action_result.summary.urls_added | numeric | | 5 |
action_result.data.\*.links | numeric | | 100 |
action_result.data.\*.urls | numeric | | 30 |
action_result.data.\*.duration | numeric | | 0.41873 |
summary.total_objects | numeric | | 1 |
summary.total_objects_successful | numeric | | 1 |

______________________________________________________________________

Auto-generated Splunk SOAR Connector documentation.

Copyright 2026 Splunk Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and limitations under the License.
