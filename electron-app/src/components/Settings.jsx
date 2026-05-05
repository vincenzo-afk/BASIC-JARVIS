import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Settings = ({ isOpen, onClose, settings, onSave }) => {
    const [localSettings, setLocalSettings] = useState(settings || {
        selectedModel: 'llama3.1:8b',
        ollamaHost: 'http://localhost:11434',
        ocrEnabled: true,
        voiceEnabled: true,
        hotkey: 'Alt+Space',
        theme: 'dark'
    });
    const [availableModels, setAvailableModels] = useState([]);
    const [loading, setLoading] = useState(false);
    const [testResult, setTestResult] = useState(null);

    // Sync local settings with props
    useEffect(() => {
        if (settings) {
            setLocalSettings(settings);
        }
    }, [settings]);

    // Fetch available models when opened
    useEffect(() => {
        if (isOpen) {
            fetchModels();
        }
    }, [isOpen]);

    const fetchModels = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${localSettings.ollamaHost}/api/tags`, {
                timeout: 5000
            });
            setAvailableModels(res.data.models || []);
        } catch (error) {
            console.error('Failed to fetch models:', error);
            setAvailableModels([]);
        }
        setLoading(false);
    };

    const testConnection = async () => {
        setTestResult({ status: 'testing', message: 'Testing connection...' });

        try {
            // Test Ollama
            await axios.get(`${localSettings.ollamaHost}/api/tags`, { timeout: 3000 });

            // Test Backend
            await axios.get('http://localhost:8000/', { timeout: 3000 });

            setTestResult({ status: 'success', message: '✅ All connections working!' });
        } catch (error) {
            setTestResult({
                status: 'error',
                message: `❌ Connection failed: ${error.message}`
            });
        }

        setTimeout(() => setTestResult(null), 5000);
    };

    const handleChange = (key, value) => {
        setLocalSettings(prev => ({ ...prev, [key]: value }));
    };

    const handleSave = () => {
        onSave?.(localSettings);
        onClose();
    };

    const handleReset = () => {
        const defaults = {
            selectedModel: 'llama3.1:8b',
            ollamaHost: 'http://localhost:11434',
            ocrEnabled: true,
            voiceEnabled: true,
            hotkey: 'Alt+Space',
            theme: 'dark'
        };
        setLocalSettings(defaults);
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content settings-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h2 className="modal-title">Settings</h2>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                {/* Content */}
                <div className="modal-body">
                    {/* AI Model Section */}
                    <div className="settings-section">
                        <h3 className="settings-section-title">🤖 AI Model</h3>

                        <div className="settings-field">
                            <label>Selected Model</label>
                            <select
                                value={localSettings.selectedModel}
                                onChange={(e) => handleChange('selectedModel', e.target.value)}
                            >
                                {loading ? (
                                    <option>Loading models...</option>
                                ) : availableModels.length > 0 ? (
                                    availableModels.map((model) => (
                                        <option key={model.name} value={model.name}>
                                            {model.name} ({(model.size / 1e9).toFixed(1)}GB)
                                        </option>
                                    ))
                                ) : (
                                    <>
                                        <option value="llama3.1:8b">llama3.1:8b</option>
                                        <option value="qwen2.5-coder:7b">qwen2.5-coder:7b</option>
                                        <option value="glm-4-9b">glm-4-9b</option>
                                        <option value="mistral:7b">mistral:7b</option>
                                    </>
                                )}
                            </select>
                            <button
                                className="settings-refresh-btn"
                                onClick={fetchModels}
                                disabled={loading}
                            >
                                {loading ? '...' : '↻'}
                            </button>
                        </div>

                        <div className="settings-field">
                            <label>Ollama Host</label>
                            <input
                                type="text"
                                value={localSettings.ollamaHost}
                                onChange={(e) => handleChange('ollamaHost', e.target.value)}
                                placeholder="http://localhost:11434"
                            />
                        </div>
                    </div>

                    {/* Features Section */}
                    <div className="settings-section">
                        <h3 className="settings-section-title">⚡ Features</h3>

                        <div className="settings-toggles">
                            <ToggleField
                                label="Screen Reader (OCR)"
                                description="Enable screen capture and text extraction"
                                value={localSettings.ocrEnabled}
                                onChange={(val) => handleChange('ocrEnabled', val)}
                            />

                            <ToggleField
                                label="Voice Input/Output"
                                description="Enable speech-to-text and text-to-speech"
                                value={localSettings.voiceEnabled}
                                onChange={(val) => handleChange('voiceEnabled', val)}
                            />
                        </div>
                    </div>

                    {/* Shortcuts Section */}
                    <div className="settings-section">
                        <h3 className="settings-section-title">⌨️ Shortcuts</h3>

                        <div className="settings-field">
                            <label>Global Hotkey</label>
                            <input
                                type="text"
                                value={localSettings.hotkey}
                                onChange={(e) => handleChange('hotkey', e.target.value)}
                                placeholder="Alt+Space"
                            />
                            <span className="settings-hint">Requires app restart</span>
                        </div>
                    </div>

                    {/* Connection Test */}
                    <div className="settings-section">
                        <h3 className="settings-section-title">🔌 Connection</h3>

                        <button
                            className="settings-test-btn"
                            onClick={testConnection}
                            disabled={testResult?.status === 'testing'}
                        >
                            Test Connection
                        </button>

                        {testResult && (
                            <div className={`settings-test-result ${testResult.status}`}>
                                {testResult.message}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="modal-footer">
                    <button className="btn-secondary" onClick={handleReset}>
                        Reset to Defaults
                    </button>
                    <div className="modal-footer-right">
                        <button className="btn-secondary" onClick={onClose}>
                            Cancel
                        </button>
                        <button className="btn-primary" onClick={handleSave}>
                            Save Settings
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
};

// Toggle Field Component
const ToggleField = ({ label, description, value, onChange }) => (
    <div className="toggle-field">
        <div className="toggle-field-info">
            <span className="toggle-field-label">{label}</span>
            {description && <span className="toggle-field-desc">{description}</span>}
        </div>
        <button
            className={`toggle-switch ${value ? 'on' : 'off'}`}
            onClick={() => onChange(!value)}
        >
            <span className="toggle-knob" />
        </button>
    </div>
);

export default Settings;
