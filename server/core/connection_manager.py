from __future__ import annotations

import json
import uuid
from typing import Any, Dict

from fastapi import WebSocket, WebSocketDisconnect

from schema.messages import User
from utils.bpmn_defaults import DEFAULT_BPMN_XML
from core.logger import get_logger

logger = get_logger()


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: Dict[WebSocket, Dict[str, Any]] = {}
        self.diagram_xml: str = DEFAULT_BPMN_XML
        self.revision: int = 0
        self.locks: Dict[str, str] = {}  # {element_id: user_id}

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        user_id = str(uuid.uuid4())[:8]
        user = {"id": user_id, "name": f"User-{user_id}"}
        self.active_connections[websocket] = user

        logger.info("Connected: %s", user_id)

        await self.send_init_state(websocket)
        await self.broadcast_user_list()
        await self.broadcast_locks()

    def disconnect(self, websocket: WebSocket) -> None:
        user = self.active_connections.get(websocket)
        if not user:
            return

        user_id = user["id"]
        logger.info("Disconnected: %s", user_id)

        # Remove all locks owned by this user
        self.locks = {
            element_id: uid
            for element_id, uid in self.locks.items()
            if uid != user_id
        }

        del self.active_connections[websocket]

    async def send_personal_message(self, websocket: WebSocket, message: Dict[str, Any]) -> None:
        await websocket.send_text(json.dumps(message))

    async def broadcast(self, message: Dict[str, Any]) -> None:
        text = json.dumps(message)
        to_remove = []

        for ws in list(self.active_connections.keys()):
            try:
                await ws.send_text(text)
            except WebSocketDisconnect:
                to_remove.append(ws)
            except Exception as exc:
                logger.error("Broadcast error: %s", exc)
                to_remove.append(ws)

        for ws in to_remove:
            self.disconnect(ws)

    async def broadcast_user_list(self) -> None:
        users = [User(**u).model_dump() for u in self.active_connections.values()]
        await self.broadcast({"type": "users", "users": users})

    async def broadcast_locks(self) -> None:
        await self.broadcast({"type": "locks", "locks": self.locks})

    async def send_init_state(self, websocket: WebSocket) -> None:
        users = [User(**u).model_dump() for u in self.active_connections.values()]
        current_user = self.active_connections[websocket]

        message = {
            "type": "init_state",
            "xml": self.diagram_xml,
            "revision": self.revision,
            "users": users,
            "locks": self.locks,
            "current_user_id": current_user["id"],
        }

        await self.send_personal_message(websocket, message)

    def _user_locked_elements(self, user_id: str):
        """Return all elements locked by a user."""
        return [eid for eid, uid in self.locks.items() if uid == user_id]

    async def _auto_unlock_old_locks(self, user_id: str, except_element: str | None):
        """
        Unlock all elements locked by this user except the new one.
        """
        old_elements = self._user_locked_elements(user_id)

        for eid in old_elements:
            if eid == except_element:
                continue

            del self.locks[eid]
            logger.info("Auto-unlock: %s by %s", eid, user_id)

            await self.broadcast({
                "type": "unlock",
                "elementId": eid,
                "userId": user_id
            })

    async def handle_message(self, websocket: WebSocket, data: Dict[str, Any]) -> None:
        msg_type = data.get("type")
        user = self.active_connections.get(websocket)

        if not user:
            return

        user_id = user["id"]

        if msg_type == "bpmn_update":
            xml = data.get("xml")
            if not xml:
                return

            self.diagram_xml = xml
            self.revision += 1

            await self.broadcast({
                "type": "bpmn_update",
                "xml": xml,
                "revision": self.revision,
                "from": user_id
            })

        elif msg_type == "lock":
            element_id = data.get("elementId")
            if not element_id:
                return

            # Unlock all previous locks except the new selection
            await self._auto_unlock_old_locks(user_id, except_element=element_id)

            # Lock the new element
            self.locks[element_id] = user_id
            logger.info("Lock: %s by %s", element_id, user_id)

            await self.broadcast({
                "type": "lock",
                "elementId": element_id,
                "userId": user_id
            })

            # Broadcast full sync
            await self.broadcast_locks()

        elif msg_type == "unlock":
            element_id = data.get("elementId")
            if not element_id:
                return

            if self.locks.get(element_id) == user_id:
                del self.locks[element_id]

                await self.broadcast({
                    "type": "unlock",
                    "elementId": element_id,
                    "userId": user_id
                })

                await self.broadcast_locks()

        else:
            logger.warning("Unknown WS message type: %s", msg_type)
