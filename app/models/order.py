from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.order import OrderStatus

class OrderItemBase(BaseModel):
    menu_item_id: int
    quantity: int
    special_instructions: Optional[str] = None

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    price: float
    
    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    restaurant_id: int
    delivery_address_id: int
    special_instructions: Optional[str] = None
    payment_method: str

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    delivery_address_id: Optional[int] = None
    special_instructions: Optional[str] = None
    status: Optional[OrderStatus] = None

class Order(OrderBase):
    id: int
    customer_id: int
    status: OrderStatus
    total_amount: float
    created_at: datetime
    updated_at: datetime
    payment_status: str
    items: List[OrderItem] = []
    
    class Config:
        from_attributes = True

class OrderDetail(Order):
    restaurant_name: str = ""
    customer_name: str = ""
    address_details: str = ""
    
    class Config:
        from_attributes = True