import json
import pytest
from fastapi.testclient import TestClient
from main import app
from schema.messages import InitStateMessage, UsersMessage, LockMessage, BpmnUpdateMessage

client = TestClient(app)


def test_websocket_connect_sends_init_state_and_users():
    with client.websocket_connect("/ws") as ws:
        msg1 = ws.receive_json()
        msg2 = ws.receive_json()
        msg3 = ws.receive_json()

        # Find init message
        init_msg = next(x for x in (msg1, msg2, msg3) if x["type"] == "init_state")
        InitStateMessage.model_validate(init_msg)

        # Find users message
        users_msg = next(x for x in (msg1, msg2, msg3) if x["type"] == "users")
        UsersMessage.model_validate(users_msg)


def test_websocket_bpmn_update_broadcast():
    with client.websocket_connect("/ws") as ws1:
        with client.websocket_connect("/ws") as ws2:

            # Clear startup messages for ws2
            ws2.receive_json()
            ws2.receive_json()
            ws2.receive_json()

            ws1.send_json({"type": "bpmn_update", "xml": "<X/>"})

            msg = ws2.receive_json()
            assert msg["type"] == "bpmn_update"

            BpmnUpdateMessage.model_validate(msg)


def test_websocket_lock_sync():
    with client.websocket_connect("/ws") as ws1:
        with client.websocket_connect("/ws") as ws2:
            
            for ws in (ws1, ws2):
                ws.receive_json()
                ws.receive_json()
                ws.receive_json()

            ws1.send_json({"type": "lock", "elementId": "Node_1"})

            msg = ws2.receive_json()
            assert msg["type"] == "lock"
            LockMessage.model_validate(msg)
