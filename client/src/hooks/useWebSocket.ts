import { useState, useRef, useCallback } from 'react';

import { createWebSocket } from '../services/websocketService';
import type {
  InitStateMessage,
  UsersMessage,
  BpmnUpdateMessage,
  LockMessage,
  UnlockMessage,
  LocksSyncMessage,
  OutgoingMessage,
  User,
} from '../types/messages';

export function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null);

  const [connected, setConnected] = useState(false);
  const [users, setUsers] = useState<User[]>([]);
  const [locks, setLocks] = useState<Record<string, string>>({});
  const [revision, setRevision] = useState(0);
  const [yourId, setYourId] = useState<string | null>(null);
  const [initialXml, setInitialXml] = useState<string | null>(null);

  const send = useCallback((data: OutgoingMessage) => {
    const ws = wsRef.current;
    if (ws?.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(data));
    }
  }, []);

  const init = useCallback(() => {
    if (wsRef.current) return;

    wsRef.current = createWebSocket(url, {
      onConnected: () => setConnected(true),
      onDisconnected: () => setConnected(false),

      onInitState: (msg: InitStateMessage) => {
        setYourId(msg.current_user_id);
        setUsers(msg.users);
        setRevision(msg.revision);
        setInitialXml(msg.xml);
        setLocks(msg.locks);
      },

      onUsers: (msg: UsersMessage) => setUsers(msg.users),

      onBpmnUpdate: (msg: BpmnUpdateMessage) => {
        setRevision(msg.revision);
        setInitialXml(msg.xml);
      },

      onLock: (msg: LockMessage) => setLocks((prev) => ({ ...prev, [msg.elementId]: msg.userId })),

      onUnlock: (msg: UnlockMessage) =>
        setLocks((prev) => {
          const next = { ...prev };
          delete next[msg.elementId];
          return next;
        }),

      onLocksSync: (msg: LocksSyncMessage) => setLocks(msg.locks),
    });
  }, [url]);

  return {
    init,
    send,
    connected,
    users,
    locks,
    revision,
    yourId,
    initialXml,
  };
}
