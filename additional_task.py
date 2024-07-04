import json

def convert_table_to_json_query(table, base_ws):
    json_query = {}
    for key in table:
        if key in base_ws:
            json_query[key] = base_ws[key]
        else:
            raise KeyError(f"Key '{key}' not found in base WebSocket response.")

    return json_query


# Example usage
table = {'column1': 'value1', 'column2': 'value2', 'column3': 'value3'}
base_ws = {'column2': 'response2', 'column1': 'response1', 'column3': 'response3'}

try:
    result = convert_table_to_json_query(table, base_ws)
    print(f"JSON Query: {json.dumps(result)}")
except KeyError as e:
    print(f"Error: {e}")
