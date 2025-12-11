export interface Canvas {
  zoom(level: number | string): void;
  addMarker(id: string, marker: string): void;
  removeMarker(id: string, marker: string): void;
}

export interface ElementRegistry {
  get(id: string): { id: string } | undefined;
  getAll(): { id: string }[];
}

export interface Overlays {
  add(
    elementId: string,
    type: string,
    config: {
      position: {
        top?: number;
        right?: number;
        left?: number;
        bottom?: number;
      };
      html: HTMLElement;
    },
  ): void;

  remove(filter: { type?: string; element?: string }): void;
}

export interface EventBus {
  on(event: string, callback: (event: any) => void): void;
}
