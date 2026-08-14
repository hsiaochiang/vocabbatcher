import {
  getAccent,
  getPreferHighQuality,
  type Accent,
} from './ttsPreferences';

const VOICES_WAIT_MS = 300;

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

export function speakEn(word: string): void {
  if (typeof window === 'undefined' || !window.speechSynthesis) return;

  window.speechSynthesis.cancel();
  const accent = getAccent();

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

export function speakZh(text: string): void {
  if (typeof window === 'undefined' || !window.speechSynthesis) return;

  window.speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'zh-TW';
  window.speechSynthesis.speak(utterance);
}
