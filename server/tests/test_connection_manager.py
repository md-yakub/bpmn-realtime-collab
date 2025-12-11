import pytest
import json

from core.connection_manager import ConnectionManager
from tests.utils import MockWebSocket
from schema.messages import (
    InitStateMessage,
    UsersMessage,
    BpmnUpdateMessage,
    LockMessage,
    UnlockMessage
)


@pytest.mark.asyncio
async def test_connect_sends_init_and_users():
    manager = ConnectionManager()
    ws = MockWebSocket()

    await manager.connect(ws)

    # ws.sent_messages contains:
    # 0 = init_state
    # 1 = users
    # 2 = locks

    init_msg = json.loads(ws.sent_messages[0])
    InitStateMessage.model_validate(init_msg)

    users_msg = json.loads(ws.sent_messages[1])
    UsersMessage.model_validate(users_msg)

    locks_msg = json.loads(ws.sent_messages[2])
    assert locks_msg["type"] == "locks"
    assert locks_msg["locks"] == {}


@pytest.mark.asyncio
async def test_bpmn_update_broadcast():
    manager = ConnectionManager()
    ws = MockWebSocket()

    await manager.connect(ws)
    ws.sent_messages.clear()

    await manager.handle_message(ws, {
        "type": "bpmn_update",
        "xml": "<xml />"
    })

    assert manager.revision == 1
    assert manager.diagram_xml == "<xml />"

    msg = json.loads(ws.sent_messages[0])
    assert msg["type"] == "bpmn_update"
    BpmnUpdateMessage.model_validate(msg)


@pytest.mark.asyncio
async def test_lock_and_unlock_flow():
    manager = ConnectionManager()
    ws = MockWebSocket()

    await manager.connect(ws)
    ws.sent_messages.clear()

    # Lock element
    await manager.handle_message(ws, {"type": "lock", "elementId": "Task_1"})
    assert manager.locks["Task_1"]

    # We expect TWO messages:
    # 0 → lock event
    # 1 → lock sync
    lock_event = json.loads(ws.sent_messages[0])
    assert lock_event["type"] == "lock"
    LockMessage.model_validate(lock_event)

    lock_sync = json.loads(ws.sent_messages[1])
    assert lock_sync["type"] == "locks"
    assert lock_sync["locks"]["Task_1"] == lock_event["userId"]

    # Now test unlock
    ws.sent_messages.clear()

    await manager.handle_message(ws, {"type": "unlock", "elementId": "Task_1"})
    assert "Task_1" not in manager.locks

    unlock_event = json.loads(ws.sent_messages[0])
    assert unlock_event["type"] == "unlock"
    UnlockMessage.model_validate(unlock_event)

    unlock_sync = json.loads(ws.sent_messages[1])
    assert unlock_sync["type"] == "locks"
    assert unlock_sync["locks"] == {}
