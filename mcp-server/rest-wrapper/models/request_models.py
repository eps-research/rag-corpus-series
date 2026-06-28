from typing import Optional
from pydantic import BaseModel, Field

class ListObjectsParams(BaseModel):
    corpus: str
    survey: Optional[str] = None
    tier: Optional[str] = None
    page: Optional[int] = 1
    limit: Optional[int] = 50

class GetObjectParams(BaseModel):
    corpus: str
    object_id: str

class SearchMetadataParams(BaseModel):
    corpus: str
    field: str
    value: str

class FilterObjectsParams(BaseModel):
    corpus: str
    field: str
    min: Optional[float] = None
    max: Optional[float] = None
    omega_ready_only: Optional[bool] = None

class GetCorpusSchemaParams(BaseModel):
    corpus: str
