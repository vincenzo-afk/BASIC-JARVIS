import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

const PluginPanel = ({ isOpen, onClose }) => {
    const [plugins, setPlugins] = useState([]);
    const [loading, setLoading] = useState(false);
    const [activePlugin, setActivePlugin] = useState(null);
    const [runResult, setRunResult] = useState(null);
    const [runningCommand, setRunningCommand] = useState(null);

    // Fetch plugins when opened
    useEffect(() => {
        if (isOpen) {
            fetchPlugins();
        }
    }, [isOpen]);

    const fetchPlugins = async () => {
        setLoading(true);
        try {
            const res = await axios.get(`${API_BASE}/plugins/`);
            setPlugins(res.data || []);
        } catch (error) {
            console.error('Failed to fetch plugins:', error);
            setPlugins([]);
        }
        setLoading(false);
    };

    const runPluginCommand = async (pluginName, command, params = {}) => {
        setRunningCommand(`${pluginName}:${command}`);
        setRunResult(null);

        try {
            const res = await axios.post(`${API_BASE}/plugins/${pluginName}/run`, {
                command,
                params
            });

            setRunResult({
                status: 'success',
                plugin: pluginName,
                command,
                result: res.data.result
            });
        } catch (error) {
            setRunResult({
                status: 'error',
                plugin: pluginName,
                command,
                error: error.response?.data?.detail || error.message
            });
        }

        setRunningCommand(null);
    };

    const reloadPlugin = async (pluginName) => {
        try {
            await axios.post(`${API_BASE}/plugins/${pluginName}/reload`);
            fetchPlugins();
        } catch (error) {
            console.error('Failed to reload plugin:', error);
        }
    };

    const getPluginIcon = (name) => {
        const icons = {
            youtube_dl: '📺',
            system_stats: '📊',
            auto_summariser: '📝',
            clipboard: '📋',
            notes: '📓',
            browser: '🌐'
        };
        return icons[name] || '🧩';
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content plugin-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <div>
                        <h2 className="modal-title">Plugins</h2>
                        <p className="modal-subtitle">Extend JARVIS capabilities</p>
                    </div>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                {/* Content */}
                <div className="modal-body">
                    {loading ? (
                        <div className="plugin-loading">
                            <div className="spinner-large" />
                            <p>Loading plugins...</p>
                        </div>
                    ) : plugins.length === 0 ? (
                        <div className="plugin-empty">
                            <div className="plugin-empty-icon">🧩</div>
                            <h3>No Plugins Installed</h3>
                            <p>Add plugins to <code>backend/plugins/</code> folder</p>
                        </div>
                    ) : (
                        <div className="plugin-list">
                            {plugins.map((plugin) => (
                                <PluginCard
                                    key={plugin.name}
                                    plugin={plugin}
                                    icon={getPluginIcon(plugin.name)}
                                    isActive={activePlugin === plugin.name}
                                    isRunning={runningCommand?.startsWith(plugin.name)}
                                    onToggle={() => setActivePlugin(
                                        activePlugin === plugin.name ? null : plugin.name
                                    )}
                                    onRunCommand={(cmd, params) => runPluginCommand(plugin.name, cmd, params)}
                                    onReload={() => reloadPlugin(plugin.name)}
                                />
                            ))}
                        </div>
                    )}

                    {/* Run Result */}
                    {runResult && (
                        <div className={`plugin-result ${runResult.status}`}>
                            <div className="plugin-result-header">
                                <span className="plugin-result-icon">
                                    {runResult.status === 'success' ? '✅' : '❌'}
                                </span>
                                <span className="plugin-result-title">
                                    {runResult.plugin} → {runResult.command}
                                </span>
                                <button
                                    className="plugin-result-close"
                                    onClick={() => setRunResult(null)}
                                >
                                    ✕
                                </button>
                            </div>
                            <div className="plugin-result-body">
                                {runResult.status === 'success' ? (
                                    <pre>{JSON.stringify(runResult.result, null, 2)}</pre>
                                ) : (
                                    <p className="error-text">{runResult.error}</p>
                                )}
                            </div>
                        </div>
                    )}
                </div>

                {/* Footer */}
                <div className="modal-footer">
                    <span className="plugin-count">
                        {plugins.length} plugin{plugins.length !== 1 ? 's' : ''} installed
                    </span>
                    <button className="btn-secondary" onClick={fetchPlugins}>
                        ↻ Refresh
                    </button>
                </div>
            </div>
        </div>
    );
};

// Plugin Card Component
const PluginCard = ({
    plugin,
    icon,
    isActive,
    isRunning,
    onToggle,
    onRunCommand,
    onReload
}) => {
    const [commandParams, setCommandParams] = useState({});

    return (
        <div className={`plugin-card ${isActive ? 'expanded' : ''}`}>
            {/* Header */}
            <div className="plugin-card-header" onClick={onToggle}>
                <div className="plugin-card-icon">{icon}</div>
                <div className="plugin-card-info">
                    <h4 className="plugin-card-name">{plugin.name}</h4>
                    <p className="plugin-card-desc">
                        {plugin.description || 'No description'}
                    </p>
                </div>
                <div className="plugin-card-meta">
                    <span className="plugin-version">v{plugin.version || '1.0.0'}</span>
                    <span className={`plugin-expand-icon ${isActive ? 'expanded' : ''}`}>
                        ▼
                    </span>
                </div>
            </div>

            {/* Expanded Content */}
            {isActive && (
                <div className="plugin-card-body">
                    {/* Commands */}
                    {plugin.commands && plugin.commands.length > 0 && (
                        <div className="plugin-commands">
                            <h5>Commands</h5>
                            <div className="plugin-command-list">
                                {plugin.commands.map((cmd) => (
                                    <div key={cmd} className="plugin-command">
                                        <span className="plugin-command-name">/{cmd}</span>
                                        <button
                                            className="plugin-command-run"
                                            onClick={() => onRunCommand(cmd, commandParams[cmd] || {})}
                                            disabled={isRunning}
                                        >
                                            {isRunning ? '...' : '▶ Run'}
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Dependencies */}
                    {plugin.dependencies && plugin.dependencies.length > 0 && (
                        <div className="plugin-deps">
                            <h5>Dependencies</h5>
                            <div className="plugin-dep-list">
                                {plugin.dependencies.map((dep) => (
                                    <span key={dep} className="plugin-dep">{dep}</span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="plugin-actions">
                        <button
                            className="btn-small btn-secondary"
                            onClick={onReload}
                        >
                            ↻ Reload
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PluginPanel;
