from fastapi import FastAPI, WebSocket, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.cors import CORSMiddleware

from starlette.requests import Request
import uvicorn
import asyncio
from sqlalchemy.ext.asyncio import AsyncEngine
from starlette.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError

from app.api import auth 
from app.api import menu
from fastapi.encoders import jsonable_encoder
#  users, menu, orders, restaurants, delivery, admin
from app.database import Base, engine

from app.services.websocket_service import start_redis_subscriber
from app.api.middleware.response_middleware import ResponseMiddleware
from app.services.websocket_service import handle_websocket_connection



# Create tables
# Base.metadata.create_all(bind=engine)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


app = FastAPI(
    title="Pizza Delivery API - Slyce",
    description="Backend API for a Pizza Delivery System",
    version="1.0.0",
)

@app.middleware("http")
async def log_request(request: Request, call_next):
    print("Incoming:", request.method, request.url)
    response = await call_next(request)
    return response


origins = [
    "http://localhost:3000",  # Next.js frontend
    "http://127.0.0.1:3000",
    "http://localhost:4000",  # FastAPI backend
    "http://127.0.0.1:4000",
]




# Add middleware
app.add_middleware(ResponseMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(menu.router)

# test post route for send-otp





# Global exception handler
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "error_code": exc.status_code
        }
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal server error",
            "error_code": 500
        }
    )



@app.get("/", tags=["Root"])
async def read_root():
    return {"message": "Welcome to the Slyce - Pizza Delivery API"}


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await handle_websocket_connection(websocket, user_id)

# On app startup, start Redis subscriber
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(start_redis_subscriber())
    await init_db()


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)