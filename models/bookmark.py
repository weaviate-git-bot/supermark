from pydantic import BaseModel


class VectorStoreBookmarkMetadata(BaseModel):
    url: str
    title: str
    id: str
    similarity_score: float | None = None

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id


class VectorStoreBookmark(BaseModel):
    page_content: str
    metadata: VectorStoreBookmarkMetadata
