import React from 'react';
import { LogOut } from 'lucide-react';
import NoticeBridgeLogo from './NoticeBridgeLogo';

export default function Navbar({ activePage, setActivePage, user, onLogout }) {
  const handleNav = (page) => {
    setActivePage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleScrollTo = (sectionId) => {
    if (activePage !== 'landing') {
      setActivePage('landing');
      setTimeout(() => {
        const el = document.getElementById(sectionId);
        if (el) el.scrollIntoView({ behavior: 'smooth' });
      }, 50);
    } else {
      const el = document.getElementById(sectionId);
      if (el) el.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const landingNavItems = [
    { id: 'home', label: 'Home', action: () => { handleNav('landing'); } },
    { id: 'features', label: 'Features', action: () => handleScrollTo('features') },
    { id: 'how-it-works', label: 'How It Works', action: () => handleScrollTo('how-it-works') },
    { id: 'about', label: 'About', action: () => handleScrollTo('about') },
  ];

  const appNavItems = [
    { id: 'landing', label: '← Home', action: () => handleNav('landing') },
    { id: 'dashboard', label: 'Dashboard', action: () => handleNav('dashboard') },
    { id: 'current-job', label: 'Current Job', action: () => handleNav('current-job') },
    { id: 'new-offer', label: 'New Offer', action: () => handleNav('new-offer') },
    { id: 'notice-calc', label: 'Notice Calc', action: () => handleNav('notice-calc') },
    { id: 'buyout-calc', label: 'Buyout Calc', action: () => handleNav('buyout-calc') },
    { id: 'scenarios', label: 'Scenarios', action: () => handleNav('scenarios') },
    { id: 'results', label: 'Results', action: () => handleNav('results') },
  ];

  const currentNavItems = activePage === 'landing' ? landingNavItems : appNavItems;

  return (
    <header style={{
      background: '#FFFFFF',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      boxShadow: '0 1px 3px rgba(15, 23, 42, 0.03)'
    }}>
      <div className="container" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '70px'
      }}>
        {/* Logo: NB monogram where N and B connect through a bridge concept + NoticeBridge */}
        <div onClick={() => handleNav('landing')}>
          <NoticeBridgeLogo size={38} wordmarkSize="1.35rem" />
        </div>

        {/* Center Nav Links */}
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          {currentNavItems.map((item) => {
            const isActive = activePage === item.id || (activePage === 'landing' && item.id === 'home');
            return (
              <button
                key={item.id}
                onClick={item.action}
                style={{
                  background: 'transparent',
                  color: isActive ? '#0F172A' : '#64748B',
                  border: 'none',
                  padding: '8px 14px',
                  borderRadius: '6px',
                  fontFamily: 'var(--font-heading)',
                  fontWeight: isActive ? 700 : 500,
                  fontSize: '0.92rem',
                  cursor: 'pointer',
                  transition: 'color 0.15s ease'
                }}
                onMouseEnter={(e) => { e.currentTarget.style.color = '#0F172A'; }}
                onMouseLeave={(e) => { if (!isActive) e.currentTarget.style.color = '#64748B'; }}
              >
                {item.label}
              </button>
            );
          })}
        </nav>

        {/* Right Auth / Status */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              {activePage === 'landing' && (
                <button
                  onClick={() => handleNav('dashboard')}
                  className="btn-volt"
                  style={{ padding: '7px 16px', fontSize: '0.84rem' }}
                >
                  Dashboard
                </button>
              )}
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border-subtle)',
                padding: '6px 12px',
                borderRadius: '8px'
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: 'var(--parrot-green)'
                }} />
                <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  {user.full_name || user.name || user.email || 'My Account'}
                </span>
              </div>
              <button
                onClick={onLogout}
                className="btn-outline"
                style={{ padding: '6px 10px', fontSize: '0.8rem' }}
                title="Logout"
              >
                <LogOut size={14} />
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
              <button
                onClick={() => handleNav('login')}
                className="btn-outline"
                style={{ padding: '8px 18px', fontSize: '0.86rem', background: '#FFFFFF' }}
              >
                Login
              </button>
              <button
                onClick={() => handleNav('signup')}
                className="btn-volt"
                style={{ padding: '8px 18px', fontSize: '0.86rem' }}
              >
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
