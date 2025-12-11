import { useEffect } from 'react';

import { WS_URL } from './config/constants';
import { useWebSocket } from './hooks/useWebSocket';
import { useBpmnModeler } from './hooks/useBpmnModeler';
import { Header } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { Canvas } from './components/Canvas';

export default function App() {
  const { init, send, connected, users, locks, revision, yourId, initialXml } =
    useWebSocket(WS_URL);

  const { containerRef } = useBpmnModeler(initialXml, send, yourId, locks);

  useEffect(() => {
    init();
  }, []);

  return (
    <div className="app-root">
      <Header connected={connected} users={users} revision={revision} />

      <main className="main-layout">
        <Canvas containerRef={containerRef} />
        <Sidebar locks={locks} users={users} />
      </main>
    </div>
  );
}
