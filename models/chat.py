from typing import List, Any, Dict, Type

from langchain.schema import Document, BaseMessage, _message_from_dict, _message_to_dict
from pydantic import BaseModel

from models.bookmark import VectorStoreBookmark, VectorStoreBookmarkMetadata


class ChatServiceMessage(BaseModel):
    done: bool = False
    msg: str = ''
    relevant_documents: List[VectorStoreBookmark] = []


class UserChatMessage(BaseModel):
    message: str


class UserSearchMessage(BaseModel):
    query: str
    use_hybrid: bool = True
    certainty: float = 0.8
    limit_chunks: int = 10
    alpha: float = 0.25


class ChatEndpointMessage(BaseModel):
    chat_response: str
    documents: List[VectorStoreBookmarkMetadata]
    done: bool


class ConversationMessage(BaseModel):
    message: Dict[str, Any]
    used_context: List[VectorStoreBookmarkMetadata] | List[str] | None = None
    timestamp: int

    @classmethod
    def parse_obj(cls: Type['ConversationMessage'], obj: Any) -> 'ConversationMessage':
        if isinstance(obj, cls):
            return obj
        if isinstance(obj, dict):
            return cls(
                message=_message_to_dict(_message_from_dict(obj['message'])),
                used_context=obj['used_context'],
                timestamp=obj['timestamp']
            )
        raise TypeError(f'Cannot parse {cls} from {obj}')
