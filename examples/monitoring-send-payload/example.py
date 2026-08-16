"""
Demonstrates sending the pandoraPlugintools monitoring payload to the
Pandora FMS console API v2 '/monitoring' endpoint using the third-party
'requests' library.

'requests' is NOT a dependency of pandoraPlugintools -- it must be
installed separately (`pip install requests`) and is only used here, in
the caller's own script, never inside the library package itself.

This script is safe to run without a real server: unless the
PANDORA_MONITORING_URL environment variable is set, it only prints the
method, URL, headers and body that WOULD be sent.
"""

import json
import os

import pandoraPlugintools as ppt

ppt.set_monitoring_items([])

agent_data = {
    "agent_name": "nginx-01",
    "os": "Linux",
    "interval": 300,
}
module_data = [
    {"name": "nginx_status", "type": "generic_proc", "data": 1},
    {"name": "active_connections", "type": "generic_data", "data": 42},
]

ppt.add_monitoring_item(agent_data, module_data)

payload = ppt.print_monitoring_payload()

url = os.environ.get(
    "PANDORA_MONITORING_URL", "https://<console_host>/pandora_console/api/v2/monitoring"
)
api_token = os.environ.get("PANDORA_API_TOKEN", "<api_token>")
headers = {
    "Authorization": "Bearer " + api_token,
    "Content-Type": "application/json",
}

if __name__ == "__main__" and os.environ.get("PANDORA_MONITORING_URL"):
    # requests is a third-party library, not a pandoraPlugintools dependency.
    # Install it separately with: pip install requests
    try:
        import requests
    except ImportError:
        print("requests is not installed; run 'pip install requests' to send the payload.")
    else:
        response = requests.post(url, headers=headers, data=payload)
        print(response.status_code, response.text)
else:
    print("Dry run (set PANDORA_MONITORING_URL to actually send this payload):")
    print("POST", url)
    print("Headers:", headers)
    print("Body:", json.dumps(json.loads(payload), indent=2))
