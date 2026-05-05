import React, { useState, useEffect, useCallback, useRef } from 'react';
import './styles/globals.css';

const API_BASE = 'http://localhost:8000/api';

// ==================== MAIN APP ====================
function App() {
    // Connection state
    const [backendConnected, setBackendConnected] = useState(false);
    const [ollamaConnected, setOllamaConnected] = useState(false);
    const [status, setStatus] = useState('Connecting...');

    // UI state
    const [input, setInput] = useState('');
    const [messages, setMessages] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('chat');
    const [showSettings, setShowSettings] = useState(false);

    // Settings
    const [settings, setSettings] = useState({
        model: 'llama3.1:8b',
        voiceEnabled: true,
        autoSpeak: true
    });

    // Available models
    const [models, setModels] = useState([]);

    // Plugins
    const [plugins, setPlugins] = useState([]);
    const [pluginError, setPluginError] = useState(null);

    // Voice state - CONTINUOUS LISTENING
    const [isListening, setIsListening] = useState(false);
    const [voiceStatus, setVoiceStatus] = useState('');
    const recognitionRef = useRef(null);
    const isListeningRef = useRef(false);

    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // ==================== BACKEND CONNECTION ====================
    useEffect(() => {
        const checkBackend = async () => {
            try {
                const res = await fetch('http://localhost:8000/health', {
                    method: 'GET',
                    headers: { 'Accept': 'application/json' }
                });
                if (res.ok) {
                    const data = await res.json();
                    setBackendConnected(data.status === 'healthy');
                    setOllamaConnected(data.ollama === 'connected');
                    if (!isListening) {
                        setStatus(data.ollama === 'connected' ? 'Ready' : 'Ollama Disconnected');
                    }
                } else {
                    setBackendConnected(false);
                    setStatus('Backend Error');
                }
            } catch (err) {
                setBackendConnected(false);
                setOllamaConnected(false);
                setStatus('Backend Offline');
            }
        };

        checkBackend();
        const interval = setInterval(checkBackend, 10000);
        return () => clearInterval(interval);
    }, [isListening]);

    // ==================== LOAD MODELS ====================
    useEffect(() => {
        if (backendConnected) {
            fetch(`${API_BASE}/chat/models`)
                .then(res => res.json())
                .then(data => {
                    if (data.models) {
                        setModels(data.models.map(m => m.name));
                    }
                })
                .catch(err => console.error('Failed to load models:', err));
        }
    }, [backendConnected]);

    // ==================== LOAD PLUGINS ====================
    useEffect(() => {
        if (backendConnected) {
            loadPlugins();
        }
    }, [backendConnected]);

    const loadPlugins = async () => {
        try {
            setPluginError(null);
            const res = await fetch(`${API_BASE}/plugins/`);
            const data = await res.json();

            if (Array.isArray(data)) {
                setPlugins(data);
            } else if (data.plugins) {
                setPlugins(data.plugins);
            } else {
                setPlugins([]);
            }
        } catch (err) {
            console.error('Failed to load plugins:', err);
            setPluginError('Failed to connect to backend. Make sure the server is running.');
            setPlugins([]);
        }
    };

    // ==================== AUTO SCROLL ====================
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    // ==================== CHAT FUNCTION ====================
    const sendMessage = async (messageText = null) => {
        const textToSend = messageText || input.trim();
        if (!textToSend || isLoading) return;

        if (!messageText) setInput('');
        setIsLoading(true);
        setStatus('Thinking...');

        // Add user message
        setMessages(prev => [...prev, { role: 'user', content: textToSend }]);

        try {
            const response = await fetch(`${API_BASE}/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    model: settings.model,
                    prompt: textToSend
                })
            });

            const data = await response.json();

            if (data.response) {
                setMessages(prev => [...prev, {
                    role: 'assistant',
                    content: data.response,
                    model: data.model
                }]);

                // Speak response if auto-speak is enabled
                if (settings.autoSpeak && backendConnected) {
                    speakText(data.response);
                }

                setStatus(isListening ? '🎤 Listening...' : 'Ready');
            } else if (data.error) {
                setMessages(prev => [...prev, {
                    role: 'error',
                    content: data.error
                }]);
                setStatus('Error');
            }
        } catch (err) {
            setMessages(prev => [...prev, {
                role: 'error',
                content: `Connection error: ${err.message}`
            }]);
            setStatus('Error');
        } finally {
            setIsLoading(false);
        }
    };

    // ==================== TEXT TO SPEECH ====================
    const speakText = async (text) => {
        try {
            // Use backend TTS
            await fetch(`${API_BASE}/voice/speak`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ text, blocking: false })
            });
        } catch (err) {
            // Fallback to browser TTS
            if ('speechSynthesis' in window) {
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                utterance.pitch = 1.0;
                window.speechSynthesis.speak(utterance);
            }
        }
    };

    // ==================== SCREEN CAPTURE ====================
    const captureScreen = async () => {
        setStatus('Reading screen...');
        try {
            const res = await fetch(`${API_BASE}/screen/read`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({})
            });
            const data = await res.json();

            if (data.text) {
                const screenContent = data.text.substring(0, 500) + (data.text.length > 500 ? '...' : '');
                setMessages(prev => [...prev, {
                    role: 'system',
                    content: `📸 Screen captured: ${data.word_count} words extracted\n\n${screenContent}`
                }]);
                setStatus(isListening ? '🎤 Listening...' : 'Screen captured!');
            } else {
                setStatus('No text found on screen');
            }
        } catch (err) {
            setStatus('Screen capture failed');
        }
        if (!isListening) {
            setTimeout(() => setStatus('Ready'), 2000);
        }
    };

    // ==================== CONTINUOUS VOICE LISTENING ====================
    const startContinuousListening = useCallback(() => {
        if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
            setStatus('Voice not supported in this browser');
            return;
        }

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        const recognition = new SpeechRecognition();

        recognition.continuous = true;  // Keep listening
        recognition.interimResults = true;  // Show partial results
        recognition.lang = 'en-US';
        recognition.maxAlternatives = 1;

        recognition.onstart = () => {
            console.log('Voice recognition started');
            setVoiceStatus('Listening...');
            setStatus('🎤 Listening...');
        };

        recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const transcript = event.results[i][0].transcript;
                if (event.results[i].isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            if (interimTranscript) {
                setVoiceStatus(`Hearing: "${interimTranscript}"`);
            }

            if (finalTranscript) {
                console.log('Final transcript:', finalTranscript);
                setVoiceStatus(`You said: "${finalTranscript}"`);

                // Process the voice command
                processVoiceCommand(finalTranscript.trim());
            }
        };

        recognition.onerror = (event) => {
            console.error('Voice error:', event.error);
            if (event.error === 'no-speech') {
                setVoiceStatus('No speech detected, still listening...');
            } else if (event.error === 'aborted') {
                // Intentionally stopped
            } else {
                setVoiceStatus(`Error: ${event.error}`);
            }
        };

        recognition.onend = () => {
            console.log('Voice recognition ended, isListeningRef:', isListeningRef.current);
            // Auto-restart if still in listening mode
            if (isListeningRef.current) {
                setTimeout(() => {
                    try {
                        recognition.start();
                        console.log('Restarted listening');
                    } catch (err) {
                        console.error('Failed to restart:', err);
                    }
                }, 100);
            } else {
                setStatus('Ready');
                setVoiceStatus('');
            }
        };

        recognitionRef.current = recognition;

        try {
            recognition.start();
            isListeningRef.current = true;
            setIsListening(true);
        } catch (err) {
            console.error('Failed to start recognition:', err);
            setStatus('Voice failed to start');
        }
    }, []);

    const stopListening = useCallback(() => {
        isListeningRef.current = false;
        setIsListening(false);
        if (recognitionRef.current) {
            recognitionRef.current.stop();
            recognitionRef.current = null;
        }
        setVoiceStatus('');
        setStatus('Ready');
    }, []);

    const toggleVoice = () => {
        if (isListening) {
            stopListening();
        } else {
            startContinuousListening();
        }
    };

    // ==================== PROCESS VOICE COMMANDS ====================
    const processVoiceCommand = async (command) => {
        const lowerCommand = command.toLowerCase();

        // Check for special commands
        if (lowerCommand.includes('stop listening') || lowerCommand.includes('turn off voice')) {
            stopListening();
            speakText('Voice listening stopped');
            return;
        }

        if (lowerCommand.includes('read screen') || lowerCommand.includes('capture screen') || lowerCommand.includes('what\'s on my screen')) {
            await captureScreen();
            return;
        }

        if (lowerCommand.includes('system stats') || lowerCommand.includes('show system') || lowerCommand.includes('computer stats')) {
            await runPlugin('system_stats', 'stats');
            return;
        }

        if (lowerCommand.includes('clear chat') || lowerCommand.includes('clear messages')) {
            setMessages([]);
            speakText('Chat cleared');
            return;
        }

        // Default: send to AI
        await sendMessage(command);
    };

    // ==================== RUN PLUGIN ====================
    const runPlugin = async (pluginName, command, params = {}) => {
        setStatus(`Running ${pluginName}...`);
        try {
            const res = await fetch(`${API_BASE}/plugins/${pluginName}/run`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command, params })
            });

            if (!res.ok) {
                throw new Error(`HTTP ${res.status}`);
            }

            const data = await res.json();

            let resultText = '';
            if (data.result) {
                resultText = typeof data.result === 'string' ? data.result : JSON.stringify(data.result, null, 2);
            } else if (data.error) {
                resultText = `Error: ${data.error}`;
            } else {
                resultText = JSON.stringify(data, null, 2);
            }

            setMessages(prev => [...prev, {
                role: 'system',
                content: `🧩 ${pluginName}.${command}:\n${resultText}`
            }]);

            setStatus(isListening ? '🎤 Listening...' : 'Ready');
        } catch (err) {
            console.error('Plugin error:', err);
            setMessages(prev => [...prev, {
                role: 'error',
                content: `Plugin error: ${err.message}. Make sure backend is running.`
            }]);
            setStatus(isListening ? '🎤 Listening...' : 'Plugin error');
        }
    };

    // ==================== KEYBOARD HANDLER ====================
    const handleKeyDown = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    // ==================== CONNECTION STATUS COLOR ====================
    const getStatusColor = () => {
        if (!backendConnected) return '#ef4444';
        if (!ollamaConnected) return '#eab308';
        if (isListening) return '#22c55e';
        return '#22c55e';
    };

    // ==================== RENDER ====================
    return (
        <div className="app-container">
            {/* Title Bar */}
            <div className="title-bar">
                <div className="title-bar-left">
                    <div
                        className="status-dot"
                        style={{ background: getStatusColor() }}
                        title={status}
                    />
                    <span className="title-text">JARVIS</span>
                    <span className="status-badge">{settings.model}</span>
                    {isListening && <span className="listening-badge">🎤 LIVE</span>}
                </div>
                <div className="title-bar-right">
                    <button className="title-btn" onClick={() => setShowSettings(!showSettings)} title="Settings">
                        ⚙️
                    </button>
                    <div className="window-controls">
                        <button className="win-btn minimize" onClick={() => window.electronAPI?.minimizeWindow?.()}>─</button>
                        <button className="win-btn maximize" onClick={() => window.electronAPI?.maximizeWindow?.()}>□</button>
                        <button className="win-btn close" onClick={() => window.electronAPI?.hideWindow?.()}>✕</button>
                    </div>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="settings-panel">
                    <h3>⚙️ Settings</h3>
                    <div className="setting-row">
                        <label>AI Model:</label>
                        <select
                            value={settings.model}
                            onChange={(e) => setSettings({ ...settings, model: e.target.value })}
                        >
                            {models.length > 0 ? models.map(m => (
                                <option key={m} value={m}>{m}</option>
                            )) : (
                                <option value="llama3.1:8b">llama3.1:8b</option>
                            )}
                        </select>
                    </div>
                    <div className="setting-row">
                        <label>Auto-Speak Responses:</label>
                        <input
                            type="checkbox"
                            checked={settings.autoSpeak}
                            onChange={(e) => setSettings({ ...settings, autoSpeak: e.target.checked })}
                        />
                    </div>
                    <button className="settings-close" onClick={() => setShowSettings(false)}>Close</button>
                </div>
            )}

            {/* Tab Navigation */}
            <div className="tab-nav">
                <button
                    className={`tab-btn ${activeTab === 'chat' ? 'active' : ''}`}
                    onClick={() => setActiveTab('chat')}
                >
                    💬 Chat
                </button>
                <button
                    className={`tab-btn ${activeTab === 'plugins' ? 'active' : ''}`}
                    onClick={() => { setActiveTab('plugins'); loadPlugins(); }}
                >
                    🧩 Plugins
                </button>
                <div className="voice-toggle-container">
                    <button
                        className={`voice-toggle-btn ${isListening ? 'active' : ''}`}
                        onClick={toggleVoice}
                    >
                        {isListening ? '🛑 Stop Listening' : '🎤 Start Listening'}
                    </button>
                </div>
            </div>

            {/* Voice Status Bar */}
            {isListening && (
                <div className="voice-status-bar">
                    <div className="voice-indicator">
                        <span className="pulse-dot"></span>
                        {voiceStatus || 'Listening for commands...'}
                    </div>
                    <div className="voice-commands-hint">
                        Say: "read screen" • "system stats" • "stop listening" • or ask anything
                    </div>
                </div>
            )}

            {/* Main Content */}
            <div className="main-content">
                {activeTab === 'chat' && (
                    <>
                        {/* Messages */}
                        <div className="messages-container">
                            {messages.length === 0 && (
                                <div className="welcome-message">
                                    <h1>👋 Hello! I'm JARVIS</h1>
                                    <p>Your local AI assistant. Click buttons below or start voice listening!</p>
                                    <div className="feature-grid">
                                        <div className="feature-card" onClick={captureScreen}>
                                            <span className="feature-icon">📸</span>
                                            <span>Read Screen</span>
                                        </div>
                                        <div className="feature-card" onClick={toggleVoice}>
                                            <span className="feature-icon">{isListening ? '🛑' : '🎤'}</span>
                                            <span>{isListening ? 'Stop Voice' : 'Start Voice'}</span>
                                        </div>
                                        <div className="feature-card" onClick={() => runPlugin('system_stats', 'stats')}>
                                            <span className="feature-icon">💻</span>
                                            <span>System Stats</span>
                                        </div>
                                        <div className="feature-card" onClick={() => setActiveTab('plugins')}>
                                            <span className="feature-icon">🧩</span>
                                            <span>All Plugins</span>
                                        </div>
                                    </div>
                                </div>
                            )}

                            {messages.map((msg, i) => (
                                <div key={i} className={`message ${msg.role}`}>
                                    <div className="message-avatar">
                                        {msg.role === 'user' ? '👤' : msg.role === 'assistant' ? '🤖' : msg.role === 'error' ? '⚠️' : 'ℹ️'}
                                    </div>
                                    <div className="message-content">
                                        <pre>{msg.content}</pre>
                                        {msg.model && <span className="message-model">{msg.model}</span>}
                                    </div>
                                </div>
                            ))}

                            {isLoading && (
                                <div className="message assistant loading">
                                    <div className="message-avatar">🤖</div>
                                    <div className="message-content">
                                        <div className="typing-indicator">
                                            <span></span><span></span><span></span>
                                        </div>
                                    </div>
                                </div>
                            )}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="input-area">
                            <div className="input-wrapper">
                                <input
                                    ref={inputRef}
                                    type="text"
                                    value={input}
                                    onChange={(e) => setInput(e.target.value)}
                                    onKeyDown={handleKeyDown}
                                    placeholder={isListening ? "Listening... or type here" : "Ask JARVIS anything..."}
                                    disabled={isLoading}
                                />
                                <div className="input-actions">
                                    <button
                                        className={`voice-btn ${isListening ? 'active' : ''}`}
                                        onClick={toggleVoice}
                                        title={isListening ? "Stop Listening" : "Start Voice"}
                                    >
                                        {isListening ? '🛑' : '🎤'}
                                    </button>
                                    <button
                                        className="screen-btn"
                                        onClick={captureScreen}
                                        title="Capture Screen"
                                    >
                                        📸
                                    </button>
                                    <button
                                        className="send-btn"
                                        onClick={() => sendMessage()}
                                        disabled={!input.trim() || isLoading}
                                    >
                                        ➤
                                    </button>
                                </div>
                            </div>
                            <div className="input-footer">
                                <span className="status-text">{status}</span>
                                <span className="hint-text">Enter to send • 🎤 for voice</span>
                            </div>
                        </div>
                    </>
                )}

                {activeTab === 'plugins' && (
                    <div className="plugins-panel">
                        <h2>🧩 Available Plugins</h2>
                        {pluginError && (
                            <div className="plugin-error">
                                ⚠️ {pluginError}
                                <button onClick={loadPlugins}>Retry</button>
                            </div>
                        )}
                        {plugins.length === 0 && !pluginError ? (
                            <div className="no-plugins">
                                <p>Loading plugins...</p>
                                <button onClick={loadPlugins}>Refresh</button>
                            </div>
                        ) : (
                            <div className="plugins-grid">
                                {plugins.map(plugin => (
                                    <div key={plugin.name} className="plugin-card">
                                        <h3>{plugin.name.replace(/_/g, ' ')}</h3>
                                        <p>{plugin.description || 'No description'}</p>
                                        <div className="plugin-commands">
                                            {(plugin.commands || []).map(cmd => (
                                                <button
                                                    key={cmd}
                                                    className="plugin-cmd-btn"
                                                    onClick={() => runPlugin(plugin.name, cmd)}
                                                >
                                                    {cmd}
                                                </button>
                                            ))}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

export default App;
