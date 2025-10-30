// Core domain types
export interface SystemHealth {
  status: 'healthy' | 'degraded' | 'offline' | 'unhealthy';
  timestamp: number;
  uptime: number;
  version?: string;
  services?: Record<string, string>;
  metrics?: Record<string, unknown>;
}

export interface PerformanceMetrics {
  throughput: number;
  latency: number;
  errorRate: number;
  timestamp: number;
}

// Voice API Types
export interface RecognitionResult {
  transcript: string;
  isFinal: boolean;
  confidence: number;
}

export interface VoiceServiceOptions {
  language?: string;
  continuous?: boolean;
  interimResults?: boolean;
  onResult?: (result: RecognitionResult) => void;
  onError?: (error: string) => void;
}

// Global type augmentation for browser APIs
declare global {
  interface Window {
    // Using any to avoid dependency on non-standardized SpeechRecognition TS types
    SpeechRecognition: any;
    webkitSpeechRecognition: any;
  }
}

export interface SpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: SpeechRecognitionResultList;
}

export interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

export interface SpeechRecognitionResult {
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
  isFinal: boolean;
}

export interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}
