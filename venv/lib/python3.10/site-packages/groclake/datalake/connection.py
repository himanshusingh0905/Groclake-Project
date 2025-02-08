# connection.
import mysql.connector
import redis
from elasticsearch import Elasticsearch
from io import BytesIO
from PIL import Image
import requests
from google.cloud import storage
from google.oauth2 import service_account
import boto3
import uuid
from pymongo import MongoClient
import base64



class Connection:
    def __init__(self):
        self.connection = None

    def connect(self):
        raise NotImplementedError("Subclasses must implement the connect method.")

    def read(self, query):
        raise NotImplementedError("Subclasses must implement the read method.")

class SQLConnection(Connection):
    def __init__(self, db_config):
        super().__init__()
        self.db_config = db_config
        self.cursor = None  # Initialize the cursor attribute
        self.connect()

    def connect(self):
        try:
            if self.connection and self.connection.is_connected():
                return  # Connection is active, no need to reconnect
            self.connection = mysql.connector.connect(**self.db_config)
            self.cursor = self.connection.cursor(dictionary=True)
        except mysql.connector.Error as e:
            print(f"Error connecting to MySQL: {e}")
            self.connection = None
    def ensure_connection(self):
        """Reconnects if the connection is lost."""
        if not self.connection or not self.connection.is_connected():
            self.connect()

    def read(self, query, params=None, multiple=False, parsed=True):
        self.ensure_connection()
        """
        Executes a SELECT query and retrieves the result.

        Args:
            query (str): SQL query to execute.
            params (tuple): Parameters for the SQL query.
            fetch_all (bool): Whether to fetch all results or a single result.
            parsed (bool): Whether to parse results into a dictionary.

        Returns:
            list or dict: Query result as a list of dictionaries (fetch_all=True),
                          or a single dictionary (fetch_all=False and parsed=True).
        """
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
            cursor = self.connection.cursor(dictionary=parsed)
            cursor.execute(query, params)

            if multiple:
                # Fetch all rows and return as a list
                result = cursor.fetchall()
            else:
                # Fetch a single row
                result = cursor.fetchone()

            # Return an empty dictionary or list if no result is found
            if multiple and not result:
                return []
            elif not multiple and not result:
                return {} if parsed else None

            return result
        except mysql.connector.Error as err:
            raise Exception(f"MySQL query error: {err}")
        finally:
            cursor.close()


    def write(self, query, params=None):
        self.ensure_connection()

        """
        Executes a write query and commits the transaction.

        Args:
            query (str): The SQL query to execute.
            params (tuple or None): Parameters to pass to the query.

        Returns:
            int: The last inserted ID if applicable.
        """
        if not self.connection:
            raise Exception("Connection not established. Call connect() first.")
        try:
            self.cursor.execute(query, params or ())
            self.connection.commit()
            return self.cursor.lastrowid
        except Exception as e:
            self.connection.rollback()
            print(f"Error executing write query: {e}")
            raise

    def close(self):
        """Closes the connection and cursor."""
        if self.cursor:
            self.cursor.close()
            self.cursor = None
        if self.connection:
            self.connection.close()
            self.connection = None


    #Add close method here as well

class RedisConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config

    def connect(self):
        self.connection = redis.StrictRedis(**self.config)

    def read(self, query):
        if not self.connection:
            raise Exception("Connection not established.")
        if query == "dbsize":
            return self.connection.dbsize()
        else:
            raise ValueError("Unsupported query for Redis.")

    def get(self, key):
        return self.connection.get(key)

    def set(self, key, value, cache_ttl=86400):
        """
        Set a value in Redis with an optional TTL (time-to-live).

        Args:
            key (str): The key to set in Redis.
            value (any): The value to associate with the key.
            cache_ttl (int): Time-to-live in seconds (default: 1 day).
        """
        self.connection.set(key, value, ex=cache_ttl)


