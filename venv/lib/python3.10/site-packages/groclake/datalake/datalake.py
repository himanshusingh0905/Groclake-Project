from .pipeline import Pipeline
import threading
from ..utillake import Utillake


class Datalake:
    def __init__(self):
        self.pipelines = {}
        self.utillake=Utillake()
        self.datalake_id = None
        self.params = {}

    def create_pipeline(self, name):
        if name in self.pipelines:
            raise ValueError(f"Pipeline with name '{name}' already exists.")
        pipeline = Pipeline(name)
        self.pipelines[name] = pipeline
        return pipeline

    def get_pipeline_by_name(self, name):
        return self.pipelines.get(name)

    def execute_all(self):
        threads = []
        for pipeline in self.pipelines.values():
            thread = threading.Thread(target=pipeline.execute)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()


    def create(self, payload=None):
        api_endpoint = '/datalake/create'
        if not payload:
            payload = {}

        response = self.utillake.call_api(api_endpoint, payload, self)
        if response and 'datalake_id' in response:
            self.datalake_id = response['datalake_id']

        return response

    def document_fetch(self, payload):
        api_endpoint = '/datalake/document/fetch'
        return self.utillake.call_api(api_endpoint, payload, self)

    def document_push(self, payload):
        api_endpoint = '/datalake/document/push'
        return self.utillake.call_api(api_endpoint, payload, self)