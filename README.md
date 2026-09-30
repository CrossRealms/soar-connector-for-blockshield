# BlockShield

Publisher: CrossRealms <br>
Connector Version: 1.0.1 <br>
Product Vendor: CrossRealms <br>
Product Name: BlockShield <br>
Minimum Product Version: 8.7.0.232

Retrieve threat intelligence about IP addresses and submit domains, IPs and URLs to the BlockShield blocklist

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
action_result.data.\* | string | | |
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
action_result.data.\* | string | | |
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
action_result.data.\* | string | | |
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
action_result.data.\* | string | | |
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
