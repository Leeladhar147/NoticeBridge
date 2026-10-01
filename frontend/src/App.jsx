import React, { useState, useEffect } from 'react';
import TopNavigationLine from './components/TopNavigationLine';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import { api } from './api/client';

import LandingPage from './pages/LandingPage';
import LoginPage from './pages/LoginPage';
import SignupPage from './pages/SignupPage';
import DashboardPage from './pages/DashboardPage';
import CurrentEmploymentPage from './pages/CurrentEmploymentPage';
import NewOfferPage from './pages/NewOfferPage';
import NoticeCalculatorPage from './pages/NoticeCalculatorPage';
import BuyoutCalculatorPage from './pages/BuyoutCalculatorPage';
import ScenarioSimulatorPage from './pages/ScenarioSimulatorPage';
import ResultsPage from './pages/ResultsPage';

export default function App() {
  const [activePage, setActivePage] = useState('landing');
  const [user, setUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Restore authenticated session on initial mount
  useEffect(() => {
    const token = localStorage.getItem('nb_token');
    if (token) {
      api.getMe()
        .then((userData) => {
          setUser(userData);
        })
        .catch(() => {
          localStorage.removeItem('nb_token');
          setUser(null);
        })
        .finally(() => {
          setAuthLoading(false);
        });
    } else {
      setAuthLoading(false);
    }
  }, []);

  const handleLogout = async () => {
    try {
      await api.logout();
    } catch (e) {
      // Non-blocking logout cleanup
    }
    localStorage.removeItem('nb_token');
    setUser(null);
    setActivePage('landing');
  };

  const handleLoginSuccess = (userData) => {
    setUser(userData);
    setActivePage('dashboard');
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#FFFFFF' }}>
      {/* Top Navigation Line - Animates strictly on route navigation */}
      <TopNavigationLine activePage={activePage} />

      {/* Main Navbar */}
      <Navbar
        activePage={activePage}
        setActivePage={setActivePage}
        user={user}
        onLogout={handleLogout}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1 }}>
        {activePage === 'landing' && <LandingPage setActivePage={setActivePage} user={user} />}
        {activePage === 'login' && <LoginPage setActivePage={setActivePage} onLoginSuccess={handleLoginSuccess} />}
        {activePage === 'signup' && <SignupPage setActivePage={setActivePage} onLoginSuccess={handleLoginSuccess} />}
        {activePage === 'dashboard' && <DashboardPage setActivePage={setActivePage} user={user} />}
        {activePage === 'current-job' && <CurrentEmploymentPage setActivePage={setActivePage} user={user} />}
        {activePage === 'new-offer' && <NewOfferPage setActivePage={setActivePage} user={user} />}
        {activePage === 'notice-calc' && <NoticeCalculatorPage setActivePage={setActivePage} user={user} />}
        {activePage === 'buyout-calc' && <BuyoutCalculatorPage setActivePage={setActivePage} user={user} />}
        {activePage === 'scenarios' && <ScenarioSimulatorPage setActivePage={setActivePage} user={user} />}
        {activePage === 'results' && <ResultsPage setActivePage={setActivePage} user={user} />}
      </main>

      {/* Footer with Mandatory Disclaimer Banner */}
      <Footer />
    </div>
  );
}
