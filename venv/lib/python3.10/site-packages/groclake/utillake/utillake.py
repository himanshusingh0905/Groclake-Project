from flask import Flask, request, jsonify
from ..config import BASE_URL
import requests
import os
import uuid


class GrocAgent:
    _intent = []
    _agent_name = None
    _intent_handlers = {}
    _app = None

    def __init__(self, app, agent_name, initial_intent=None, intent_description=None, intent_handler=None, adaptor_config=None):
        """
        Initializes the GrocAgent with a name and optionally registers an initial intent.

        Args:
            agent_name (str): The name of the agent.
            initial_intent (str, optional): The initial intent to register.
            intent_description (str, optional): Description of the initial intent.
        """
        self._app = app
        self._agent_name = agent_name
        self._intent = ["summarize", "sentiment", "chat"]  # List of registered intents
        self._intent_handlers = {
            "summarize": self._handleSummarize,
            "sentiment": self._handleSentiment,
            "chat": self._handleChat,
        }
        if initial_intent:
            self._intent_handlers[initial_intent] = intent_handler

        # Add the adaptor configuration handling
        _handler = self.intentOrchestrator

        # Pass adaptor_config to AttpAdaptor
        self.adaptor = AttpAdaptor(app, _handler, adaptor_config)

        if initial_intent and intent_description:
            error = self.registerIntent(initial_intent, intent_description)
            if error:
                print(error)

    def run(self, host="0.0.0.0", port=5000, debug=True):
        """
        Proxy method to run the Flask app.
        """
        #print(f"Starting {self.agent_name} on {host}:{port} with debug={debug}")
        self._app.run(host=host, port=port, debug=debug)

    def intentDetect(self, query_text, intent, entities, metadata):
        """
        Detects the intent based on the given query text and metadata.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            str: The detected intent.
        """
        # Simulated logic to detect intent (expand as needed)
        return intent

    def intentOrchestrator(self, attphandler_payload):
        """
        Handles the detected intent and provides a response.

        Args:
            query_text (str): The input text to analyze.
            intent (str): The detected intent.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Response in a structured format.
        """
        intent = attphandler_payload.get("intent")
        entities = attphandler_payload.get("entities", [])
        metadata = attphandler_payload.get("metadata", {})
        query_text = attphandler_payload.get("query_text")
        if intent in self._intent_handlers:
            response = self._intent_handlers.get(intent)(attphandler_payload)
            return response
        else:
            # Default response if intent is not recognized
            return {
                    "entities": entities,
                    "intent": intent,
                    "metadata": metadata,
                    "query_text": query_text,
                    "response_text": f"Intent '{intent}' not recognized.",
                    "status": 400
            }

    def _handleSummarize(self, query_text, entities, metadata):
        """
        Handles the 'summarize' intent by creating a summary based on the query text.

        Args:
            query_text (str): The input text to summarize.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        summary = f"Summary of the query: {query_text[:50]}..."
        return {
            "body": {
                "query_text": query_text,
                "response_text": summary,
                "intent": "summarize",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def _handleSentiment(self, query_text, entities, metadata):
        """
        Handles the 'sentiment' intent by analyzing the sentiment of the query text.

        Args:
            query_text (str): The input text to analyze.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        sentiment = "positive" if "good" in query_text else "negative" if "bad" in query_text else "neutral"
        return {
            "body": {
                "query_text": query_text,
                "response_text": f"Sentiment detected: {sentiment}",
                "intent": "sentiment",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def _handleChat(self, query_text, entities, metadata):
        """
        Handles the 'chat' intent by generating a chatbot response.

        Args:
            query_text (str): The input text for the chatbot.
            entities (list): The extracted entities.
            metadata (dict): Additional metadata for context.

        Returns:
            dict: Structured response.
        """
        from groclake.modellake import Modellake
        model = Modellake()
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": query_text}
            ]
        }
        chat_response = model.chat_complete(payload=payload)

        return {
            "body": {
                "query_text": query_text,
                "response_text": chat_response,
                "intent": "chat",
                "entities": entities,
                "metadata": metadata,
                "status": 200
            }
        }

    def registerIntent(self, intent, intent_description):
        """
        Registers a new intent with its description.

        Args:
            intent (str): The name of the intent to register.
            intent_description (str): A description of the intent.

        Returns:
            str: Error message if registration fails, otherwise None.
        """
        if intent in [i[0] for i in self._intent]:
            return f"Error: Intent '{intent}' is already registered."

        self._intent.append([intent, intent_description])
        return None

    def registerHandler(self, intent_name, handler_function):
        """
        Dynamically registers a handler function for a specific intent.

        Args:
            intent_name (str): The name of the intent.
            handler_function (callable): The handler function.

        Returns:
            str: Success message or error message if the intent is already registered.
        """
        if intent_name in self._intent_handlers:
            return f"Error: Intent '{intent_name}' is already registered."

        self._intent_handlers[intent_name] = handler_function
        return f"Handler for intent '{intent_name}' successfully registered."

    def getName(self):
        """
        Returns the name of the agent.

        Returns:
            str: The name of the agent.
        """
        return self._agent_name

    def getIntent(self):
        """
        Returns the list of registered intents.

        Returns:
            list: The list of registered intents.
        """
        return self._intent


