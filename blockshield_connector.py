# File: blockshield_connector.py
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

import phantom.app as phantom
import requests
from phantom.action_result import ActionResult
from phantom.base_connector import BaseConnector

from blockshield_consts import (
    BLOCKSHIELD_BULK_DOMAINS_ENDPOINT,
    BLOCKSHIELD_BULK_IPS_ENDPOINT,
    BLOCKSHIELD_BULK_URLS_ENDPOINT,
    BLOCKSHIELD_CONNECTIVITY_ENDPOINT,
    BLOCKSHIELD_DEFAULT_SUBNET,
    BLOCKSHIELD_DEFAULT_TIMEOUT,
    BLOCKSHIELD_ERR_CONNECTIVITY_TEST,
    BLOCKSHIELD_ERR_INVALID_TIMEOUT,
    BLOCKSHIELD_ERR_MISSING_CONFIG,
    BLOCKSHIELD_ERR_MISSING_PARAM,
    BLOCKSHIELD_ERR_MISSING_PARAMS,
    BLOCKSHIELD_ERR_REST_CALL,
    BLOCKSHIELD_ERR_SERVER,
    BLOCKSHIELD_ERR_SERVER_DETAILS,
    BLOCKSHIELD_ERR_UNKNOWN_ACTION,
    BLOCKSHIELD_IPINFO_ENDPOINT,
    BLOCKSHIELD_PROG_CONNECTING,
    BLOCKSHIELD_SUCC_BULK_SUBMIT,
    BLOCKSHIELD_SUCC_CONNECTIVITY_TEST,
    BLOCKSHIELD_SUCC_IPINFO,
)


