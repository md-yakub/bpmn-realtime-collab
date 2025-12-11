export function LockList({ locks, users }: any) {
  return (
    <div className="locks-list">
      {Object.entries(locks).map(([id, uid]) => (
        <div key={id} className="lock-row">
          <span className="lock-icon">🔒</span>
          <span className="lock-label">{id}</span>
          <span className="lock-user">{users.find((u: any) => u.id === uid)?.name || uid}</span>
        </div>
      ))}
    </div>
  );
}