class AttpAdaptor:
    def __init__(self, app, callback,adaptor_config):
        self.app = app
        self.callback = callback
        self.apc_id = adaptor_config.get('apc_id')
        self.client_agent_uuid = adaptor_config.get('client_agent_uuid')
        self.app.add_url_rule('/query', 'query_handler', self.query_handler, methods=['POST'])
        self.app.add_url_rule('/readme', 'readme_handler', self.readme_handler, methods=['POST'])
        self.app.add_url_rule('/pinger', 'pinger_handler', self.pinger_handler, methods=['POST'])

    def extract_header(self, request_data):
        """
        Extracts the header from the request data.
        """
        header = request_data.get('header', {})
        return {
            'client_agent_uuid': header.get('client_agent_uuid'),
            'server_agent_uuid': header.get('server_agent_uuid'),
            'message_id': header.get('message_id'),
            'task_id': header.get('task_id'),
            'apc_id': header.get('apc_id'),
            'auth_token': header.get('auth_token'),
        }

    def extract_body(self, request_data):
        """
        Extracts the body from the request data.
        """
        body = request_data.get('body', {})
        return {
            'query_text': body.get('query_text'),
            'intent': body.get('intent'),
            'entities': body.get('entities'),
            'metadata': body.get('metadata'),
        }

    def create_header(self, auth_token, apc_id, server_agent_uuid, client_agent_uuid, message_id, task_id):
        """
        Creates the header part of the response payload.
        """
        return {
            "version": "1.0",
            "message": "response",
            "content-type": "application/json",
            "auth_token": auth_token,
            "apc_id": apc_id,
            "server_agent_uuid": server_agent_uuid,
            "client_agent_uuid": client_agent_uuid,
            "message_id": message_id,
            "task_id": task_id,
        }

    def create_body(self, response):
        """
        Creates the body part of the response payload.
        """
        return {
            "query_text": response.get("query_text", ""),
            "response_text": response.get("response_text", "Search completed successfully."),
            "intent": response.get("intent", None),
            "entities": response.get("entities", []),
            "metadata": response.get("metadata", {}),
        }

    def get_readme_content(self, readme_payload):
        """
        Reads the content of a README file if it exists and constructs a response.
        """
        query_text = readme_payload.get("query_text", "")
        intent = readme_payload.get("intent", "")
        entities = readme_payload.get("entities", [])
        metadata = readme_payload.get("metadata", {})

        readme_file_path = os.path.join(os.getcwd(), '.readme')

        if os.path.exists(readme_file_path):
            with open(readme_file_path, 'r') as file:
                readme_content = file.read()
        else:
            readme_content = "README file not found."

        return {
            "query_text": query_text,
            "response_text": readme_content,
            "intent": intent,
            "entities": entities,
            "metadata": metadata,
        }


    def sendQuery(self, server_uuid, payload , task_id):
        try:
            url = f"https://api-uat-cartesian.groclake.ai/agache/agent/{server_uuid}/query"
            message_id = str(uuid.uuid4())

            headers = {
                "content-type": "application/json"
            }

            body_payload = {
                "header": {
                    "version": "1.0",
                    "message": "Request",
                    "Content-Type": "application/json",
                    "apc_id": self.apc_id,
                    "server_agent_uuid": server_uuid,
                    "client_agent_uuid": self.client_agent_uuid,
                    "message_id": message_id,
                    "task_id" : task_id
                },
                "body": {
                    "query_text": payload.get("query_text", ""),
                    "intent": payload.get("intent"),
                    "entities": payload.get("entities", []),
                    "metadata": payload.get("metadata", {})
                }
            }

            # Send the HTTP POST request
            response = requests.post(url, json=body_payload, headers=headers)
            response.raise_for_status()

            # Return the response from the server
            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Error in sendQuery: {str(e)}")
            return {"error": "Failed to send query"}

    def query_handler(self):
        try:
            request_data = request.get_json()
            print(f"Received request data: {request_data}")
            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            # Prepare payload for callback
            attphandler_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata')
            }

            # Call the callback function
            response = self.callback(attphandler_payload)

            # Create header and body
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body(response)

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            print(f"Error in query_handler: {str(e)}")  # For debugging
            return jsonify({"error": "Internal Server Error"}), 500

    def readme_handler(self):
        try:
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                body.get('query_text'),
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            readme_payload = {
                "query_text": body.get('query_text'),
                "intent": body.get('intent'),
                "entities": body.get('entities'),
                "metadata": body.get('metadata')
            }

            response = self.get_readme_content(readme_payload)

            # Create header and body
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body(response)

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            print(f"Error in readme_handler: {str(e)}")  # For debugging
            return jsonify({"error": "Internal Server Error"}), 500

    def pinger_handler(self):
        try:
            # Get JSON data from the request
            request_data = request.get_json()

            # Extract header and body
            header = self.extract_header(request_data)
            body = self.extract_body(request_data)

            # Handle missing fields
            if not all([
                header.get('client_agent_uuid'),
                header.get('server_agent_uuid')
            ]):
                return jsonify({"error": "Missing required fields in payload"}), 400

            # Set the response text to "yes"
            response_text = "yes"

            # Create header and body for response
            header_part = self.create_header(
                header.get('auth_token'),
                header.get('apc_id'),
                header.get('server_agent_uuid'),
                header.get('client_agent_uuid'),
                header.get('message_id'),
                header.get('task_id')
            )
            body_part = self.create_body({
                "intent": body.get('intent', ''),
                "query_text": body.get('query_text', ''),
                "entities": body.get('entities', []),
                "metadata": body.get('metadata', {}),
                "response_text": response_text
            })

            # Create the response payload
            response_payload = {
                "header": header_part,
                "body": body_part
            }

            return jsonify(response_payload), 200

        except Exception as e:
            # Log the error and return a generic message
            print(f"Error in pinger_handler: {str(e)}")
            return jsonify({"error": "Internal Server Error"}), 500

