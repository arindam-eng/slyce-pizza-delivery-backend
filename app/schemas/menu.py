from pydantic import BaseModel, conlist
from typing import Optional, List
from app.models.sku import SkuSize

class SKUBase(BaseModel):
    code: str
    description: Optional[str] = None
    price: float
    size: SkuSize

class SKUCreate(SKUBase):
    pass

class SKUOut(SKUBase):
    id: int
    class Config:
        from_attributes = True

class MenuBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    image_url: Optional[str] = None
    is_active: bool
    category_id: int
    skus: conlist(SKUCreate, min_length=1, max_length=3)

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    skus: Optional[conlist(SKUCreate, min_length=1, max_length=3)]

class MenuOut(MenuBase):
    id: int
    skus: List[SKUOut]
    class Config:
        from_attributes = True

