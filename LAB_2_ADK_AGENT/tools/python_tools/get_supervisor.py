import http.client
import json
from ibm_watsonx_orchestrate.agent_builder.tools import tool


@tool
def get_supervisor(employee_id: str) -> str:
    """Get supervisor details for a given employee.

    This function retrieves an access token from the API, then queries
    the CROSS interface to return supervisor information in JSON format.

    Args:
        employee_id: The unique employee ID to search for.

    Returns:
        A JSON string containing supervisor details of the specified employee.
    """
    conn = http.client.HTTPSConnection("cross-qa.myworkplaze.com")
    payload = json.dumps({
    "client_id": "cross_qa_ibm",
    "client_secret": "wW0JFH3HE9ewpGBR"
    })
    headers = {
    'Content-Type': 'application/json',
    'Cookie': '_cfuvid=RG4zQUudVOaP2gFmHB0WdnwxGu4zFbkXvgxZFW.Qy34-1741071420178-0.0.1.1-604800000; _cfuvid=NgWA6lllQ_plzDse9YuCGo0JXx1GTE1McSCDcuB2E9Q-1755486640552-0.0.1.1-604800000; _cfuvid=8APkjIE6NYiKmjQ.WkToUI4bZbkc3QP1PXEX.no0S4Y-1755654910894-0.0.1.1-604800000; _cfuvid=77Oc77LheB95zOlD5ZHgVVuemMpvR8gA.ixQ4K5JJAU-1761820312.7244112-1.0.1.1-BJDuisa5bgOdQufszn0ifj.Gve8TiXTsJCHnHFt_oS0'
    }
    conn.request("POST", "/v1/api/cross/token", payload, headers)
    res = conn.getresponse()
    data = res.read()
    token_json_str = data.decode("utf-8")
    token_json = json.loads(token_json_str)
    token = token_json['jwt_token']
    print(token)

    # conn = http.client.HTTPSConnection("cross-qa.myworkplaze.com")
    payload = json.dumps({
    "cross_id": "CROSS-DEMO-APIEX8WM0034",
    "parameter": [
        {
        "column": "SearchValue1",
        "value": f"{employee_id}"
        }
    ]
    })
    headers = {
    'Content-Type': 'application/json',
    'Cookie': '_cfuvid=NgWA6lllQ_plzDse9YuCGo0JXx1GTE1McSCDcuB2E9Q-1755486640552-0.0.1.1-604800000; _cfuvid=8APkjIE6NYiKmjQ.WkToUI4bZbkc3QP1PXEX.no0S4Y-1755654910894-0.0.1.1-604800000; _cfuvid=q1oyAHQMk9OS5p8qtijVOUjTAGaXCk76dQvBO.XWBsI-1761817217.7664132-1.0.1.1-RLGNkTTsvRyU3IXd3.K9hHum9DCFyXDfNrK_.8LjtNM',
    'Authorization': f'Bearer {token}'
    }
    conn.request("POST", "/v1/api/cross/private/generatedata/api/cross-interface", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print(type(data.decode("utf-8")))
    supervisor_json = data.decode("utf-8")
    return supervisor_json

# get_supervisor("900003")