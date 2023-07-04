from datetime import datetime
from functools import lru_cache

import firebase_admin
import weaviate
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1 import AsyncClient

from config import Config
from utils.files import get_root_path

document_schema = {
    "class": "Document",
    "vectorizer": 'text2vec-openai',
    "properties": [
        {
            "name": "title",
            "dataType": ["string"],
        },
        {
            "name": "url",
            "dataType": ["string"],
        },
        {
            "name": "content",
            "dataType": ["string"],
        },
        {
            "name": "firebase_id",
            "dataType": ["string"],
        },
        {
            "name": "user_id",
            "dataType": ["string"]
        }
    ]
}


@lru_cache()
def get_vectorstore() -> weaviate.Client:
    config = Config()
    print(f'Connecting to Weaviate at {config.weaviate_url}')
    weaviate_client = weaviate.Client(
        config.weaviate_url,
        auth_client_secret=weaviate.AuthApiKey(config.weaviate_key) if config.weaviate_key else None,
        additional_headers={
            "X-OpenAI-Api-Key": Config().openai_api_key
        }
    )

    if not weaviate_client.schema.exists(document_schema['class']):
        weaviate_client.schema.create_class(document_schema)

    return weaviate_client


cred_path = get_root_path().joinpath('bookmarkai-c7f69-0e7393f3fe4e.json')
cred = credentials.Certificate(cred_path)
app = firebase_admin.initialize_app(cred)
firebase_app = firestore.client()

async_firebase_app = AsyncClient.from_service_account_json(
    cred_path
)
