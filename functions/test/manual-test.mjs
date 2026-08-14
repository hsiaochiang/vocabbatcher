import { mkdir, writeFile } from 'node:fs/promises';
import { Buffer } from 'node:buffer';
import path from 'node:path';
import process from 'node:process';

const projectId = process.env.FIREBASE_PROJECT_ID ?? 'gen-lang-client-0930375434';
const region = process.env.FUNCTION_REGION ?? 'us-central1';
const functionName = 'synthesizeSpeech';
const endpoint =
  process.env.SYNTHESIZE_SPEECH_URL ??
  `https://${region}-${projectId}.cloudfunctions.net/${functionName}`;
const outputDir = path.resolve('test-output');
const outputPath = path.join(outputDir, 'synthesizeSpeech-en-US.mp3');

async function callCallable(data) {
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ data }),
  });
  const body = await response.json();
  return { status: response.status, body };
}

function isMp3(buffer) {
  const hasId3Header = buffer.subarray(0, 3).toString('ascii') === 'ID3';
  const hasFrameSync = buffer[0] === 0xff && (buffer[1] & 0xe0) === 0xe0;
  return hasId3Header || hasFrameSync;
}

async function runSuccessCase() {
  const { status, body } = await callCallable({
    text: 'enhance',
    lang: 'en-US',
  });

  if (status !== 200 || !body.result?.audioBase64) {
    throw new Error(
      `Expected successful callable result, got HTTP ${status}: ${JSON.stringify(body)}`,
    );
  }

  const audio = Buffer.from(body.result.audioBase64, 'base64');
  if (audio.length === 0) {
    throw new Error('Generated MP3 is empty.');
  }
  if (!isMp3(audio)) {
    throw new Error('Generated file does not look like an MP3.');
  }

  await mkdir(outputDir, { recursive: true });
  await writeFile(outputPath, audio);
  console.log(`success: wrote ${outputPath} (${audio.length} bytes)`);
}

async function runInvalidLangCase() {
  const { status, body } = await callCallable({
    text: 'enhance',
    lang: 'en-AU',
  });

  const errorStatus = body.error?.status;
  if (status < 400 || errorStatus !== 'INVALID_ARGUMENT') {
    throw new Error(
      `Expected invalid-argument error, got HTTP ${status}: ${JSON.stringify(body)}`,
    );
  }

  console.log(
    `invalid lang: rejected with ${errorStatus} (${body.error?.message ?? 'no message'})`,
  );
}

console.log(`calling ${endpoint}`);
await runSuccessCase();
await runInvalidLangCase();