class BlockShieldConnector(BaseConnector):
    """
    Connector for the BlockShield threat intelligence and blocklist service.
    """

    def __init__(self):
        super().__init__()
        self._session = None
        self._base_url = None
        self._timeout = BLOCKSHIELD_DEFAULT_TIMEOUT

    @staticmethod
    def _parse_list_param(value):
        """
        Split a comma-separated action parameter into a list of non-empty, stripped values.
        """
        return [item.strip() for item in (value or "").split(",") if item.strip()]

    def _make_rest_call(self, endpoint, action_result, method="get", params=None, data=None):
        """
        Helper function to make REST calls to the BlockShield API.
        """
        url = f"{self._base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        self.debug_print(f"Making REST call to: {url}")

        try:
            response = self._session.request(method=method, url=url, params=params, json=data, timeout=self._timeout)

            # Add debug data
            if hasattr(action_result, "add_debug_data"):
                action_result.add_debug_data({"r_status_code": response.status_code})
                action_result.add_debug_data({"r_text": response.text})

            # Process response
            if 200 <= response.status_code < 300:
                if response.text:
                    try:
                        return phantom.APP_SUCCESS, response.json()
                    except ValueError:
                        return phantom.APP_SUCCESS, response.text
                return phantom.APP_SUCCESS, {}

            # Error handling
            error_message = BLOCKSHIELD_ERR_SERVER.format(code=response.status_code)
            if response.text:
                try:
                    resp_json = response.json()
                    error = resp_json.get("error", "Unknown error") if isinstance(resp_json, dict) else resp_json
                except ValueError:
                    error = response.text
                error_message = BLOCKSHIELD_ERR_SERVER_DETAILS.format(code=response.status_code, error=error)

            return action_result.set_status(phantom.APP_ERROR, error_message), None

        except Exception as e:
            return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_REST_CALL.format(error=e)), None

    def _handle_test_connectivity(self, param):
        """
        Validate the asset configuration for connectivity using supplied credentials.
        """
        action_result = self.add_action_result(ActionResult(dict(param)))
        self.save_progress(BLOCKSHIELD_PROG_CONNECTING)

        ret_val, _ = self._make_rest_call(BLOCKSHIELD_CONNECTIVITY_ENDPOINT, action_result)

        if phantom.is_fail(ret_val):
            self.save_progress(BLOCKSHIELD_ERR_CONNECTIVITY_TEST)
            return action_result.get_status()

        self.save_progress(BLOCKSHIELD_SUCC_CONNECTIVITY_TEST)
        return action_result.set_status(phantom.APP_SUCCESS)

    def _handle_ipinfo(self, param):
        """
        Retrieve threat intelligence information about an IP address.
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        ip = param.get("ip")
        if not ip:
            return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_MISSING_PARAM.format(param="ip"))

        ret_val, response = self._make_rest_call(f"{BLOCKSHIELD_IPINFO_ENDPOINT}/{ip}", action_result)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)
        action_result.update_summary({"ip": ip})

        return action_result.set_status(phantom.APP_SUCCESS, BLOCKSHIELD_SUCC_IPINFO.format(ip=ip))

    def _handle_bulk_domains(self, param):
        """
        Submit a list of domains to the BlockShield blocklist.
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        domains = self._parse_list_param(param.get("domains"))
        source = param.get("source")
        description = param.get("description")

        if not domains or not source:
            return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_MISSING_PARAMS.format(list_param="domains"))

        data = {"domains": domains, "source": source, "description": description}

        ret_val, response = self._make_rest_call(BLOCKSHIELD_BULK_DOMAINS_ENDPOINT, action_result, method="post", data=data)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)
        action_result.update_summary({"domains_added": len(domains)})

        return action_result.set_status(phantom.APP_SUCCESS, BLOCKSHIELD_SUCC_BULK_SUBMIT.format(count=len(domains), indicator="domains"))

    def _handle_bulk_ips(self, param):
        """
        Submit a list of IP addresses to the BlockShield blocklist.
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        ips = self._parse_list_param(param.get("ips"))
        source = param.get("source")
        subnet = param.get("subnet", BLOCKSHIELD_DEFAULT_SUBNET)
        reported_by = param.get("reported_by", "")
        description = param.get("description")

        if not ips or not source:
            return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_MISSING_PARAMS.format(list_param="ips"))

        data = {"ips": ips, "source": source, "subnet": subnet, "reported_by": reported_by, "description": description}

        ret_val, response = self._make_rest_call(BLOCKSHIELD_BULK_IPS_ENDPOINT, action_result, method="post", data=data)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)
        action_result.update_summary({"ips_added": len(ips)})

        return action_result.set_status(phantom.APP_SUCCESS, BLOCKSHIELD_SUCC_BULK_SUBMIT.format(count=len(ips), indicator="IPs"))

    def _handle_bulk_urls(self, param):
        """
        Submit a list of URLs to the BlockShield blocklist.
        """
        action_result = self.add_action_result(ActionResult(dict(param)))

        urls = self._parse_list_param(param.get("urls"))
        source = param.get("source")
        description = param.get("description")

        if not urls or not source:
            return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_MISSING_PARAMS.format(list_param="urls"))

        data = {"urls": urls, "source": source, "description": description}

        ret_val, response = self._make_rest_call(BLOCKSHIELD_BULK_URLS_ENDPOINT, action_result, method="post", data=data)

        if phantom.is_fail(ret_val):
            return action_result.get_status()

        action_result.add_data(response)
        action_result.update_summary({"urls_added": len(urls)})

        return action_result.set_status(phantom.APP_SUCCESS, BLOCKSHIELD_SUCC_BULK_SUBMIT.format(count=len(urls), indicator="URLs"))

    def initialize(self):
        """
        Initialize the connector.
        """
        self.debug_print("Initializing connector")
        config = self.get_config()

        # Get configuration parameters
        self._base_url = config.get("base_url")
        username = config.get("username")
        password = config.get("password")

        if not self._base_url or not username or not password:
            return self.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_MISSING_CONFIG)

        try:
            self._timeout = int(config.get("timeout", BLOCKSHIELD_DEFAULT_TIMEOUT))
        except (TypeError, ValueError):
            return self.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_INVALID_TIMEOUT)
        if self._timeout <= 0:
            return self.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_INVALID_TIMEOUT)

        self._session = requests.Session()
        self._session.auth = (username, password)
        self._session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})
        self._session.verify = config.get("verify_ssl", True)

        return phantom.APP_SUCCESS

    def finalize(self):
        """
        Release the HTTP session once the action has completed.
        """
        if self._session:
            self._session.close()
        return phantom.APP_SUCCESS

    def handle_action(self, param):
        """
        Dispatcher for actions.
        """
        self.debug_print("action_id ", self.get_action_identifier())

        action_mapping = {
            "test_connectivity": self._handle_test_connectivity,
            "ipinfo": self._handle_ipinfo,
            "bulk_domains": self._handle_bulk_domains,
            "bulk_ips": self._handle_bulk_ips,
            "bulk_urls": self._handle_bulk_urls,
        }

        action = self.get_action_identifier()

        if action in action_mapping:
            return action_mapping[action](param)

        action_result = self.add_action_result(ActionResult(dict(param)))
        return action_result.set_status(phantom.APP_ERROR, BLOCKSHIELD_ERR_UNKNOWN_ACTION.format(action=action))


if __name__ == "__main__":
    import sys

    connector = BlockShieldConnector()
    connector.print_progress_message = True

    sys.exit(0)
