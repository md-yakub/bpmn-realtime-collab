import { LockList } from './LockList';

export function Sidebar({ locks, users }: any) {
  return (
    <aside className="sidebar">
      <h2>Locks</h2>
      <LockList locks={locks} users={users} />
    </aside>
  );
}
