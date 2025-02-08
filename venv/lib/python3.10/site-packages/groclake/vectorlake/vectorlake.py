from ..utillake import Utillake


class Vectorlake:
    def __init__(self):
        self.utillake = Utillake()
        self.vectorlake_id = None
        self.params = {}

    def generate(self, query):
        api_endpoint = '/vector/generate'
        return self.utillake.call_api(api_endpoint, {'query': query},self)

    def push(self, payload):
        api_endpoint = '/vector/push'
        return self.utillake.call_api(api_endpoint, payload, self)

    def search(self, payload):
        api_endpoint = '/vector/search'
        return self.utillake.call_api(api_endpoint, payload, self)


    def create(self, payload=None):
        api_endpoint = '/vector/create'
        if not payload:
            payload = {}

        response = self.utillake.call_api(api_endpoint, payload, self)

        if response and 'vectorlake_id' in response:
            self.vectorlake_id = response['vectorlake_id']

        return response