class Utillake:
    def __init__(self):
        self.groc_api_key = self.get_groc_api_key()

    @staticmethod
    def get_groc_api_key():
        groc_api_key = os.getenv('GROCLAKE_API_KEY')
        if not groc_api_key:
            raise ValueError("GROCLAKE_API_KEY is not set in the environment variables.")
        groc_account_id = os.getenv('GROCLAKE_ACCOUNT_ID')
        if not groc_account_id:
            raise ValueError("GROCLAKE_ACCOUNT_ID is not set in the environment variables.")
        return groc_api_key

    @staticmethod
    def _get_groc_api_headers():
        return {'GROCLAKE-API-KEY': os.getenv('GROCLAKE_API_KEY')}

    @staticmethod
    def _add_groc_account_id(payload):
        return payload.update({'groc_account_id': os.getenv('GROCLAKE_ACCOUNT_ID')})


    def call_api(self, endpoint, payload,lake_obj=None):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if lake_obj:
            lake_ids = ['cataloglake_id', 'vectorlake_id', 'datalake_id', 'modellake_id']

            for lake_id in lake_ids:
                if hasattr(lake_obj, lake_id) and getattr(lake_obj, lake_id):
                    payload[lake_id] = getattr(lake_obj, lake_id)

        self._add_groc_account_id(payload)
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}

    def get_api_response(self, endpoint):
        headers = self._get_groc_api_headers()
        url = f"{BASE_URL}{endpoint}"
        if not endpoint:
            raise ValueError("Invalid API call.")
        try:
            response = requests.get(url, headers=headers, timeout=90)
            response_data = response.json()
            if response.status_code == 200 and 'api_action_status' in response_data:
                response_data.pop('api_action_status')
            return response_data if response.status_code == 200 else {}
        except requests.RequestException as e:
            return {}
