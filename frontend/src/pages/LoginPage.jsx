import React, { useState } from 'react';
import { Lock, Mail, ArrowRight } from 'lucide-react';
import { api } from '../api/client';
import NoticeBridgeLogo from '../components/NoticeBridgeLogo';

export default function LoginPage({ setActivePage, onLoginSuccess }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const res = await api.login({ email, password });
      localStorage.setItem('nb_token', res.access_token);
      onLoginSuccess({
        id: res.user_id,
        email: res.email,
        full_name: res.full_name
      });
      setActivePage('dashboard');
    } catch (err) {
      setError(err.message || 'Login failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container" style={{ padding: '60px 24px', maxWidth: '460px' }}>
      <div className="sports-card" style={{ background: '#FFFFFF', padding: '32px' }}>
        <div style={{ textAlign: 'center', marginBottom: '24px' }}>
          <div style={{ display: 'inline-flex', marginBottom: '12px' }}>
            <NoticeBridgeLogo size={42} showWordmark={false} />
          </div>
          <h2 style={{ fontSize: '1.65rem', marginBottom: '4px', color: 'var(--text-primary)' }}>
            Sign In to NoticeBridge
          </h2>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
            Access your personalized transition simulations & financing models
          </p>
        </div>

        {error && (
          <div style={{
            background: 'var(--tradelearn-pink-light)',
            border: '1px solid var(--tradelearn-pink-border)',
            color: 'var(--tradelearn-pink-text)',
            padding: '10px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            marginBottom: '20px'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
              Work Email
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="email"
                required
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@company.com"
                style={{ paddingLeft: '38px' }}
              />
              <Mail size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <div style={{ marginBottom: '22px' }}>
            <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '5px' }}>
              Password
            </label>
            <div style={{ position: 'relative' }}>
              <input
                type="password"
                required
                className="form-input"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                style={{ paddingLeft: '38px' }}
              />
              <Lock size={16} color="var(--text-muted)" style={{ position: 'absolute', left: '12px', top: '13px' }} />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-volt"
            style={{ width: '100%', padding: '11px' }}
          >
            {loading ? 'Authenticating...' : 'Sign In'}
            <ArrowRight size={18} />
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Don't have an account?{' '}
          <span
            onClick={() => setActivePage('signup')}
            style={{ color: 'var(--parrot-green)', cursor: 'pointer', fontWeight: 700 }}
          >
            Create an Account
          </span>
        </div>
      </div>
    </div>
  );
}
