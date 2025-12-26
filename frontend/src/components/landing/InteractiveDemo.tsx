import { useState } from 'react';
import { Play, Terminal, Copy, Check } from 'lucide-react';
import { executeDemo, type DemoResponse } from '@/lib/api';

const demoCommands = [
  { value: 'spawn-agent', label: 'Spawn Agent', description: 'Create a new agent instance' },
  { value: 'execute-task', label: 'Execute Task', description: 'Run a task on an agent' },
  { value: 'query-database', label: 'Query Database', description: 'Execute a database query' },
  { value: 'check-health', label: 'Health Check', description: 'Check system health status' },
  { value: 'list-agents', label: 'List Agents', description: 'Show all active agents' },
];

export default function InteractiveDemo() {
  const [selectedCommand, setSelectedCommand] = useState(demoCommands[0].value);
  const [output, setOutput] = useState<string>('');
  const [executing, setExecuting] = useState(false);
  const [copied, setCopied] = useState(false);

  const handleExecute = async () => {
    setExecuting(true);
    setOutput('');
    
    try {
      const result: DemoResponse = await executeDemo(selectedCommand);
      setOutput(result.output);
    } catch (error) {
      setOutput(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setExecuting(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(output);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <section id="demo" className="py-20 px-6 bg-gray-50 dark:bg-gray-900/50">
      <div className="container-custom">
        <div className="section-header text-center">
          <h2 className="section-title">Interactive Demo</h2>
          <p className="section-subtitle mx-auto">
            Try out AMAS commands in real-time and see how agents respond
          </p>
        </div>

        <div className="max-w-4xl mx-auto">
          <div className="card">
            {/* Command Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium mb-3">Select a command to execute:</label>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
                {demoCommands.map((cmd) => (
                  <button
                    key={cmd.value}
                    onClick={() => setSelectedCommand(cmd.value)}
                    className={`p-3 rounded-lg border-2 text-left transition-all ${
                      selectedCommand === cmd.value
                        ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20'
                        : 'border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-700'
                    }`}
                  >
                    <div className="font-medium text-sm mb-1">{cmd.label}</div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{cmd.description}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Execute Button */}
            <div className="mb-6">
              <button
                onClick={handleExecute}
                disabled={executing}
                className="btn-primary w-full flex items-center justify-center gap-2"
              >
                {executing ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                    Executing...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4" />
                    Execute Command
                  </>
                )}
              </button>
            </div>

            {/* Output Terminal */}
            <div className="relative">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                  <span className="text-sm font-medium">Output</span>
                </div>
                {output && (
                  <button
                    onClick={handleCopy}
                    className="text-sm text-gray-600 dark:text-gray-400 hover:text-primary-500 flex items-center gap-2"
                  >
                    {copied ? (
                      <>
                        <Check className="w-4 h-4" />
                        Copied!
                      </>
                    ) : (
                      <>
                        <Copy className="w-4 h-4" />
                        Copy
                      </>
                    )}
                  </button>
                )}
              </div>
              <div className="bg-charcoal dark:bg-black rounded-lg p-4 min-h-[300px] max-h-[400px] overflow-auto font-mono text-sm">
                {executing ? (
                  <div className="flex items-center gap-2 text-green-400">
                    <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                    Executing command...
                  </div>
                ) : output ? (
                  <pre className="text-green-400 whitespace-pre-wrap">{output}</pre>
                ) : (
                  <div className="text-gray-500 italic">
                    Click "Execute Command" to see the output here...
                  </div>
                )}
              </div>
            </div>

            {/* Info Box */}
            <div className="mt-6 p-4 rounded-lg bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800">
              <p className="text-sm text-blue-900 dark:text-blue-200">
                <strong>Note:</strong> This demo uses simulated data. In production, these commands would interact with your actual agent systems.
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}