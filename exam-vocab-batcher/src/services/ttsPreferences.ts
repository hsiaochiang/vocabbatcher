export type Accent = 'en-US' | 'en-GB';

const ACCENT_KEY = 'ttsAccent';
const PREFER_HIGH_QUALITY_KEY = 'ttsPreferHighQuality';
const USE_CLOUD_TTS_KEY = 'ttsUseCloudTts';
const DEFAULT_ACCENT: Accent = 'en-US';

function canUseStorage() {
  try {
    return typeof window !== 'undefined' && Boolean(window.localStorage);
  } catch {
    return false;
  }
}

export function getAccent(): Accent {
  if (!canUseStorage()) return DEFAULT_ACCENT;

  try {
    const value = window.localStorage.getItem(ACCENT_KEY);
    return value === 'en-GB' || value === 'en-US' ? value : DEFAULT_ACCENT;
  } catch {
    return DEFAULT_ACCENT;
  }
}

export function setAccent(accent: Accent): void {
  if (!canUseStorage()) return;

  try {
    window.localStorage.setItem(ACCENT_KEY, accent);
  } catch {
    // localStorage can be unavailable in private browsing or restricted contexts.
  }
}

export function getPreferHighQuality(): boolean {
  if (!canUseStorage()) return false;

  try {
    return window.localStorage.getItem(PREFER_HIGH_QUALITY_KEY) === 'true';
  } catch {
    return false;
  }
}

export function setPreferHighQuality(value: boolean): void {
  if (!canUseStorage()) return;

  try {
    window.localStorage.setItem(PREFER_HIGH_QUALITY_KEY, value ? 'true' : 'false');
  } catch {
    // localStorage can be unavailable in private browsing or restricted contexts.
  }
}

export function getUseCloudTts(): boolean {
  if (!canUseStorage()) return false;

  try {
    return window.localStorage.getItem(USE_CLOUD_TTS_KEY) === 'true';
  } catch {
    return false;
  }
}

export function setUseCloudTts(value: boolean): void {
  if (!canUseStorage()) return;

  try {
    window.localStorage.setItem(USE_CLOUD_TTS_KEY, value ? 'true' : 'false');
  } catch {
    // localStorage can be unavailable in private browsing or restricted contexts.
  }
}
