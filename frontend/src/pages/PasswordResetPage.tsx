import { FormEvent, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { authApi } from '../api/auth.api';

const fieldClassName = 'w-full rounded-xl border border-[#d7e3e8] bg-white/75 px-4 py-3 text-[#172033] outline-none transition focus:border-[#42cdb3] focus:ring-4 focus:ring-[#42cdb3]/15';

export const PasswordResetPage = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const token = searchParams.get('token');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmation, setConfirmation] = useState('');
  const [message, setMessage] = useState('');
  const [testResetUrl, setTestResetUrl] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setMessage('');
    setError('');
    setSubmitting(true);

    try {
      if (token) {
        const response = await authApi.resetPassword({
          token,
          new_password: password,
          confirm_password: confirmation,
        });
        setMessage(response.message || 'Password reset successfully.');
        window.setTimeout(() => navigate('/login'), 1200);
      } else {
        const response = await authApi.requestPasswordReset(email);
        setTestResetUrl(response.data?.reset_url || '');
        setMessage(response.message || 'If an active account matches that email, a reset link will be sent.');
      }
    } catch (requestError: any) {
      setError(requestError.response?.data?.detail || 'Password reset request failed.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="workspace-grid relative flex min-h-screen items-center justify-center overflow-hidden bg-[#f4f7fb] px-4 py-10">
      <div className="page-enter relative w-full max-w-md">
        <div className="glass-panel rounded-[2rem] p-8 sm:p-10">
          <p className="mb-2 text-sm font-bold uppercase tracking-[0.18em] text-[#e2775f]">Account recovery</p>
          <h1 className="text-3xl font-black text-[#123c52]">
            {token ? 'Choose a new password' : 'Reset your password'}
          </h1>
          <form onSubmit={handleSubmit} className="mt-7 space-y-5">
            {token ? (
              <>
                <div>
                  <label htmlFor="new-password" className="mb-2 block text-sm font-bold text-[#315469]">New password</label>
                  <input id="new-password" type="password" minLength={8} maxLength={100} autoComplete="new-password" required value={password} onChange={(event) => setPassword(event.target.value)} className={fieldClassName} />
                </div>
                <div>
                  <label htmlFor="confirm-password" className="mb-2 block text-sm font-bold text-[#315469]">Confirm new password</label>
                  <input id="confirm-password" type="password" minLength={8} maxLength={100} autoComplete="new-password" required value={confirmation} onChange={(event) => setConfirmation(event.target.value)} className={fieldClassName} />
                </div>
              </>
            ) : (
              <div>
                <label htmlFor="recovery-email" className="mb-2 block text-sm font-bold text-[#315469]">Email</label>
                <input id="recovery-email" type="email" autoComplete="email" required value={email} onChange={(event) => setEmail(event.target.value)} className={fieldClassName} placeholder="you@example.com" />
              </div>
            )}
            {error && <p role="alert" className="rounded-xl border border-[#f4b4a7] bg-[#fff0ed] px-4 py-3 text-sm font-medium text-[#a74838]">{error}</p>}
            {message && <p role="status" className="rounded-xl border border-[#9de4d4] bg-[#e9faf5] px-4 py-3 text-sm font-medium text-[#176b5d]">{message}</p>}
            {testResetUrl && (
              <a href={testResetUrl} className="block break-all text-sm font-bold text-[#167d70] underline">
                Open password reset link
              </a>
            )}
            <button type="submit" disabled={submitting} className="w-full rounded-xl bg-[#123c52] px-4 py-3 font-bold text-white transition hover:bg-[#1b536c] disabled:opacity-50">
              {submitting ? 'Please wait...' : token ? 'Set new password' : 'Send reset link'}
            </button>
          </form>
          <p className="mt-6 text-center text-sm text-[#557083]">
            <Link to="/login" className="font-bold text-[#167d70] hover:text-[#e2775f]">Back to sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
};