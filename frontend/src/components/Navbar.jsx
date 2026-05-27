import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/components.css';

function Navbar() {
  const { user, isAuthenticated, logout } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const navigate = useNavigate();

  const handleLogout = () => {
    setMobileOpen(false);
    logout();
  };

  const handleNavigate = (path) => {
    setMobileOpen(false);
    navigate(path);
  };

  const userInitial = user?.full_name
    ? user.full_name.charAt(0).toUpperCase()
    : user?.email?.charAt(0).toUpperCase() || '?';

  return (
    <nav className="navbar" role="navigation" aria-label="Main navigation">
      <div className="navbar-inner">
        <Link to="/" className="navbar-logo" id="navbar-logo">
          <span className="navbar-logo-icon">💓</span>
          <span className="navbar-logo-text">HeartGuard</span>
        </Link>

        {/* Desktop links */}
        <div className="navbar-links">
          {isAuthenticated ? (
            <div className="navbar-user">
              <div className="navbar-user-avatar" title={user?.full_name || user?.email}>
                {userInitial}
              </div>
              <span className="navbar-user-name">
                {user?.full_name || user?.email}
              </span>
              <Link to="/dashboard" className="navbar-link" id="nav-dashboard">
                Dashboard
              </Link>
              <Link to="/assess" className="navbar-link" id="nav-assess">
                New Assessment
              </Link>
              <button
                className="navbar-link"
                id="nav-logout"
                onClick={handleLogout}
                type="button"
              >
                Logout
              </button>
            </div>
          ) : (
            <>
              <Link to="/login" className="navbar-link" id="nav-login">
                Login
              </Link>
              <Link to="/register" id="nav-register">
                <button className="btn-primary" type="button" style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
                  Get Started
                </button>
              </Link>
            </>
          )}
        </div>

        {/* Mobile hamburger */}
        <button
          className="navbar-hamburger"
          id="navbar-hamburger"
          onClick={() => setMobileOpen((prev) => !prev)}
          aria-label="Toggle menu"
          type="button"
        >
          {mobileOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Mobile menu */}
      <div className={`navbar-mobile-menu ${mobileOpen ? 'open' : ''}`}>
        {isAuthenticated ? (
          <>
            <div className="navbar-user-name" style={{ marginBottom: '8px' }}>
              {user?.full_name || user?.email}
            </div>
            <button
              className="navbar-link"
              id="nav-mobile-dashboard"
              onClick={() => handleNavigate('/dashboard')}
              type="button"
            >
              Dashboard
            </button>
            <button
              className="navbar-link"
              id="nav-mobile-assess"
              onClick={() => handleNavigate('/assess')}
              type="button"
            >
              New Assessment
            </button>
            <button
              className="navbar-link"
              id="nav-mobile-logout"
              onClick={handleLogout}
              type="button"
            >
              Logout
            </button>
          </>
        ) : (
          <>
            <button
              className="navbar-link"
              id="nav-mobile-login"
              onClick={() => handleNavigate('/login')}
              type="button"
            >
              Login
            </button>
            <button
              className="navbar-link"
              id="nav-mobile-register"
              onClick={() => handleNavigate('/register')}
              type="button"
            >
              Register
            </button>
          </>
        )}
      </div>
    </nav>
  );
}

export default Navbar;
