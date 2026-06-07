import { useState, useEffect } from 'react';
import { NavLink, Outlet, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Receipt, UserCog, LogOut, ShieldCheck, User } from 'lucide-react';
import './Layout.css';

const navItems = [
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/log-expense', label: 'Log Expense', icon: Receipt },
  { to: '/profile', label: 'Profile & Settings', icon: UserCog },
];

const pageNames = {
  '/dashboard': 'Dashboard',
  '/log-expense': 'Log',
  '/profile': 'Profile',
};

export default function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(JSON.parse(localStorage.getItem('user') || '{}'));

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  useEffect(() => {
    const handleUserUpdated = () => {
      setUser(JSON.parse(localStorage.getItem('user') || '{}'));
    };

    window.addEventListener('userUpdated', handleUserUpdated);
    return () => window.removeEventListener('userUpdated', handleUserUpdated);
  }, []);


  const currentPage = pageNames[location.pathname] || 'Dashboard';

  return (
    <div className="layout">
      {/* Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="sidebar-brand-icon">
            <ShieldCheck />
          </div>
          <div className="sidebar-brand-text">AI Expense<br />Tracker</div>
        </div>

        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? 'active' : ''}`
              }
            >
              <item.icon />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-logout" onClick={handleLogout}>
            <LogOut />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Top Bar */}
      <header className="topbar">
        <div className="topbar-title">
          Active Portal: <span>{currentPage}</span>
        </div>
        <div className="topbar-actions">
          <div className="topbar-user">
            <User />
            {user.full_name || 'User'}
          </div>
          <button className="topbar-logout" onClick={handleLogout}>
            <LogOut />
            Logout
          </button>
        </div>
      </header>

      {/* Page Content */}
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
}
