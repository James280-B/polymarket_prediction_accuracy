import requests

from scr.utils import parameters


class SubgraphDataHandler(object):
    _subgraph_url = ("https://api.goldsky.com/api/public/"
                     "project_cl6mb8i9h0003e201j6li0diw/subgraphs/pnl-subgraph/0.0.14/gn")

    def __init__(self, condition_id: str) -> None:
        self.condition_id = condition_id

    def _create_query_for_winning_token(self) -> dict:
        payload = {
            "query": """
                query GetCondition($conditionId: ID!) {
                    condition(id: $conditionId) {
                        id
                        positionIds
                        payoutNumerators
                        payoutDenominator
                    }
                }
            """,
            "variables": {
                "conditionId": f"{self.condition_id}",
            }
        }

        return payload

    def _send_graphql_query_to_subgraph(self, variables) -> dict | None:
        payload = self._create_query_for_winning_token()
        api_key = parameters.read_environment_variable("API_KEY")

        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {api_key}'
        }

        if variables:
            payload['variables'] = variables

        response = requests.post(self._subgraph_url, headers=headers, json=payload)

        if response.status_code == 200:
            return response.json()
        else:
            print("Error:", response.text)
            return None

    def output_query_data(self) -> dict:
        result_dd = self._send_graphql_query_to_subgraph(variables=None)
        print(result_dd)
        return result_dd