class ESConnection(Connection):
    def __init__(self, es_host, es_port, es_api_key=None):
        super().__init__()
        self.es_host = es_host
        self.es_port = es_port
        self.api_key = es_api_key
        self.connection = None  # Initialize connection here

    def connect(self):
        """
        Establishes a connection to Elasticsearch
        """
        self.connection = Elasticsearch(
            f"http://{self.es_host}:{self.es_port}/",
            api_key=self.api_key
        )

    def read(self, query):
        """
        Executes a query to Elasticsearch, here 'query' contains 'index' dynamically passed in.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        # Access 'index' dynamically from 'query' dictionary
        index = query.get('index')
        body = query.get('body')

        es_response = self.connection.count(index=index, body=body)
        return es_response.get("count", 0)

    def write(self, query, params=None):
        """
        Executes a write query to Elasticsearch, where 'index' is dynamically passed in.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        index = query.get('index')
        body = query.get('body')

        try:
            response = self.connection.index(index=index, body=body)
            return response
        except Exception as e:
            raise Exception(f"Error executing write query: {e}")

    def search(self, query=None, index=None, body=None):
        """
        Executes a search query to Elasticsearch.
        Accepts a dictionary query or individual index and body arguments.
        """
        if not self.connection:
            raise Exception("Connection not established.")

        # Validate index and body
        if not index or not body:
            raise ValueError("Both 'index' and 'body' are required for the search query.")

        try:
            response = self.connection.search(index=index, body=body)
            return response
        except Exception as e:
            raise Exception(f"Error executing search query: {e}")



class GCPConnection(Connection):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.gcp_storage = None
        self.bucket = None
        self.bucket_name = config.get("gcp_bucket_name")
        self.IMAGE_PREFIX  = config.get("host_cdn_url")
        if not self.bucket_name:
            raise ValueError("Bucket name is required in GCP config.")

    def connect(self):
        """
        Establishes a connection to the specified GCP bucket by initializing the storage client.
        """
        try:
            credentials_json = self.config.get("gcp_credentials_json")
            if not credentials_json:
                raise ValueError("Service account file is required in GCP config.")

            if isinstance(credentials_json, dict):
                # Create credentials from a dictionary
                credentials = service_account.Credentials.from_service_account_info(credentials_json)
            else:
                raise ValueError("The credentials_json must be a dictionary.")

            # Initialize the GCP storage client
            self.gcp_storage = storage.Client(credentials=credentials)
            self.bucket = self.gcp_storage.bucket(self.bucket_name)

        except Exception as e:
            raise ConnectionError(f"Failed to connect to GCP bucket: {e}")

    @staticmethod
    def decode_base64_image(base64_string):
        """Decodes base64 string to bytes."""
        return base64.b64decode(base64_string)

    @staticmethod
    def download_image_from_url(url):
        """Downloads an image from the given URL and returns the binary content."""
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return response.content
        else:
            raise ValueError(f"Failed to download image from URL: {response.status_code}")

    @staticmethod
    def process_image_to_webp(image_content):
        """Processes the image and converts it to WEBP format."""
        image = Image.open(BytesIO(image_content)).convert('RGBA')
        webp_image = BytesIO()
        image.save(webp_image, 'WEBP', quality=90)
        webp_image.seek(0)
        return webp_image


    @staticmethod
    def process_image(response):
        image = Image.open(BytesIO(response)).convert('RGBA')
        if image.mode == 'RGB':
            file_ext = '.jpg'
            content_type = 'image/jpg'
            format_type = 'JPEG'
        else:
            file_ext = '.png'
            content_type = 'image/png'
            format_type = 'PNG'
        gcp_file = BytesIO()
        image.save(gcp_file, format=format_type)
        gcp_file.seek(0)
        return gcp_file, file_ext, content_type



    def upload(self, params):
        """Handles image processing and uploads to GCP."""
        image_type = params.get("image_type")
        image_data = params.get("image_data")
        image_format = params.get("image")
        destination_blob_name = params.get("gcp_bucket_path")

        if not image_type or not image_data:
            raise ValueError("Both image_type and image_data must be provided.")

        # Process image
        if image_type == "base64":
            processed_image = self.decode_base64_image(image_data)
        elif image_type == "url":
            processed_image = self.download_image_from_url(image_data)
        else:
            raise ValueError("Unsupported image type. Use 'base64' or 'url'.")

        # Logic for processing and uploading images based on format
        if image_format == "webp":
            # Convert to WEBP format
            webp_image = self.process_image_to_webp(processed_image)
            self.upload_webp_image(webp_image, destination_blob_name, content_type="image/webp")
            return self.IMAGE_PREFIX + destination_blob_name + ".webp"
        else:
            # Convert to JPEG format
            image_data, file_ext, content_type = self.process_image(processed_image)
            self.upload_jpeg_image(image_data, destination_blob_name, file_ext, content_type)
            return self.IMAGE_PREFIX + destination_blob_name + f'{file_ext}'


    def upload_webp_image(self, image_data, destination_path, content_type="image/webp"):
        bucket = self.gcp_storage.bucket(self.bucket_name)
        destination_path += '.webp'
        blob = bucket.blob(destination_path)
        blob.upload_from_file(image_data, content_type=content_type)


    def upload_jpeg_image(self, image_data, destination_path, file_ext, content_type):
        bucket = self.gcp_storage.bucket(self.bucket_name)
        destination_path += f'{file_ext}'
        blob = bucket.blob(destination_path)
        blob.upload_from_file(image_data, content_type=content_type)





