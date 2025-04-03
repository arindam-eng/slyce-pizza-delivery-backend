from sqlalchemy import Column, Integer, String, ForeignKey, Enum
import enum
from sqlalchemy.orm import relationship
from app.database import Base

class SkuSize(str, enum.Enum):
    M = "medium"
    L = "large"
    S = "small"

    
class SKU(Base):
    __tablename__ = "sku"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Integer, nullable=False)
    size = Column(String, nullable=True)
    menu_id = Column(Integer, ForeignKey("menu.id"))
    menu = relationship("Menu", back_populates="skus")
    role = Column(Enum(SkuSize), default=SkuSize.S)