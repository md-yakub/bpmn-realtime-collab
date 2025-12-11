import { useEffect, useRef, useCallback } from 'react';
import Modeler from 'bpmn-js/lib/Modeler';

import type {
  Canvas,
  ElementRegistry,
  EventBus,
  Overlays,
  SelectionChangedEvent,
} from '../types/bpmn-wrapper';

export function useBpmnModeler(
  initialXml: string | null,
  send: (data: unknown) => void,
  yourId: string | null,
  locks: Record<string, string>,
) {
  const containerRef = useRef<HTMLDivElement | null>(null);
  const modelerRef = useRef<Modeler | null>(null);
  const isImportingRef = useRef(false);
  const lockRenderTimeout = useRef<number | null>(null);

  useEffect(() => {
    if (!containerRef.current || modelerRef.current) return;

    const modeler = new Modeler({
      container: containerRef.current,
    });

    modelerRef.current = modeler;

    const eventBus = modeler.get('eventBus') as EventBus;

    eventBus.on('selection.changed', (e: SelectionChangedEvent) => {
      const selected = e.newSelection?.[0];

      const isElement =
        selected?.businessObject && !selected.businessObject.$type.includes('Process');

      const myLocked = Object.entries(locks)
        .filter(([, uid]) => uid === yourId)
        .map(([id]) => id);

      if (isElement) {
        const id = selected!.id;

        send({ type: 'lock', elementId: id });

        myLocked.forEach((prev) => prev !== id && send({ type: 'unlock', elementId: prev }));
      } else {
        myLocked.forEach((prev) => send({ type: 'unlock', elementId: prev }));
      }
    });

    eventBus.on('commandStack.changed', async () => {
      if (isImportingRef.current) return;
      const { xml } = await modeler.saveXML({ format: true });
      send({ type: 'bpmn_update', xml });
    });
  }, [locks, yourId, send]);

  useEffect(() => {
    if (!initialXml || !modelerRef.current) return;

    isImportingRef.current = true;

    modelerRef.current.importXML(initialXml).then(() => {
      isImportingRef.current = false;

      const canvas = modelerRef.current!.get('canvas') as Canvas;
      canvas.zoom('fit-viewport');

      scheduleRenderLocks();
    });
  }, [initialXml]);

  useEffect(() => {
    scheduleRenderLocks();
  }, [locks, yourId]);

  const scheduleRenderLocks = useCallback(() => {
    if (!modelerRef.current || !yourId) return;

    if (lockRenderTimeout.current !== null) {
      clearTimeout(lockRenderTimeout.current);
    }

    lockRenderTimeout.current = window.setTimeout(() => {
      renderLocks();
    }, 40);
  }, [yourId, locks]);

  const renderLocks = useCallback(() => {
    if (!modelerRef.current || isImportingRef.current || !yourId) return;

    const modeler = modelerRef.current;
    const overlays = modeler.get('overlays') as Overlays;
    const registry = modeler.get('elementRegistry') as ElementRegistry;
    const canvas = modeler.get('canvas') as Canvas;

    overlays.remove({ type: 'lock' });

    registry.getAll().forEach((el) => {
      canvas.removeMarker(el.id, 'locked-by-others');
    });

    Object.entries(locks).forEach(([elementId, uid]) => {
      if (uid === yourId) return;

      const element = registry.get(elementId);
      if (!element) return;

      const html = document.createElement('div');
      html.className = 'lock-overlay';
      html.textContent = '🔒';

      overlays.add(elementId, 'lock', {
        position: { top: -10, right: 0 },
        html,
      });

      canvas.addMarker(elementId, 'locked-by-others');
    });
  }, [locks, yourId]);

  return { containerRef };
}
