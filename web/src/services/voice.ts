import { apiService } from './api';

export interface VoiceCommand {
  id: string;
  command: string;
  confidence: number;
  timestamp: number;
  processed: boolean;
  result?: any;
}

export interface VoiceConfig {
  language: string;
  continuous: boolean;
  interimResults: boolean;
  maxAlternatives: number;
  grammars?: string[];
}

class VoiceService {
  private recognition: SpeechRecognition | null = null;
  private isListening: boolean = false;
  private isSupported: boolean = false;
  private config: VoiceConfig = {
    language: 'en-US',
    continuous: true,
    interimResults: true,
    maxAlternatives: 1,
  };

  constructor() {
    this.initializeSpeechRecognition();
  }

  private initializeSpeechRecognition(): void {
    if (typeof window !== 'undefined') {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      
      if (SpeechRecognition) {
        this.recognition = new SpeechRecognition();
        this.isSupported = true;
        this.setupRecognition();
      } else {
        console.warn('Speech recognition not supported in this browser');
        this.isSupported = false;
      }
    }
  }

  private setupRecognition(): void {
    if (!this.recognition) return;

    this.recognition.continuous = this.config.continuous;
    this.recognition.interimResults = this.config.interimResults;
    this.recognition.lang = this.config.language;
    this.recognition.maxAlternatives = this.config.maxAlternatives;

    this.recognition.onstart = () => {
      this.isListening = true;
      console.log('Voice recognition started');
    };

    this.recognition.onend = () => {
      this.isListening = false;
      console.log('Voice recognition ended');
    };

    this.recognition.onerror = (event) => {
      console.error('Voice recognition error:', event.error);
      this.isListening = false;
    };

    this.recognition.onresult = (event) => {
      this.handleRecognitionResult(event);
    };
  }

  private async handleRecognitionResult(event: SpeechRecognitionEvent): Promise<void> {
    const results = Array.from(event.results);
    const lastResult = results[results.length - 1];

    if (lastResult.isFinal) {
      const command = lastResult[0].transcript.trim();
      const confidence = lastResult[0].confidence;

      console.log('Voice command detected:', command, 'Confidence:', confidence);

      try {
        // Process the command through the API
        const result = await apiService.processVoiceCommand(command);
        
        // Create voice command record
        const voiceCommand: VoiceCommand = {
          id: `voice_${Date.now()}`,
          command,
          confidence,
          timestamp: Date.now(),
          processed: true,
          result,
        };

        // Emit event for UI updates
        this.emitVoiceCommand(voiceCommand);
      } catch (error) {
        console.error('Failed to process voice command:', error);
        
        const voiceCommand: VoiceCommand = {
          id: `voice_${Date.now()}`,
          command,
          confidence,
          timestamp: Date.now(),
          processed: false,
        };

        this.emitVoiceCommand(voiceCommand);
      }
    }
  }

  private emitVoiceCommand(command: VoiceCommand): void {
    // Dispatch custom event for components to listen to
    window.dispatchEvent(new CustomEvent('voiceCommand', { detail: command }));
  }

  public startListening(): Promise<void> {
    return new Promise((resolve, reject) => {
      if (!this.isSupported || !this.recognition) {
        reject(new Error('Speech recognition not supported'));
        return;
      }

      if (this.isListening) {
        reject(new Error('Already listening'));
        return;
      }

      try {
        this.recognition.start();
        resolve();
      } catch (error) {
        reject(error);
      }
    });
  }

  public stopListening(): void {
    if (this.recognition && this.isListening) {
      this.recognition.stop();
    }
  }

  public toggleListening(): Promise<void> {
    if (this.isListening) {
      this.stopListening();
      return Promise.resolve();
    } else {
      return this.startListening();
    }
  }

  public setConfig(config: Partial<VoiceConfig>): void {
    this.config = { ...this.config, ...config };
    if (this.recognition) {
      this.setupRecognition();
    }
  }

  public getConfig(): VoiceConfig {
    return { ...this.config };
  }

  public isVoiceSupported(): boolean {
    return this.isSupported;
  }

  public isCurrentlyListening(): boolean {
    return this.isListening;
  }

  public getAvailableLanguages(): string[] {
    return [
      'en-US',
      'en-GB',
      'es-ES',
      'fr-FR',
      'de-DE',
      'it-IT',
      'pt-BR',
      'ru-RU',
      'ja-JP',
      'ko-KR',
      'zh-CN',
    ];
  }

  // Voice command patterns for better recognition
  public getCommandPatterns(): Record<string, string[]> {
    return {
      'scan': [
        'scan for vulnerabilities',
        'perform security scan',
        'check security',
        'scan target',
      ],
      'analyze': [
        'analyze code quality',
        'check code',
        'review code',
        'analyze project',
      ],
      'research': [
        'research target',
        'gather intelligence',
        'investigate',
        'find information',
      ],
      'monitor': [
        'show system status',
        'display metrics',
        'check health',
        'monitor performance',
      ],
      'start': [
        'start agent',
        'activate agent',
        'begin task',
        'execute command',
      ],
      'stop': [
        'stop agent',
        'deactivate agent',
        'cancel task',
        'halt operation',
      ],
    };
  }

  // Text-to-Speech for feedback
  public speak(text: string, options?: SpeechSynthesisUtterance): void {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      
      if (options) {
        Object.assign(utterance, options);
      } else {
        utterance.rate = 0.9;
        utterance.pitch = 1;
        utterance.volume = 0.8;
      }

      window.speechSynthesis.speak(utterance);
    }
  }

  public stopSpeaking(): void {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }
  }
}

// Export singleton instance
export const voiceService = new VoiceService();
export default voiceService;

// Extend Window interface for TypeScript
declare global {
  interface Window {
    SpeechRecognition: typeof SpeechRecognition;
    webkitSpeechRecognition: typeof SpeechRecognition;
  }
}