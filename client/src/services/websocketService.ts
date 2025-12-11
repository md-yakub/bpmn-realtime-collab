import type { IncomingMessage } from '../types/messages';

export type WebSocketHandlers = {
  onInitState?: (msg: any) => void;
  onUsers?: (msg: any) => void;
  onBpmnUpdate?: (msg: any) => void;
  onLock?: (msg: any) => void;
  onUnlock?: (msg: any) => void;
  onLocksSync?: (msg: any) => void;
  onConnected?: () => void;
  onDisconnected?: () => void;
};

export function createWebSocket(url: string, handlers: WebSocketHandlers): WebSocket {
  const ws = new WebSocket(url);

  ws.onopen = () => handlers.onConnected?.();
  ws.onclose = ws.onerror = () => handlers.onDisconnected?.();

  ws.onmessage = (event) => {
    const data: IncomingMessage = JSON.parse(event.data);

    switch (data.type) {
      case 'init_state':
        handlers.onInitState?.(data);
        break;
      case 'users':
        handlers.onUsers?.(data);
        break;
      case 'bpmn_update':
        handlers.onBpmnUpdate?.(data);
        break;
      case 'lock':
        handlers.onLock?.(data);
        break;
      case 'unlock':
        handlers.onUnlock?.(data);
        break;
      case 'locks':
        handlers.onLocksSync?.(data);
        break;
    }
  };

  return ws;
}
