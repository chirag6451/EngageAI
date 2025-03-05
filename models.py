from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None

class UserInDB(User):
    id: int
    hashed_password: str

class FileUpload(BaseModel):
    file_id: int
    filename: str
    row_count: Optional[int] = None
    columns: Optional[List[str]] = None
    created_at: Optional[datetime] = None

class FileData(BaseModel):
    data_id: int
    file_id: int
    row_data: Dict
    column_names: List[str]
