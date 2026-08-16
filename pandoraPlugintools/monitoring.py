import json

####
# Define some global variables
#########################################################################################

_MONITORING_ITEMS = []

####
# Set fixed list of monitoring items
#########################################################################################
def set_monitoring_items(data: list = []) -> None:
    """
    Sets the monitoring items list to the specified value.

    Args:
        data (list): A list of monitoring item dicts, each with 'agent_data'
            and 'module_data' keys, as accepted by the '/monitoring' API endpoint.

    Returns:
        None
    """
    global _MONITORING_ITEMS

    _MONITORING_ITEMS = data


####
# Add one monitoring item (agent_data + module_data)
#########################################################################################
def add_monitoring_item(agent_data: dict = {}, module_data: list = []) -> None:
    """
    Adds one monitoring item to the internal monitoring items list.

    Builds a single entry of the '/monitoring' API payload array from an
    agent dict and a list of module dicts. Both are plain dicts the caller
    already built (e.g. via 'init_agent()'/'init_module()' or by hand);
    this function does not validate or transform their shape.

    Args:
        agent_data (dict): A dictionary containing agent configuration.
        module_data (list): A list of dictionaries representing modules.

    Returns:
        None
    """
    global _MONITORING_ITEMS

    _MONITORING_ITEMS.append({"agent_data": agent_data, "module_data": module_data})


####
# Get monitoring items
#########################################################################################
def get_monitoring_items() -> list:
    """
    Retrieves the current monitoring items list.

    Returns:
        list: The list of monitoring items accumulated so far.
    """
    return _MONITORING_ITEMS


####
# Build (and optionally print) the monitoring API payload as JSON
#########################################################################################
def print_monitoring_payload(print_flag: bool = False) -> str:
    """
    Build the JSON array ready to be sent as the request body to the
    '/monitoring' API endpoint, optionally printing it.

    Args:
        print_flag (bool): A flag indicating whether to print the JSON payload.

    Returns:
        str: The JSON representation of the monitoring items list.
    """
    json_string = json.dumps(_MONITORING_ITEMS)

    if print_flag:
        from .output import print_stdout

        print_stdout(json_string)

    return json_string
