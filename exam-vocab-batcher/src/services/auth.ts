import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithRedirect,
  getRedirectResult,
  signOut as firebaseSignOut,
  type User,
} from 'firebase/auth';
import { doc, getDoc, setDoc, serverTimestamp } from 'firebase/firestore';
import { auth, db, firebaseEnabled } from './firebase';

const googleProvider = new GoogleAuthProvider();

async function ensureUserDoc(user: User): Promise<void> {
  if (!db) return;
  const ref = doc(db, 'users', user.uid);
  const snap = await getDoc(ref);
  if (!snap.exists()) {
    await setDoc(ref, {
      displayName: user.displayName ?? '',
      createdAt: serverTimestamp(),
    });
  }
}

export async function signInWithGoogle(): Promise<void> {
  if (!auth) return;
  // 手機瀏覽器(iOS Safari / Android Chrome)常封鎖或立刻關閉彈出視窗，
  // 改用整頁導向登入(signInWithRedirect)，登入完成後導回本頁再由
  // completeRedirectSignIn() 接住結果。
  await signInWithRedirect(auth, googleProvider);
}

export async function completeRedirectSignIn(): Promise<User | null> {
  if (!auth) return null;
  const result = await getRedirectResult(auth);
  if (result?.user) {
    await ensureUserDoc(result.user);
    return result.user;
  }
  return null;
}

export async function signOut(): Promise<void> {
  if (!auth) return;
  await firebaseSignOut(auth);
}

export function onAuthStateChange(
  callback: (user: User | null) => void,
): () => void {
  if (!auth) {
    callback(null);
    return () => {};
  }
  return onAuthStateChanged(auth, callback);
}

export { firebaseEnabled };
export type { User };
