export interface User {
  id: string;
  name: string;
}

export interface InitStateMessage {
  type: 'init_state';
  xml: string;
  revision: number;
  users: User[];
  locks: Record<string, string>;
  current_user_id: string;
}

export interface UsersMessage {
  type: 'users';
  users: User[];
}

export interface BpmnUpdateMessage {
  type: 'bpmn_update';
  xml: string;
  revision: number;
  from: string;
}

export interface LockMessage {
  type: 'lock';
  elementId: string;
  userId: string;
}

export interface UnlockMessage {
  type: 'unlock';
  elementId: string;
  userId: string;
}

export interface LocksSyncMessage {
  type: 'locks';
  locks: Record<string, string>;
}

export type IncomingMessage =
  | InitStateMessage
  | UsersMessage
  | BpmnUpdateMessage
  | LockMessage
  | UnlockMessage
  | LocksSyncMessage;

export type OutgoingMessage =
  | {
      type: 'bpmn_update';
      xml: string;
    }
  | {
      type: 'lock';
      elementId: string;
    }
  | {
      type: 'unlock';
      elementId: string;
    };
