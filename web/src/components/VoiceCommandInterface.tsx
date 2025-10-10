import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Mic, 
  MicOff, 
  Volume2, 
  VolumeX, 
  Settings, 
  History,
  Zap,
  CheckCircle,
  AlertTriangle,
  Clock,
  Brain,
  Shield,
  Search,
  FileText,
  TestTube,
  Network
} from 'lucide-react';
import { voiceService, VoiceCommand } from '../services/voice';
import { toast } from 'react-hot-toast';

interface VoiceCommandInterfaceProps {
  onCommandProcessed?: (command: VoiceCommand) => void;
  compact?: boolean;
}

const VoiceCommandInterface: React.FC<VoiceCommandInterfaceProps> = ({ 
  onCommandProcessed,
  compact = false
}) => {
  const [isListening, setIsListening] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [commandHistory, setCommandHistory] = useState<VoiceCommand[]>([]);
  const [currentTranscript, setCurrentTranscript] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [voiceConfig, setVoiceConfig] = useState(voiceService.getConfig());
  const [isProcessing, setIsProcessing] = useState(false);

  const audioRef = useRef<HTMLAudioElement>(null);

  useEffect(() => {
    setIsSupported(voiceService.isVoiceSupported());
    
    // Listen for voice commands
    const handleVoiceCommand = (event: CustomEvent<VoiceCommand>) => {
      const command = event.detail;
      setCommandHistory(prev => [command, ...prev.slice(0, 9)]); // Keep last 10
      onCommandProcessed?.(command);
      
      if (command.processed) {
        toast.success('Command processed successfully');
        if (command.result?.feedback) {
          speak(command.result.feedback);
        }
      } else {
        toast.error('Failed to process command');
      }
    };

    // Listen for speech recognition events
    const handleSpeechStart = () => {
      setIsListening(true);
      setCurrentTranscript('');
    };

    const handleSpeechEnd = () => {
      setIsListening(false);
    };

    const handleSpeechResult = (event: any) => {
      setCurrentTranscript(event.detail || '');
    };

    window.addEventListener('voiceCommand', handleVoiceCommand as EventListener);
    window.addEventListener('speechStart', handleSpeechStart);
    window.addEventListener('speechEnd', handleSpeechEnd);
    window.addEventListener('speechResult', handleSpeechResult);

    return () => {
      window.removeEventListener('voiceCommand', handleVoiceCommand as EventListener);
      window.removeEventListener('speechStart', handleSpeechStart);
      window.removeEventListener('speechEnd', handleSpeechEnd);
      window.removeEventListener('speechResult', handleSpeechResult);
    };
  }, [onCommandProcessed]);

  const toggleListening = async () => {
    try {
      if (isListening) {
        voiceService.stopListening();
        setIsListening(false);
      } else {
        await voiceService.startListening();
        setIsListening(true);
      }
    } catch (error) {
      toast.error('Failed to toggle voice recognition');
      console.error('Voice recognition error:', error);
    }
  };

  const speak = (text: string) => {
    if (isSpeaking) {
      voiceService.stopSpeaking();
    }
    voiceService.speak(text, {
      onstart: () => setIsSpeaking(true),
      onend: () => setIsSpeaking(false),
      onerror: () => setIsSpeaking(false)
    });
  };

  const stopSpeaking = () => {
    voiceService.stopSpeaking();
    setIsSpeaking(false);
  };

  const getCommandIcon = (command: string) => {
    const lower = command.toLowerCase();
    if (lower.includes('scan') || lower.includes('security')) return <Shield className="w-4 h-4" />;
    if (lower.includes('analyze') || lower.includes('code')) return <Brain className="w-4 h-4" />;
    if (lower.includes('research') || lower.includes('investigate')) return <Search className="w-4 h-4" />;
    if (lower.includes('monitor') || lower.includes('status')) return <Network className="w-4 h-4" />;
    if (lower.includes('document') || lower.includes('report')) return <FileText className="w-4 h-4" />;
    if (lower.includes('test') || lower.includes('validate')) return <TestTube className="w-4 h-4" />;
    return <Zap className="w-4 h-4" />;
  };

  const getCommandSuggestions = () => {
    const patterns = voiceService.getCommandPatterns();
    return Object.entries(patterns).flatMap(([category, commands]) => 
      commands.map(cmd => ({ category, command: cmd }))
    );
  };

  const handleSuggestionClick = (command: string) => {
    speak(command);
    // Simulate command processing
    const mockCommand: VoiceCommand = {
      id: `voice_${Date.now()}`,
      command,
      confidence: 1.0,
      timestamp: Date.now(),
      processed: true,
      result: { message: 'Command executed successfully' }
    };
    setCommandHistory(prev => [mockCommand, ...prev.slice(0, 9)]);
    onCommandProcessed?.(mockCommand);
  };

  if (!isSupported) {
    return (
      <div className="text-center py-8">
        <AlertTriangle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <h3 className="text-lg font-semibold text-gray-400 mb-2">Voice Commands Not Supported</h3>
        <p className="text-gray-500">Your browser doesn't support speech recognition.</p>
      </div>
    );
  }

  if (compact) {
    return (
      <div className="flex items-center space-x-2">
        <button
          onClick={toggleListening}
          disabled={isProcessing}
          className={`p-3 rounded-full transition-all duration-200 ${
            isListening
              ? 'bg-red-500 hover:bg-red-600 text-white animate-pulse'
              : 'bg-blue-600 hover:bg-blue-700 text-white'
          } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
        >
          {isListening ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>
        
        {isSpeaking && (
          <button
            onClick={stopSpeaking}
            className="p-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-full transition-colors"
          >
            <VolumeX className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Main Voice Interface */}
      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-8 border border-blue-600/30">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-white mb-2">Voice Command Interface</h2>
          <p className="text-gray-400 mb-8">Control AMAS with natural language commands</p>
          
          {/* Voice Button */}
          <div className="relative mb-8">
            <motion.button
              onClick={toggleListening}
              disabled={isProcessing}
              className={`relative w-32 h-32 rounded-full transition-all duration-200 ${
                isListening
                  ? 'bg-red-500 hover:bg-red-600 text-white'
                  : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white'
              } ${isProcessing ? 'opacity-50 cursor-not-allowed' : ''}`}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <AnimatePresence>
                {isListening && (
                  <motion.div
                    className="absolute inset-0 rounded-full border-4 border-red-400"
                    animate={{ scale: [1, 1.2, 1] }}
                    transition={{ duration: 1, repeat: Infinity }}
                  />
                )}
              </AnimatePresence>
              
              {isListening ? (
                <MicOff className="w-12 h-12 mx-auto" />
              ) : (
                <Mic className="w-12 h-12 mx-auto" />
              )}
            </motion.button>
            
            <div className="mt-4">
              {isListening ? (
                <p className="text-red-400 font-medium">Listening... Speak now</p>
              ) : (
                <p className="text-gray-400">Click to start voice command</p>
              )}
            </div>
          </div>

          {/* Current Transcript */}
          {currentTranscript && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              className="bg-slate-700/50 rounded-lg p-4 mb-6"
            >
              <p className="text-white font-medium">You said:</p>
              <p className="text-gray-300 italic">"{currentTranscript}"</p>
            </motion.div>
          )}

          {/* Control Buttons */}
          <div className="flex justify-center space-x-4">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors"
            >
              <History className="w-4 h-4" />
              <span>History</span>
            </button>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="flex items-center space-x-2 px-4 py-2 bg-slate-700 text-gray-300 rounded-lg hover:bg-slate-600 transition-colors"
            >
              <Settings className="w-4 h-4" />
              <span>Settings</span>
            </button>
            
            {isSpeaking && (
              <button
                onClick={stopSpeaking}
                className="flex items-center space-x-2 px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
              >
                <VolumeX className="w-4 h-4" />
                <span>Stop Speaking</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Command Suggestions */}
      <div className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-green-600/30">
        <h3 className="text-lg font-semibold text-white mb-4">Try These Commands</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          {getCommandSuggestions().slice(0, 6).map((suggestion, index) => (
            <button
              key={index}
              onClick={() => handleSuggestionClick(suggestion.command)}
              className="flex items-center space-x-2 p-3 bg-slate-700/50 text-gray-300 rounded-lg hover:bg-slate-600/50 transition-colors text-left"
            >
              {getCommandIcon(suggestion.command)}
              <span className="text-sm">{suggestion.command}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Command History */}
      <AnimatePresence>
        {showHistory && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-purple-600/30"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Recent Commands</h3>
            <div className="space-y-3 max-h-64 overflow-y-auto">
              {commandHistory.map((command) => (
                <div key={command.id} className="flex items-center space-x-3 p-3 bg-slate-700/30 rounded-lg">
                  <div className="flex-shrink-0">
                    {command.processed ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <AlertTriangle className="w-4 h-4 text-red-500" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-white text-sm font-medium truncate">{command.command}</p>
                    <p className="text-gray-400 text-xs">
                      {new Date(command.timestamp).toLocaleTimeString()} • 
                      Confidence: {Math.round(command.confidence * 100)}%
                    </p>
                  </div>
                  <div className="flex-shrink-0">
                    {getCommandIcon(command.command)}
                  </div>
                </div>
              ))}
              {commandHistory.length === 0 && (
                <p className="text-gray-400 text-center py-4">No commands yet</p>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Settings */}
      <AnimatePresence>
        {showSettings && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="bg-gradient-to-br from-slate-800/50 to-slate-900/50 rounded-xl p-6 border border-yellow-600/30"
          >
            <h3 className="text-lg font-semibold text-white mb-4">Voice Settings</h3>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Language
                </label>
                <select
                  value={voiceConfig.language}
                  onChange={(e) => {
                    const newConfig = { ...voiceConfig, language: e.target.value };
                    setVoiceConfig(newConfig);
                    voiceService.setConfig(newConfig);
                  }}
                  className="w-full px-3 py-2 bg-slate-700 text-white rounded-lg border border-gray-600"
                >
                  {voiceService.getAvailableLanguages().map(lang => (
                    <option key={lang} value={lang}>{lang}</option>
                  ))}
                </select>
              </div>
              
              <div className="flex items-center space-x-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={voiceConfig.continuous}
                    onChange={(e) => {
                      const newConfig = { ...voiceConfig, continuous: e.target.checked };
                      setVoiceConfig(newConfig);
                      voiceService.setConfig(newConfig);
                    }}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-300">Continuous listening</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={voiceConfig.interimResults}
                    onChange={(e) => {
                      const newConfig = { ...voiceConfig, interimResults: e.target.checked };
                      setVoiceConfig(newConfig);
                      voiceService.setConfig(newConfig);
                    }}
                    className="rounded"
                  />
                  <span className="text-sm text-gray-300">Show interim results</span>
                </label>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default VoiceCommandInterface;