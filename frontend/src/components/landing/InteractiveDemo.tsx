/**
 * Interactive Demo Component
 * 
 * SECURITY FEATURES (per AI audit):
 * - NO arbitrary code execution
 * - Input sanitization
 * - Output escaping
 * - Allow-listed commands only
 * - XSS prevention
 */

import { useState } from 'react';

// ============================================================================
// SECURITY: Allow-listed commands only (no eval!)
// ============================================================================
const ALLOWED_COMMANDS = {
  help: () => 'Available commands: help, status, metrics, ping',
  status: () => 'System status: ✅ All systems operational',
  metrics: () => 'Active agents: 12 | Tasks: 1543 | Success rate: 98.7%',
  ping: () => 'pong',
} as const;

type AllowedCommand = keyof typeof ALLOWED_COMMANDS;

// ============================================================================
// COMPONENT
// ============================================================================
export function InteractiveDemo() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState<string[]>(['👋 Welcome to AMAS Interactive Demo']);

  const handleCommand = (cmd: string) => {
    const trimmed = cmd.trim().toLowerCase();
    
    // SECURITY: Sanitize input (remove special characters)
    const sanitized = trimmed.replace(/[^a-z0-9\s-]/g, '');
    
    // Add command to output
    const newOutput = [...output, `$ ${sanitized}`];
    
    // SECURITY: Only execute allow-listed commands
    if (sanitized in ALLOWED_COMMANDS) {
      const result = ALLOWED_COMMANDS[sanitized as AllowedCommand]();
      newOutput.push(result);
    } else if (sanitized === '') {
      // Empty command - do nothing
    } else {
      newOutput.push(`❌ Command not found: ${sanitized}. Type 'help' for available commands.`);
    }
    
    setOutput(newOutput);
    setInput('');
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      handleCommand(input);
    }
  };

  return (
    <section className="py-16 bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-8 text-gray-900 dark:text-white">
            Try It Live
          </h2>
          
          {/* Terminal-style Demo */}
          <div className="bg-gray-900 rounded-lg shadow-xl p-6 font-mono text-sm">
            {/* Output Area */}
            <div className="mb-4 space-y-2 h-64 overflow-y-auto">
              {output.map((line, idx) => (
                <div 
                  key={idx} 
                  className={line.startsWith('$') ? 'text-green-400' : 'text-gray-300'}
                >
                  {/* SECURITY: React automatically escapes text - no XSS risk */}
                  {line}
                </div>
              ))}
            </div>
            
            {/* Input Area */}
            <div className="flex items-center space-x-2">
              <span className="text-green-400">$</span>
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1 bg-transparent text-white outline-none"
                placeholder="Type 'help' for commands..."
                autoComplete="off"
                spellCheck="false"
                maxLength={50} // SECURITY: Limit input length
              />
            </div>
          </div>
          
          {/* Help Text */}
          <p className="mt-4 text-center text-gray-600 dark:text-gray-400 text-sm">
            This is a safe, sandboxed demo. No actual system commands are executed.
          </p>
        </div>
      </div>
    </section>
  );
}
