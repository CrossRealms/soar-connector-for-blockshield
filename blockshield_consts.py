# File: blockshield_consts.py
#
# Copyright (c) 2025-2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software distributed under
# the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific language governing permissions
# and limitations under the License.

# Defaults
BLOCKSHIELD_DEFAULT_TIMEOUT = 30
BLOCKSHIELD_DEFAULT_SUBNET = 32

# API endpoints
BLOCKSHIELD_CONNECTIVITY_ENDPOINT = "/v1/health"
BLOCKSHIELD_IPINFO_ENDPOINT = "/v1/ipinfo"
BLOCKSHIELD_BULK_DOMAINS_ENDPOINT = "/v1/bulk_domains"
BLOCKSHIELD_BULK_IPS_ENDPOINT = "/v1/bulk_ips"
BLOCKSHIELD_BULK_URLS_ENDPOINT = "/v1/bulk_urls"

# Progress messages
BLOCKSHIELD_PROG_CONNECTING = "Testing connectivity to BlockShield service"

# Success messages
BLOCKSHIELD_SUCC_CONNECTIVITY_TEST = "Test Connectivity Passed"
BLOCKSHIELD_SUCC_IPINFO = "Successfully retrieved info for IP {ip}"
BLOCKSHIELD_SUCC_BULK_SUBMIT = "Successfully added {count} {indicator}"

# Error messages
BLOCKSHIELD_ERR_CONNECTIVITY_TEST = "Test Connectivity Failed"
BLOCKSHIELD_ERR_MISSING_CONFIG = "Missing required configuration parameters: 'base_url', 'username' or 'password'"
BLOCKSHIELD_ERR_INVALID_TIMEOUT = "Please provide a positive integer value for the 'timeout' configuration parameter"
BLOCKSHIELD_ERR_MISSING_PARAM = "Missing required parameter: '{param}'"
BLOCKSHIELD_ERR_MISSING_PARAMS = "Missing required parameters: '{list_param}' or 'source'"
BLOCKSHIELD_ERR_UNKNOWN_ACTION = "Unknown action: {action}"
BLOCKSHIELD_ERR_SERVER = "Error from server. Status Code: {code}"
BLOCKSHIELD_ERR_SERVER_DETAILS = "Error from server. Status Code: {code}. Error: {error}"
BLOCKSHIELD_ERR_REST_CALL = "Error making REST call: {error}"
