from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.delivery import DeliveryStatus

class DeliveryBase(BaseModel):
    order_id: int
    delivery_notes: Optional[str] = None

class DeliveryCreate(DeliveryBase):
    delivery_person_id: Optional[int] = None

class DeliveryUpdate(BaseModel):
    status: Optional[DeliveryStatus] = None
    delivery_notes: Optional[str] = None
    customer_signature: Optional[bool] = None

class Delivery(DeliveryBase):
    id: int
    delivery_person_id: Optional[int] = None
    status: DeliveryStatus
    assigned_at: datetime
    picked_up_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    customer_signature: bool
    
    class Config:
        from_attributes = True

class DeliveryDetail(Delivery):
    order_total: float
    restaurant_name: str
    customer_name: str
    delivery_address: str
    
    class Config:
        from_attributes = True