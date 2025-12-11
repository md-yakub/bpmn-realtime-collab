from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json

from api.routes import router as api_router
from config import CORS_ORIGINS, APP_NAME, APP_VERSION
from core.connection_manager import ConnectionManager
from core.logger import get_logger

logger = get_logger()

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            if isinstance(data, dict):
                await manager.handle_message(websocket, data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast_user_list()
        await manager.broadcast_locks()

    except Exception as exc:
        logger.error("Unexpected WS error: %s", exc)
        manager.disconnect(websocket)
        await manager.broadcast_user_list()
        await manager.broadcast_locks()
