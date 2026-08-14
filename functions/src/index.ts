import { TextToSpeechClient } from '@google-cloud/text-to-speech';
import { HttpsError, onCall } from 'firebase-functions/v2/https';

type SupportedLang = 'en-US' | 'en-GB';

const MAX_TEXT_LENGTH = 200;
const SUPPORTED_LANGS = new Set<SupportedLang>(['en-US', 'en-GB']);
let ttsClient: TextToSpeechClient | undefined;

function getTtsClient(): TextToSpeechClient {
  ttsClient ??= new TextToSpeechClient();
  return ttsClient;
}

function parseText(value: unknown): string {
  if (typeof value !== 'string') {
    throw new HttpsError('invalid-argument', 'text must be a string.');
  }

  const text = value.trim();
  if (!text) {
    throw new HttpsError('invalid-argument', 'text is required.');
  }
  if (text.length > MAX_TEXT_LENGTH) {
    throw new HttpsError(
      'invalid-argument',
      `text must be ${MAX_TEXT_LENGTH} characters or fewer.`,
    );
  }

  return text;
}

function parseLang(value: unknown): SupportedLang {
  if (typeof value !== 'string' || !SUPPORTED_LANGS.has(value as SupportedLang)) {
    throw new HttpsError(
      'invalid-argument',
      'lang must be either en-US or en-GB.',
    );
  }

  return value as SupportedLang;
}

export const synthesizeSpeech = onCall({ region: 'us-central1' }, async (request) => {
  const text = parseText(request.data?.text);
  const lang = parseLang(request.data?.lang);

  const [response] = await getTtsClient().synthesizeSpeech({
    input: { text },
    voice: {
      languageCode: lang,
      ssmlGender: 'NEUTRAL',
    },
    audioConfig: {
      audioEncoding: 'MP3',
    },
  });

  const audioContent = response.audioContent;
  if (!audioContent) {
    throw new HttpsError('internal', 'Text-to-Speech returned empty audio.');
  }

  const audioBase64 =
    typeof audioContent === 'string'
      ? audioContent
      : Buffer.from(audioContent).toString('base64');

  return { audioBase64 };
});
