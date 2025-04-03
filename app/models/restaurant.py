from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import time

class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    city = Column(String, nullable=False)
    state = Column(String, nullable=False)
    postal_code = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=True)
    opening_time = Column(Time, nullable=False)
    closing_time = Column(Time, nullable=False)
    description = Column(String, nullable=True)
    image_url = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)

    staff = relationship("User", back_populates="restaurant")  # Link to User table

class RestaurantCreate(RestaurantBase):
    pass

class RestaurantUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postal_code: Optional[str] = None
    phone_number: Optional[str] = None
    email: Optional[EmailStr] = None
    opening_time: Optional[time] = None
    closing_time: Optional[time] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None
    image_url: Optional[str] = None

class Restaurant(RestaurantBase):
    id: int
    is_active: bool
    
    class Config:
        from_attributes = True

class RestaurantWithMenu(Restaurant):
    menu_items: List[str] = []  # Just menu item IDs for lighter response
    
    class Config:
        from_attributes = True
