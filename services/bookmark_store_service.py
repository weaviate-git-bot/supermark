import abc
import asyncio
from functools import lru_cache
from typing import List

from google.cloud.firestore_v1 import ArrayUnion, ArrayRemove

from config import Config
from models.bookmark_store import UserDoc
from models.extension import ExtensionDocument
from models.extension import ExtensionDocument, ExtensionPDFDocument
from services.context_service import config
from utils.db import firebase_app, async_firebase_app


class BaseBookmarkStoreService(abc.ABC):
    @abc.abstractmethod
    def get_user_folders(self, x_uid: str):
        pass

    @abc.abstractmethod
    def get_bookmarks_by_url(self, x_uid: str, url: str):
        pass

    @abc.abstractmethod
    def add_bookmark(self, x_uid: str, document: ExtensionDocument):
        pass

    @abc.abstractmethod
    def delete_user_bookmark(self, x_uid: str, document: ExtensionDocument):
        pass


class AsyncBookmarkStoreService(BaseBookmarkStoreService):
    def __init__(self):
        self.db = async_firebase_app
        self.config = Config()

    @lru_cache(maxsize=64)
    def get_user_document(self, x_uid: str):
        if config.environment == 'production':
            return self.db.collection('users').document(x_uid)
        else:
            return self.db.collection('test_users').document(x_uid)


    async def get_user_folders(self, x_uid: str) -> List[str]:
        doc_ref = self.get_user_document(x_uid)
        doc = await doc_ref.get()
        if not doc.exists:
            raise Exception(f'User {x_uid} does not exist')
        return UserDoc.parse_obj(doc.to_dict()).folders

    async def get_bookmarks_by_url(self, x_uid: str, url: str):
        doc_ref = self.get_user_document(x_uid).collection('bookmarks')
        docs = await doc_ref.where('url', '==', url).get()
        return [doc.to_dict() for doc in docs]

    async def add_bookmark(self, x_uid: str, document: ExtensionDocument | ExtensionPDFDocument):
        user_doc_ref = self.get_user_document(x_uid)
        firebase_data = {
            'folder': document.folder,
            'timestamp': document.timestamp,
            'url': document.url,
            'title': document.title,
            'type': "pdf" if isinstance(document, ExtensionPDFDocument) else "url"
        }
        add_bookmark_task = user_doc_ref.collection('bookmarks').add(firebase_data)
        create_new_folder_task = user_doc_ref.update({
            'folders': ArrayUnion([document.folder])
        })
        bookmark_task, folder_task = await asyncio.gather(add_bookmark_task, create_new_folder_task)
        return bookmark_task[1]  # bookmark_task: Tuple[timestamp, ref]

    async def delete_user_bookmark(self, x_uid: str, document: ExtensionDocument | ExtensionPDFDocument):
        col_ref = self.get_user_document(x_uid).collection('bookmarks')
        docs = col_ref.where("url", '==', document.url).stream()

        for doc in docs:
            await doc.reference.delete()

    async def batch_delete(self, x_uid: str, ids: List[str], folders_to_delete: List[str] | None = None):
        doc_refs = [
            self.get_user_document(
                x_uid
            ).collection(
                'bookmarks'
            ).document(_id) for _id in ids
        ]
        await asyncio.gather(*[doc_ref.delete() for doc_ref in doc_refs])
        if folders_to_delete:
            user_doc_ref = self.get_user_document(x_uid)
            await user_doc_ref.update({
                'folders': ArrayRemove(folders_to_delete)
            })

