import { useEffect, useState } from 'react';
import {
  onAuthStateChange,
  signInWithGoogle,
  signOut,
  firebaseEnabled,
  type User,
} from '../services/auth';

export default function UserBadge() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const unsubscribe = onAuthStateChange(setUser);
    return unsubscribe;
  }, []);

  if (!firebaseEnabled) return null;

  const handleSignIn = async () => {
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (err) {
      console.error('Google 登入失敗:', err);
    } finally {
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
    <button
      type="button"
      onClick={handleSignIn}
      disabled={loading}
      className="min-h-[44px] rounded-full bg-primary/10 px-3 py-2 text-sm font-medium text-primary hover:bg-primary/20 disabled:opacity-50"
    >
      使用 Google 登入
    </button>
  );
}
