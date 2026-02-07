import React, { useState, useRef, useEffect, useImperativeHandle, forwardRef } from 'react';
import { Search, Loader2, Mic, MicOff } from 'lucide-react';

const PLACEHOLDERS = [
  "e.g. Who won Wimbledon 2023?",
  "e.g. Federer vs Nadal on clay",
  "e.g. Top 10 players in 2024",
  "e.g. Roger Federer vs Nadal stats",
];

const getSpeechRecognition = (): (new () => SpeechRecognition) | null => {
  if (typeof window === 'undefined') return null;
  return window.SpeechRecognition ?? (window as unknown as { webkitSpeechRecognition: typeof SpeechRecognition }).webkitSpeechRecognition ?? null;
};

export interface SearchPanelRef {
  focus: () => void;
}

interface SearchPanelProps {
  onQuerySubmit: (query: string) => void;
  disabled?: boolean;
  value: string;
  onChange: (value: string) => void;
}

export const SearchPanel = forwardRef<SearchPanelRef, SearchPanelProps>(function SearchPanel({
  onQuerySubmit,
  disabled = false,
  value,
  onChange
}, ref) {
  const [isListening, setIsListening] = useState(false);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useImperativeHandle(ref, () => ({
    focus: () => inputRef.current?.focus(),
  }), []);

  useEffect(() => {
    const id = setInterval(() => {
      setPlaceholderIndex((i) => (i + 1) % PLACEHOLDERS.length);
    }, 4000);
    return () => clearInterval(id);
  }, []);

  const SpeechRecognitionClass = getSpeechRecognition();
  const speechSupported = SpeechRecognitionClass !== null;

  useEffect(() => {
    if (!SpeechRecognitionClass) return;
    const recognition = new SpeechRecognitionClass();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';
    recognition.maxAlternatives = 1;

    recognition.onresult = (ev: SpeechRecognitionEvent) => {
      const result = ev.results[ev.resultIndex];
      const transcript = result[0]?.transcript?.trim() ?? '';
      if (transcript) {
        onChangeRef.current(transcript);
      }
      setIsListening(false);
    };

    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => setIsListening(false);

    recognitionRef.current = recognition;
    return () => {
      recognitionRef.current?.stop();
      recognitionRef.current = null;
    };
  }, [SpeechRecognitionClass]);

  const handleToggleMic = () => {
    if (!recognitionRef.current || disabled) return;
    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      try {
        recognitionRef.current.start();
        setIsListening(true);
      } catch {
        setIsListening(false);
      }
    }
  };

  const handleSubmit = () => {
    if (value.trim() && !disabled) {
      onQuerySubmit(value.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSubmit();
      return;
    }
    if (e.key === 'Escape') {
      onChange('');
      inputRef.current?.blur();
      return;
    }
    if (e.key === '/' && !value) {
      e.preventDefault();
      inputRef.current?.focus();
    }
  };

  return (
    <div className="sticky top-0 z-30 -mx-8 px-8 pt-4 pb-4 -mt-4 bg-slate-950/0 backdrop-blur-sm mb-6 animate-in fade-in fill-mode-both delay-150 duration-700">
      <div className="group relative flex items-center bg-slate-800/50 backdrop-blur-xl border border-white/10 rounded-2xl shadow-2xl shadow-black/20 focus-within:ring-2 focus-within:ring-emerald-500/20 focus-within:border-emerald-500/50 transition-all duration-300">
        <div className="pl-6 pointer-events-none text-slate-400">
          <Search className="w-5 h-5 group-focus-within:text-emerald-400 transition-colors" />
        </div>
        <input
          ref={inputRef}
          className="w-full py-5 px-6 bg-transparent text-lg text-white focus:outline-none placeholder:text-slate-500"
          type="text"
          placeholder={PLACEHOLDERS[placeholderIndex]}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          aria-label="Ask a tennis question"
        />
        <div className="pr-2 flex items-center gap-1">
          {speechSupported && (
            <button
              type="button"
              onClick={handleToggleMic}
              disabled={disabled}
              title={isListening ? 'Stop listening' : 'Speak your query'}
              aria-label={isListening ? 'Stop listening' : 'Speak your query'}
              className={`p-3 rounded-xl transition-all duration-200 ${
                isListening
                  ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30 animate-pulse'
                  : 'text-slate-400 hover:text-emerald-400 hover:bg-white/5'
              } disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-transparent disabled:hover:text-slate-400`}
            >
              {isListening ? (
                <MicOff className="w-5 h-5" aria-hidden />
              ) : (
                <Mic className="w-5 h-5" aria-hidden />
              )}
            </button>
          )}
          <button
            className="bg-emerald-500 hover:bg-emerald-400 disabled:bg-slate-700 disabled:text-slate-500 text-slate-950 font-bold py-3 px-6 rounded-xl transition-all duration-300 active:scale-95 flex items-center gap-2 group shadow-lg shadow-emerald-500/20"
            onClick={handleSubmit}
            disabled={disabled || !value.trim()}
          >
            {disabled ? <Loader2 className="w-5 h-5 animate-spin" /> : <span>Analyze</span>}
          </button>
        </div>
      </div>
      {isListening && (
        <p className="text-sm text-slate-400 mt-2 px-2" role="status" aria-live="polite">
          Listening... speak your question, then click Analyze.
        </p>
      )}
      {speechSupported && !isListening && (
        <p className="text-xs text-slate-500 mt-2 px-2">Tip: Use the mic to speak your question</p>
      )}
    </div>
  );
});
