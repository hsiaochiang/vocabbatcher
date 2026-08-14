import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import UserBadge from '../components/UserBadge';
import { getVoicesAsync, speakEn } from '../services/tts';
import {
  getAccent,
  getPreferHighQuality,
  getUseCloudTts,
  setAccent,
  setPreferHighQuality,
  setUseCloudTts,
  type Accent,
} from '../services/ttsPreferences';

type VoiceMode = 'device' | 'quality' | 'cloud';

const ACCENT_OPTIONS: { value: Accent; label: string; description: string }[] = [
  {
    value: 'en-US',
    label: '美式發音',
    description: '偏向一般美國英語語音。',
  },
  {
    value: 'en-GB',
    label: '英式發音',
    description: '需要裝置或瀏覽器提供 en-GB 語音。',
  },
];

const VOICE_MODE_OPTIONS: {
  value: VoiceMode;
  label: string;
  description: string;
}[] = [
  {
    value: 'device',
    label: '裝置預設語音',
    description: '離線可用，使用目前瀏覽器或裝置提供的英文發音。',
  },
  {
    value: 'quality',
    label: '優先高品質裝置語音',
    description:
      '使用瀏覽器/裝置內建的網路語音（如果有），iPad/iPhone 可能沒有效果。',
  },
  {
    value: 'cloud',
    label: 'Google 雲端語音（最準，需要網路）',
    description:
      '每次播放都需要連網，音質最接近 Google Translate；網路不通時會自動改用裝置預設發音。',
  },
];

function getInitialVoiceMode(): VoiceMode {
  if (getUseCloudTts()) return 'cloud';
  if (getPreferHighQuality()) return 'quality';
  return 'device';
}

export default function SettingsPage() {
  const navigate = useNavigate();
  const [accent, setAccentState] = useState<Accent>(() => getAccent());
  const [voiceMode, setVoiceMode] = useState<VoiceMode>(() =>
    getInitialVoiceMode(),
  );
  const [checkingVoices, setCheckingVoices] = useState(true);
  const [hasBritishVoice, setHasBritishVoice] = useState(false);
  const canSpeak =
    typeof window !== 'undefined' &&
    (Boolean(window.speechSynthesis) || voiceMode === 'cloud');

  useEffect(() => {
    let cancelled = false;

    getVoicesAsync()
      .then((voices) => {
        if (cancelled) return;
        setHasBritishVoice(
          voices.some((voice) => voice.lang.toLowerCase() === 'en-gb'),
        );
        setCheckingVoices(false);
      })
      .catch(() => {
        if (cancelled) return;
        setHasBritishVoice(false);
        setCheckingVoices(false);
      });

    return () => {
      cancelled = true;
    };
  }, []);

  const handleAccentChange = (nextAccent: Accent) => {
    setAccent(nextAccent);
    setAccentState(nextAccent);
  };

  const handleVoiceModeChange = (nextMode: VoiceMode) => {
    setVoiceMode(nextMode);
    setUseCloudTts(nextMode === 'cloud');
    setPreferHighQuality(nextMode === 'quality');
  };

  return (
    <div className="flex min-h-screen flex-col bg-bg-light">
      <Header
        title="發音設定"
        onBack={() => navigate(-1)}
        rightSlot={<UserBadge />}
      />

      <main className="flex-1 px-4 pb-10 pt-4">
        <section className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div className="flex items-start justify-between gap-3">
            <div>
              <h2 className="text-base font-bold text-gray-900">英文發音模式</h2>
              <p className="mt-1 text-sm leading-6 text-gray-600">
                設定會套用到全站所有英文發音按鈕。
              </p>
            </div>
            <button
              type="button"
              onClick={() => speakEn('hello')}
              disabled={!canSpeak}
              className="inline-flex min-h-[44px] shrink-0 items-center justify-center gap-2 rounded-full bg-primary px-4 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary/90 disabled:cursor-not-allowed disabled:opacity-40"
            >
              <span className="material-symbols-outlined text-[20px]">
                volume_up
              </span>
              測試發音
            </button>
          </div>

          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {ACCENT_OPTIONS.map((option) => {
              const disabled =
                option.value === 'en-GB' && !checkingVoices && !hasBritishVoice;
              return (
                <button
                  key={option.value}
                  type="button"
                  onClick={() => handleAccentChange(option.value)}
                  disabled={disabled}
                  aria-pressed={accent === option.value}
                  className={`min-h-[104px] rounded-xl border p-4 text-left transition-colors ${
                    accent === option.value
                      ? 'border-primary bg-primary/5 text-primary'
                      : 'border-gray-200 bg-white text-gray-700 hover:border-primary/40 hover:bg-primary/5'
                  } ${disabled ? 'cursor-not-allowed opacity-50 hover:border-gray-200 hover:bg-white' : ''}`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="font-semibold">{option.label}</span>
                    <span className="material-symbols-outlined text-[22px]">
                      {accent === option.value
                        ? 'radio_button_checked'
                        : 'radio_button_unchecked'}
                    </span>
                  </div>
                  <p className="mt-2 text-sm leading-5 text-gray-600">
                    {option.description}
                  </p>
                </button>
              );
            })}
          </div>

          {!checkingVoices && !hasBritishVoice && (
            <p className="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-sm leading-6 text-amber-800">
              這台裝置目前沒有偵測到英式語音，所以英式發音選項暫時不可選。
            </p>
          )}
        </section>

        <section className="mt-4 rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
          <div>
            <h2 className="text-base font-bold text-gray-900">發音引擎</h2>
            <p className="mt-1 text-sm leading-6 text-gray-600">
              口音維持上方選擇，這裡決定英文按鈕用哪一種聲音來源。
            </p>
          </div>

          <div className="mt-4 grid gap-3">
            {VOICE_MODE_OPTIONS.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleVoiceModeChange(option.value)}
                aria-pressed={voiceMode === option.value}
                className={`min-h-[92px] rounded-xl border p-4 text-left transition-colors ${
                  voiceMode === option.value
                    ? 'border-primary bg-primary/5 text-primary'
                    : 'border-gray-200 bg-white text-gray-700 hover:border-primary/40 hover:bg-primary/5'
                }`}
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-semibold">{option.label}</span>
                  <span className="material-symbols-outlined text-[22px]">
                    {voiceMode === option.value
                      ? 'radio_button_checked'
                      : 'radio_button_unchecked'}
                  </span>
                </div>
                <p className="mt-2 text-sm leading-5 text-gray-600">
                  {option.description}
                </p>
              </button>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
