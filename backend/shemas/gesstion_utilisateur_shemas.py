from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Modèles Pydantic
class UserCreate(BaseModel):
    nom: Optional[str] = None
    prenom: Optional[str] = None
    username: str
    email: EmailStr
    password: str
    

class UserResponse(BaseModel):
    id: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    username: str
    email: str 
    created_at: datetime
    is_active: bool

class UserLogin(BaseModel):
    email: EmailStr
    password: str 

class UserUpdate(BaseModel):
    username: str
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: EmailStr
    password: str = Field(..., ge=10, description="Mot de passe minimum 10 caractères")