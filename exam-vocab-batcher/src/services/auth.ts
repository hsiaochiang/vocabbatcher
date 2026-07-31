import {
  GoogleAuthProvider,
  onAuthStateChanged,
  signInWithPopup,
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

export async function signInWithGoogle(): Promise<User | null> {
  if (!auth) return null;
  const result = await signInWithPopup(auth, googleProvider);
  await ensureUserDoc(result.user);
  return result.user;
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
