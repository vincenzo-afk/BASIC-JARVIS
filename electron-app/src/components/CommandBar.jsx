import React, { useState, useRef, useEffect, useCallback } from 'react';

const API_BASE = 'http://localhost:8000/api';

/**
 * Enhanced CommandBar with Streaming Responses
 */
const CommandBar = ({ model = 'llama3.1:8b', onSubmit, setStatus, conversationHistory = [] }) => {
    const [input, setInput] = useState('');
    const [response, setResponse] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [isStreaming, setIsStreaming] = useState(false);
    const [tokensGenerated, setTokensGenerated] = useState(0);
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);

    const inputRef = useRef(null);
    const responseRef = useRef(null);
    const abortControllerRef = useRef(null);

    // Quick command suggestions
    const commandSuggestions = [
        { icon: '📸', text: 'Read my screen', prompt: 'Can you read what\'s on my screen?' },
        { icon: '💻', text: 'System stats', prompt: 'Show me my system stats' },
        { icon: '📝', text: 'Summarize', prompt: 'Summarize the following text: ' },
        { icon: '🔍', text: 'Search web', prompt: 'Search the web for: ' },
        { icon: '📅', text: 'Schedule task', prompt: 'Schedule a task to ' },
        { icon: '🤖', text: 'Run workflow', prompt: 'Run a workflow that ' },
    ];

    // Focus input on mount
    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    // Auto-scroll response
    useEffect(() => {
        if (responseRef.current) {
            responseRef.current.scrollTop = responseRef.current.scrollHeight;
        }
    }, [response]);

    // Streaming submit handler
    const handleSubmit = async (e) => {
        e.preventDefault();

        const query = input.trim();
        if (!query || loading) return;

        setLoading(true);
        setError(null);
        setResponse('');
        setIsStreaming(true);
        setTokensGenerated(0);
        setStatus?.('Thinking...');
        setShowSuggestions(false);

        // Create abort controller for cancellation
        abortControllerRef.current = new AbortController();

        try {
            // Use streaming endpoint
            const response = await fetch(`${API_BASE}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    model: model,
                    prompt: query,
                    system: `You are JARVIS, an intelligent AI assistant. Be helpful, concise, and friendly.
                    
Previous conversation context:
${conversationHistory.slice(-5).map(h => `User: ${h.query}\nJARVIS: ${h.response}`).join('\n\n')}`,
                    temperature: 0.7
                }),
                signal: abortControllerRef.current.signal
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let fullResponse = '';
            let tokenCount = 0;

            setStatus?.('Generating...');

            while (true) {
                const { done, value } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n').filter(line => line.startsWith('data: '));

                for (const line of lines) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        if (data.error) {
                            throw new Error(data.error);
                        }

                        if (data.chunk) {
                            fullResponse += data.chunk;
                            tokenCount++;
                            setResponse(fullResponse);
                            setTokensGenerated(tokenCount);
                        }

                        if (data.done) {
                            break;
                        }
                    } catch (parseError) {
                        // Skip invalid JSON
                    }
                }
            }

            setStatus?.('Ready');
            onSubmit?.(query, fullResponse);
            setInput('');

        } catch (err) {
            if (err.name === 'AbortError') {
                setStatus?.('Cancelled');
                return;
            }

            console.error('Chat error:', err);
            let errorMessage = 'Failed to connect to JARVIS backend.';

            if (err.message.includes('Failed to fetch')) {
                errorMessage = 'Cannot connect to backend. Make sure the server is running.';
            } else if (err.message) {
                errorMessage = err.message;
            }

            setError(errorMessage);
            setStatus?.('Error');
        } finally {
            setLoading(false);
            setIsStreaming(false);
            abortControllerRef.current = null;
        }
    };

    // Cancel streaming
    const handleCancel = () => {
        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
            setLoading(false);
            setIsStreaming(false);
            setStatus?.('Cancelled');
        }
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Escape') {
            if (loading) {
                handleCancel();
            } else {
                setInput('');
                setResponse('');
                setError(null);
                setShowSuggestions(false);
            }
        }

        // Ctrl+Enter to submit
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit(e);
        }

        // Show suggestions on /
        if (e.key === '/' && input === '') {
            setShowSuggestions(true);
            setSuggestions(commandSuggestions);
        }
    };

    const handleClear = () => {
        setInput('');
        setResponse('');
        setError(null);
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    const handleSuggestionClick = (suggestion) => {
        setInput(suggestion.prompt);
        setShowSuggestions(false);
        inputRef.current?.focus();
    };

    // Copy response to clipboard
    const handleCopyResponse = async () => {
        try {
            await navigator.clipboard.writeText(response);
            setStatus?.('Copied to clipboard!');
            setTimeout(() => setStatus?.('Ready'), 2000);
        } catch (err) {
            console.error('Failed to copy:', err);
        }
    };

    return (
        <div className="command-bar">
            {/* Input Form */}
            <form onSubmit={handleSubmit} className="command-form">
                <div className="input-wrapper">
                    <input
                        ref={inputRef}
                        id="command-input"
                        type="text"
                        value={input}
                        onChange={(e) => {
                            setInput(e.target.value);
                            if (e.target.value === '') setShowSuggestions(false);
                        }}
                        onKeyDown={handleKeyDown}
                        onFocus={() => input === '' && setShowSuggestions(false)}
                        placeholder="Ask JARVIS anything... (type / for commands)"
                        disabled={loading}
                        autoComplete="off"
                        spellCheck="false"
                    />

                    <div className="input-actions">
                        {input && !loading && (
                            <button type="button" className="clear-btn" onClick={handleClear} title="Clear (Esc)">
                                ✕
                            </button>
                        )}

                        {loading ? (
                            <button type="button" className="cancel-btn" onClick={handleCancel} title="Cancel">
                                ⬛
                            </button>
                        ) : (
                            <button
                                type="submit"
                                className="submit-btn"
                                disabled={!input.trim()}
                                title="Send (Enter)"
                            >
                                <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                            </button>
                        )}
                    </div>
                </div>

                {/* Suggestions Dropdown */}
                {showSuggestions && suggestions.length > 0 && (
                    <div className="suggestions-dropdown">
                        {suggestions.map((suggestion, index) => (
                            <button
                                key={index}
                                type="button"
                                className="suggestion-item"
                                onClick={() => handleSuggestionClick(suggestion)}
                            >
                                <span className="suggestion-icon">{suggestion.icon}</span>
                                <span className="suggestion-text">{suggestion.text}</span>
                            </button>
                        ))}
                    </div>
                )}
            </form>

            {/* Error Display */}
            {error && (
                <div className="command-error">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{error}</span>
                </div>
            )}

            {/* Response Display */}
            {(response || isStreaming) && (
                <div className="command-response" ref={responseRef}>
                    <div className="response-header">
                        <div className="response-avatar">J</div>
                        <div className="response-meta">
                            <span className="response-name">JARVIS</span>
                            <span className="response-model">{model}</span>
                        </div>
                        <div className="response-actions">
                            {response && !isStreaming && (
                                <button className="copy-btn" onClick={handleCopyResponse} title="Copy response">
                                    📋
                                </button>
                            )}
                        </div>
                    </div>
                    <div className="response-content">
                        {response}
                        {isStreaming && <span className="streaming-cursor" />}
                    </div>
                    {isStreaming && (
                        <div className="streaming-info">
                            <span className="token-count">{tokensGenerated} tokens</span>
                            <div className="streaming-indicator">
                                <div className="streaming-dot" />
                                <div className="streaming-dot" />
                                <div className="streaming-dot" />
                            </div>
                        </div>
                    )}
                </div>
            )}

            {/* Command Footer */}
            <div className="command-footer">
                <span>Model: {model}</span>
                <span>Press / for commands • Enter to send • Esc to clear</span>
            </div>
        </div>
    );
};

export default CommandBar;
