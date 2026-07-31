import { useEffect, useState } from 'react';
import {
  onAuthStateChange,
  signInWithGoogle,
  signOut,
  completeRedirectSignIn,
  firebaseEnabled,
  type User,
} from '../services/auth';

export default function UserBadge() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const unsubscribe = onAuthStateChange(setUser);
    completeRedirectSignIn().catch((err) => {
      console.error('Google 登入失敗:', err);
      setError('登入失敗，請再試一次');
    });
    return unsubscribe;
  }, []);

  if (!firebaseEnabled) return null;

  const handleSignIn = async () => {
    setError(null);
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (err) {
      console.error('Google 登入失敗:', err);
      setError('登入失敗，請再試一次');
      setLoading(false);
    }
  };

  const handleSignOut = async () => {
    setLoading(true);
    try {
      await signOut();
    } finally {
      setLoading(false);
    }
  };

  if (user) {
    return (
      <div className="flex items-center gap-2">
        {user.photoURL && (
          <img
            src={user.photoURL}
            alt={user.displayName ?? '使用者頭像'}
            className="h-8 w-8 rounded-full"
            referrerPolicy="no-referrer"
          />
        )}
        <span className="max-w-[6rem] truncate text-sm text-gray-700">
          {user.displayName}
        </span>
        <button
          type="button"
          onClick={handleSignOut}
          disabled={loading}
          className="min-h-[44px] rounded-full bg-gray-100 px-3 py-2 text-sm font-medium text-gray-600 hover:bg-gray-200 disabled:opacity-50"
        >
          登出
        </button>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-end gap-1">
      <button
        type="button"
        onClick={handleSignIn}
        disabled={loading}
        className="min-h-[44px] rounded-full bg-primary/10 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/20 disabled:opacity-50"
      >
        使用 Google 登入
      </button>
      {error && <span className="text-xs text-red-500">{error}</span>}
    </div>
  );
}
