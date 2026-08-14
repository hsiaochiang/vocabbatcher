import { httpsCallable } from 'firebase/functions';
import { functions } from './firebase';
import {
  getAccent,
  getPreferHighQuality,
  getUseCloudTts,
  type Accent,
} from './ttsPreferences';

const VOICES_WAIT_MS = 300;
const CLOUD_TTS_TIMEOUT_MS = 7000;
const CLOUD_TTS_TEXT_LIMIT = 200;
const CLOUD_TTS_CACHE_PREFIX = 'cloudTtsAudio';

type SynthesizeSpeechResponse = {
  audioBase64: string;
};

let currentCloudAudio: HTMLAudioElement | null = null;

export function getVoicesAsync(): Promise<SpeechSynthesisVoice[]> {
  if (typeof window === 'undefined' || !window.speechSynthesis) {
    return Promise.resolve([]);
  }

  const voices = window.speechSynthesis.getVoices();
  if (voices.length > 0) {
    return Promise.resolve(voices);
  }

  return new Promise((resolve) => {
    let resolved = false;

    const finish = () => {
      if (resolved) return;
      resolved = true;
      window.clearTimeout(timer);
      window.speechSynthesis.removeEventListener('voiceschanged', finish);
      resolve(window.speechSynthesis.getVoices());
    };

    const timer = window.setTimeout(finish, VOICES_WAIT_MS);
    window.speechSynthesis.addEventListener('voiceschanged', finish, {
      once: true,
    });
  });
}

function chooseVoice(
  voices: SpeechSynthesisVoice[],
  lang: Accent | 'zh-TW',
): SpeechSynthesisVoice | undefined {
  const preferHighQuality = getPreferHighQuality();
  const normalizedLang = lang.toLowerCase();
  const exactMatches = voices.filter(
    (voice) => voice.lang.toLowerCase() === normalizedLang,
  );
  const candidates =
    exactMatches.length > 0
      ? exactMatches
      : voices.filter((voice) => voice.lang.toLowerCase().startsWith('en'));

  if (preferHighQuality) {
    const remoteVoice = candidates.find((voice) => voice.localService === false);
    if (remoteVoice) return remoteVoice;
  }

  return candidates[0];
}

function speakEnWithDeviceVoice(word: string, accent: Accent): void {
  void getVoicesAsync().then((voices) => {
    if (!window.speechSynthesis) return;
    const utterance = new SpeechSynthesisUtterance(word);
    const voice = chooseVoice(voices, accent);
    utterance.lang = accent;
    utterance.rate = 0.9;
    if (voice) {
      utterance.voice = voice;
    }
    window.speechSynthesis.speak(utterance);
  });
}

function stopCurrentEnglishAudio(): void {
  if (typeof window !== 'undefined' && window.speechSynthesis) {
    window.speechSynthesis.cancel();
  }

  if (!currentCloudAudio) return;

  currentCloudAudio.pause();
  currentCloudAudio.removeAttribute('src');
  currentCloudAudio.load();
  currentCloudAudio = null;
}

function getCloudTtsCacheKey(text: string, accent: Accent): string {
  return `${CLOUD_TTS_CACHE_PREFIX}:${accent}:${encodeURIComponent(text)}`;
}

function getCachedCloudAudio(cacheKey: string): string | null {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return null;
    return window.localStorage.getItem(cacheKey);
  } catch {
    return null;
  }
}

function setCachedCloudAudio(cacheKey: string, audioBase64: string): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) return;
    window.localStorage.setItem(cacheKey, audioBase64);
  } catch {
    // Best-effort cache only; playback must keep working if storage is full.
  }
}

function withTimeout<T>(promise: Promise<T>, timeoutMs: number): Promise<T> {
  return new Promise<T>((resolve, reject) => {
    const timer = window.setTimeout(() => {
      reject(new Error('Cloud TTS timed out'));
    }, timeoutMs);

    promise
      .then((value) => {
        window.clearTimeout(timer);
        resolve(value);
      })
      .catch((error: unknown) => {
        window.clearTimeout(timer);
        reject(error);
      });
  });
}

async function playCloudAudio(audioBase64: string): Promise<void> {
  const audio = new Audio(`data:audio/mp3;base64,${audioBase64}`);
  currentCloudAudio = audio;

  const playPromise = audio.play();
  if (playPromise) {
    await playPromise;
  }
}

async function speakEnWithCloudTts(
  word: string,
  accent: Accent,
): Promise<void> {
  if (!functions || word.trim().length === 0 || word.length > CLOUD_TTS_TEXT_LIMIT) {
    throw new Error('Cloud TTS unavailable for this text');
  }

  const cacheKey = getCloudTtsCacheKey(word, accent);
  const cachedAudio = getCachedCloudAudio(cacheKey);
  if (cachedAudio) {
    await playCloudAudio(cachedAudio);
    return;
  }

  const synthesizeSpeech = httpsCallable(functions, 'synthesizeSpeech');
  const result = await withTimeout(
    synthesizeSpeech({ text: word, lang: accent }),
    CLOUD_TTS_TIMEOUT_MS,
  );
  const data = result.data as Partial<SynthesizeSpeechResponse>;

  if (typeof data.audioBase64 !== 'string' || data.audioBase64.length === 0) {
    throw new Error('Cloud TTS returned no audio');
  }

  setCachedCloudAudio(cacheKey, data.audioBase64);
  await playCloudAudio(data.audioBase64);
}

export function speakEn(word: string): void {
  if (typeof window === 'undefined') return;

  stopCurrentEnglishAudio();
  const accent = getAccent();

  if (getUseCloudTts() && functions) {
    void speakEnWithCloudTts(word, accent).catch(() => {
      speakEnWithDeviceVoice(word, accent);
    });
    return;
  }

  speakEnWithDeviceVoice(word, accent);
}

export function speakZh(text: string): void {
  if (typeof window === 'undefined' || !window.speechSynthesis) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-TW';
  window.speechSynthesis.speak(utterance);
}
