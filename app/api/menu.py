from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.menu import MenuCreate, MenuUpdate, MenuOut
from app.schemas.category import CategoryOut
from app.services.menu_service import (
    create_menu_item, update_menu_item, get_menu_items, 
    get_menu_item_by_id, remove_menu_item, get_menu_by_category_id,
    update_menu_availability,
    get_categories
)
from app.api.middleware.auth_middleware import get_current_user, role_required

router = APIRouter(prefix="/menu", tags=["Menu"])


@router.get("/all-categories", response_model=list[CategoryOut])
async def get_all_categories():
    print("Fetching categories")
    categories = await get_categories()
    if not categories:
        raise HTTPException(status_code=404, detail="No categories found")
    return categories

@router.post("/", response_model=MenuOut, dependencies=[role_required(["customer"])])
async def create_menu(menu_data: MenuCreate):
    return await create_menu_item(menu_data)

@router.put("/{menu_id}", response_model=MenuOut, dependencies=[role_required(["customer"])])
async def update_menu(menu_id: int, menu_data: MenuUpdate):
    updated_item = await update_menu_item(menu_id, menu_data)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated_item

@router.put("/{menu_id}/availability", dependencies=[role_required(["customer"])])
async def update_menu_status(menu_id: int, is_active: bool):
    updated_item = await update_menu_availability(menu_id, is_active)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu availability updated"}

@router.get("/", response_model=list[MenuOut])
async def read_menu_items():
    return await get_menu_items()

@router.get("/{menu_id}", response_model=MenuOut)
async def read_menu_item(menu_id: int):
    item = await get_menu_item_by_id(menu_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.delete("/{menu_id}", dependencies=[role_required(["customer"])])
async def delete_menu(menu_id: int):
    item = await remove_menu_item(menu_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted"}

@router.get("/category/{category_id}", response_model=list[MenuOut])
async def get_menu_by_category(category_id: int):
    menu_items = await get_menu_by_category_id(category_id)
    return menu_items




