from sqlalchemy.orm import Session
from app.models.menu import Menu
from app.models.category import Category   
from app.models.sku import SKU
from app.models.category import Category
from app.database import get_db
from sqlalchemy.future import select
from app.schemas.menu import MenuCreate, MenuUpdate
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def create_menu_item(menu_data: MenuCreate):
    async with get_db() as db:
        category_stmt = select(Category).where(Category.id == menu_data.category_id)
        category_result = await db.execute(category_stmt)
        category = category_result.scalar_one_or_none()
        if category is None:
            raise HTTPException(status_code=400, detail="Category does not exist")
            
        skus_data = menu_data.skus
        del menu_data.skus
        print(skus_data)
        new_item = Menu(**menu_data.dict())
        db.add(new_item)
        await db.flush()
        
        for sku in skus_data:
            new_sku = SKU(**sku.dict(), menu_id=new_item.id)
            db.add(new_sku)
        
        await db.commit()
        await db.refresh(new_item)
        return new_item

from sqlalchemy.future import select
from fastapi import HTTPException
from app.models.menu import Menu
from app.models.sku import SKU
from app.database import get_db
from app.schemas.menu import MenuUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete

async def update_menu_item(menu_id: int, menu_data: MenuUpdate):
    async with get_db() as db:
        # Fetch menu item
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        item = result.scalars().first()

        if not item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        update_data = menu_data.model_dump(exclude_unset=True)
        skus_data = update_data.pop("skus", None)  # Extract SKUs safely

        # Update menu fields
        for key, value in update_data.items():
            setattr(item, key, value)

        db.add(item)  # Ensure item is added to the session

        if skus_data is not None:
            # Fetch existing SKUs based on menu_id
            existing_skus_stmt = select(SKU).where(SKU.menu_id == menu_id)
            existing_skus_result = await db.execute(existing_skus_stmt)
            existing_skus = {sku.code: sku for sku in existing_skus_result.scalars()}  # Store by code

            # Extract incoming SKU codes properly
            incoming_sku_codes = {sku["code"] for sku in skus_data}
            existing_sku_codes = set(existing_skus.keys())

            # Delete SKUs that are no longer in the request
            for sku_code in existing_sku_codes - incoming_sku_codes:
                await db.execute(delete(SKU).where(SKU.code == sku_code))

            # Update existing SKUs and add new ones
            for sku_data in skus_data:
                sku_code = sku_data["code"]

                if sku_code in existing_skus:
                    # Update existing SKU
                    existing_sku = existing_skus[sku_code]
                    for key, value in sku_data.items():
                        setattr(existing_sku, key, value)
                    db.add(existing_sku)  # Ensure it's updated
                else:
                    # Add new SKU
                    new_sku = SKU(**sku_data, menu_id=menu_id)
                    db.add(new_sku)

        await db.commit()
        await db.refresh(item)

        return item

async def update_menu_availability( menu_id: int, is_active: bool):
    async with get_db() as db:
    # Fetch menu item
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        item = result.scalars().first()
        
        if not item:
            return None
        item.is_active = is_active
        db.commit()
        db.refresh(item)
        return item

async def get_menu_items():
    async with get_db() as db:
        stmt = select(Menu)
        result = await db.execute(stmt)
        return result.unique().scalars().all()

async def get_menu_item_by_id(menu_id: int):
    async with get_db() as db:
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        return result.scalars().first()

async def remove_menu_item(menu_id: int):
    async with get_db() as db:
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await db.execute(stmt)
        item = result.scalars().first()
        
        if not item:
            return None
        
        await db.delete(item)
        await db.commit()
        return item

async def get_menu_by_category_id(category_id: int):
    async with get_db() as db:
        print(f"Fetching menu items for category ID: {category_id}")
        stmt = select(Menu).where(Menu.category_id == category_id)
        result = await db.execute(stmt)
        return result.scalars().unique().all()

async def get_categories():
    async with get_db() as db:
        stmt = select(Category)
        result = await db.execute(stmt)
        return result.scalars().unique().all()