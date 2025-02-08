from ..utillake import Utillake


class Cataloglake():
    def __init__(self):
        self.utillake=Utillake()
        self.cataloglake_id = None
        self.params = {}

    def fetch(self, payload):
        api_endpoint = '/cataloglake/catalog/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def push(self, payload):
        api_endpoint = '/cataloglake/catalog/push'
        return self.utillake.call_api(api_endpoint, payload, self)

    def create_mapper(self, payload):
        api_endpoint = '/cataloglake/catalog/metadata/createmapper'
        return self.utillake.call_api(api_endpoint, payload, self)

    def convert_mapper(self, payload):
        api_endpoint = '/cataloglake/catalog/metadata/convert'
        return self.utillake.call_api(api_endpoint, payload, self)

    def gen(self, payload):
        api_endpoint = '/cataloglake/catalog/gen'
        return self.utillake.call_api(api_endpoint, payload, self)

    def recommend(self, payload):
        api_endpoint = '/cataloglake/catalog/recommender/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def search(self, payload):
        api_endpoint = '/cataloglake/catalog/search/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def update(self, payload):
        api_endpoint = '/cataloglake/catalog/update'
        return self.utillake.call_api(api_endpoint, payload, self)

    def update_inventory(self, payload):
        api_endpoint = '/cataloglake/catalog/inventoryUpdate'
        return self.utillake.call_api(api_endpoint, payload, self)

    def fetch_inventory(self, payload):
        api_endpoint = '/cataloglake/catalog/inventoryFetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def update_price(self, payload):
        api_endpoint = '/cataloglake/catalog/priceUpdate'
        return self.utillake.call_api(api_endpoint, payload, self)

    def fetch_price(self, payload):
        api_endpoint = '/cataloglake/catalog/priceFetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def cache_image(self, payload):
        api_endpoint = '/cataloglake/catalog/imageCache'
        return self.utillake.call_api(api_endpoint, payload, self)

    def create(self, payload=None):
        api_endpoint = '/cataloglake/catalog/create'
        if not payload:
            payload = {}

        response = self.utillake.call_api(api_endpoint, payload, self)

        if response and 'cataloglake_id' in response:
            self.cataloglake_id = response['cataloglake_id']

        return response

    def cache(self, payload):
        api_endpoint = '/cataloglake/catalog/cache'
        return self.utillake.call_api(api_endpoint, payload, self)

    def send(self, payload):
        api_endpoint = '/cataloglake/catalog/send'
        return self.utillake.call_api(api_endpoint, payload, self)

    def delete(self, payload):
        api_endpoint = '/cataloglake/catalog/delete'
        return self.utillake.call_api(api_endpoint, payload, self)

    def search_intent_fetch(self, payload):
        api_endpoint = '/cataloglake/catalog/search/intent/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def address_intent_fetch(self, payload):
        api_endpoint = '/cataloglake/catalog/address/intent/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def fetch_mapper(self, payload):
        api_endpoint = '/cataloglake/catalog/metadata/fetchmapper'
        return self.utillake.call_api(api_endpoint, payload, self)

    def update_mapper(self, payload):
        api_endpoint = '/cataloglake/catalog/metadata/updatemapper'
        return self.utillake.call_api(api_endpoint, payload)

    def cataloglake_catalog_delete(self, cataloglake_id=None):
        api_endpoint = '/cataloglake/catalog/delete'
        if cataloglake_id is None:
            payload = {}
        payload = {"cataloglake_id": cataloglake_id}
        return self.utillake.call_api(api_endpoint, payload)