from ..utillake import Utillake


class Modellake:
    def __init__(self):
        self.utillake=Utillake()
        self.modellake_id = None
        self.params = {}

    def translate(self, payload):
        api_endpoint = '/modellake/translate'
        return self.utillake.call_api(api_endpoint, payload, self)

    def chat_complete(self, payload):
        api_endpoint = '/modellake/chat/completion'
        return self.utillake.call_api(api_endpoint, payload, self)

    def text_to_speech(self, payload):
        api_endpoint = '/modellake/textToSpeech'
        return self.utillake.call_api(api_endpoint, payload, self)


    def create(self, payload=None):
        api_endpoint = '/modellake/create'
        if not payload:
            payload = {}

        response = self.utillake.call_api(api_endpoint, payload, self)
        if response and 'modellake_id' in response:
            self.modellake_id = response['modellake_id']

        return response

