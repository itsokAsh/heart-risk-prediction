import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../styles/auth.css';

function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setError('');
    try {
      await register(email, password, fullName);
      navigate('/dashboard');
    } catch (err) {
      setError(err.response?.data?.detail || 'Unable to create account');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <main className="page auth-page">
      <div className="auth-card">
        <div className="auth-header">
          <p className="eyebrow">Create your profile</p>
          <h1>Start with HeartGuard</h1>
          <p>Save assessments and access reports anytime.</p>
        </div>

        {error && <div className="error-banner">{error}</div>}

        <form className="auth-form" onSubmit={handleSubmit}>
          <label className="form-label" htmlFor="register-name">Full name</label>
          <input
            id="register-name"
            className="input-field"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Jordan Lee"
            required
          />

          <label className="form-label" htmlFor="register-email">Email</label>
          <input
            id="register-email"
            className="input-field"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="you@example.com"
            required
          />

          <label className="form-label" htmlFor="register-password">Password</label>
          <input
            id="register-password"
            className="input-field"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Minimum 8 characters"
            minLength={8}
            required
          />

          <button className="btn-primary" type="submit" disabled={submitting}>
            {submitting ? 'Creating account…' : 'Create account'}
          </button>
        </form>

        <p className="auth-footer">
          Already have an account? <Link to="/login">Sign in</Link>
        </p>
      </div>
    </main>
  );
}

export default Register;