class S3Connection(Connection):

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.s3_client = None
        self.s3_bucket = config.get("aws_s3_bucket")
        self.region_name = config.get("aws_region_name", "us-east-1")
        self.S3_FOLDER = config.get("aws_s3_folder")



    def connect(self):
        """
        Establishes a connection to the specified S3 bucket by initializing the S3 client.
        """
        try:
            aws_access_key_id = self.config.get("aws_access_key_id")
            aws_secret_access_key = self.config.get("aws_secret_access_key")
            if not aws_access_key_id or not aws_secret_access_key:
                raise ValueError("AWS access key ID and secret access key are required in S3 config.")

            # Initialize the S3 client
            self.s3_client = boto3.client(
                "s3",
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                region_name=self.region_name
            )
        except Exception as e:
            raise ConnectionError(f"Failed to connect to S3 bucket: {e}")

    def download_file_from_url(self, file_url):
        try:
            response = requests.get(file_url)
            response.raise_for_status()
            content_type = response.headers.get('Content-Type')
            extension = 'pdf' if 'pdf' in content_type else 'docx'
            filename = f"downloaded_document.{extension}"
            file_obj = BytesIO(response.content)

            return file_obj, filename
        except requests.RequestException as e:
            raise ValueError("Failed to download file from URL") from e

    def decode_base64_data(self, base64_data):
        try:
            decoded_data = base64.b64decode(base64_data)
            filename = f"{uuid.uuid4().hex[:16]}.pdf"
            file_obj = BytesIO(decoded_data)
            return file_obj, filename
        except Exception as e:
            raise ValueError("Invalid base64 data") from e

    def upload(self, params):
        document_type = params.get("document_type")
        document_data = params.get("document_data")
        file_obj, filename = self.download_file_from_url(document_data)
        folder_name = params.get("folder_name")

        if document_type == "base64":
            file_obj, filename = self.decode_base64_data(document_data)
        elif document_type == "url":
            file_obj, filename = self.download_file_from_url(document_data)
        else:
            raise ValueError("Unsupported document type. Use 'base64' or 'url'.")

        try:
            # s3_key = f"{self.folder_name}/{filename}"
            s3_key = f'{self.S3_FOLDER}/{folder_name}/{filename}'
            self.s3_client.upload_fileobj(
                file_obj,
                self.s3_bucket,
                s3_key            )
            return f'https://{self.s3_bucket}/{s3_key}'
        except Exception as e:
            return e
            raise


class MongoDBConnection(Connection):
    """
    Class to manage MongoDB connections and operations.
    """

    def __init__(self, config):
        super().__init__()
        self.config = config
        self.client = None
        self.database = None

    def connect(self):
        """
        Establishes a connection to the MongoDB database.
        """
        try:
            cluster = self.config.get("connection_string")
            database_name = self.config.get("data_base")
            if not cluster or not database_name:
                raise ValueError("MongoDB 'cluster' and 'data_base' are required in the config.")

            self.client = MongoClient(cluster)
            self.database = self.client[database_name]
        except Exception as e:
            raise ConnectionError(f"Failed to connect to MongoDB: {e}")

    def insert(self, collection_name, data):
        """
        Inserts a document into a MongoDB collection.

        :param collection_name: Name of the collection to insert the document.
        :param data: Dictionary representing the document to insert.
        :return: The inserted document ID.
        """
        try:
            collection = self.database[collection_name]
            result = collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise RuntimeError(f"Failed to insert data into MongoDB: {e}")


    def read(self, collection_name, query):
        """
        Reads documents from a MongoDB collection based on a query.

        :param collection_name: Name of the collection to read from.
        :param query: Dictionary representing the query to filter documents.
        :return: List of matching documents.
        """
        try:
            collection = self.database[collection_name]
            results = collection.find(query)
            return [doc for doc in results]
        except Exception as e:
            raise RuntimeError(f"Failed to read data from MongoDB: {e}")