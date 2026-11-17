**Unreleased**
* Added the BlockShield connector actions implementation
* Added the 'get ip info' action to retrieve threat intelligence about an IP address
* Added the 'add bulk domains', 'add bulk ips' and 'add bulk urls' actions to submit indicators to the BlockShield blocklist
* Added HTTP Basic authentication with a configurable base URL, SSL verification and request timeout
* Modified the 'test connectivity' action, which now logs in with POST /v1/login to confirm that the API is reachable and the configured credentials are valid
* Added validation that rejects a non-positive or non-numeric 'timeout' asset parameter
* Updated the docs to clarify the least privileged BlockShield role required for each action
* Replaced the template logos with the BlockShield logo
