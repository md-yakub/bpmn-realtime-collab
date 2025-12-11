export function Header({ connected, users, revision }: any) {
  return (
    <header className="app-header">
      <div className="app-title">
        <h1>BPMN Realtime Collab</h1>
        <span className={`status-dot ${connected ? 'online' : 'offline'}`} />
        <span className="status-text">{connected ? 'Connected' : 'Disconnected'}</span>
      </div>

      <div className="header-right">
        <div className="users-badge">
          <strong>Online:</strong>
          {users.map((u: any) => (
            <span key={u.id} className="user-pill">
              {u.name}
            </span>
          ))}
        </div>

        <div className="header-meta">
          <span>Revision #{revision}</span>
        </div>
      </div>
    </header>
  );
}
