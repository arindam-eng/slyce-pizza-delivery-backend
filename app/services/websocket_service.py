import json
from fastapi import WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List, Any
import asyncio

from app.redis import get_redis

# Store connected websocket clients
connected_clients: Dict[str, List[WebSocket]] = {}

async def handle_websocket_connection(websocket: WebSocket, user_id: str):
    """Handle new websocket connection"""
    await websocket.accept()
    
    if user_id not in connected_clients:
        connected_clients[user_id] = []
    
    connected_clients[user_id].append(websocket)
    
    try:
        while True:
            # Just keep the connection alive and listen
            data = await websocket.receive_text()
            # Process any client messages if needed
    except WebSocketDisconnect:
        # Remove the disconnected client
        connected_clients[user_id].remove(websocket)
        if not connected_clients[user_id]:
            del connected_clients[user_id]

async def broadcast_status_update(user_id: str, data: Any):
    """Broadcast status update to connected clients"""
    if user_id in connected_clients:
        message = json.dumps(data)
        for websocket in connected_clients[user_id]:
            await websocket.send_text(message)

# Redis subscriber for status updates
async def start_redis_subscriber():
    """Subscribe to Redis channels for status updates and broadcast to websockets"""
    redis_client = await get_redis()
    pubsub = redis_client.pubsub()
    
    # Subscribe to status update channel
    await pubsub.subscribe("status_updates")
    
    # Listen for messages
    while True:
        message = await pubsub.get_message(ignore_subscribe_messages=True)
        if message:
            data = json.loads(message["data"])
            user_id = data.get("user_id")
            if user_id:
                await broadcast_status_update(user_id, data)
        
        await asyncio.sleep(0.01)