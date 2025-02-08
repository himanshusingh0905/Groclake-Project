from ..utillake import Utillake


class Agentlake:
    def __init__(self):
        self.utillake=Utillake()

    def agent_register(self, payload):
        api_endpoint = '/agentlake/agent/register'
        return self.utillake.call_api(api_endpoint, payload)

    def agent_fetch(self, payload):
        api_endpoint = '/agentlake/agent/fetch'
        return self.utillake.call_api(api_endpoint, payload)

    def category_list_fetch(self):
        api_endpoint = '/agentlake/categorylist/fetch'
        return self.utillake.get_api_response(api_endpoint)

    def apc_create(self, payload):
        api_endpoint = '/agentlake/apc/create'
        return self.utillake.call_api(api_endpoint, payload)

    def apc_agent_assign(self, payload):
        api_endpoint = '/agentlake/apc/agent/assign'
        return self.utillake.call_api(api_endpoint, payload)

