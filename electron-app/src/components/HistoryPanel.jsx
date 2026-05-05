import React from 'react';

const HistoryPanel = ({ history = [] }) => {
    if (history.length === 0) {
        return (
            <div className="history-panel empty">
                <div className="history-empty-icon">📜</div>
                <p className="history-empty-text">No activity yet</p>
            </div>
        );
    }

    const formatTime = (date) => {
        const d = new Date(date);
        return d.toLocaleTimeString([], {
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    const formatDate = (date) => {
        const d = new Date(date);
        const today = new Date();
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);

        if (d.toDateString() === today.toDateString()) {
            return 'Today';
        } else if (d.toDateString() === yesterday.toDateString()) {
            return 'Yesterday';
        }
        return d.toLocaleDateString([], { month: 'short', day: 'numeric' });
    };

    const getTypeIcon = (type) => {
        const icons = {
            chat: '💬',
            screen: '📸',
            voice: '🎤',
            action: '⚡',
            plugin: '🧩',
            error: '⚠️'
        };
        return icons[type] || '📝';
    };

    const getTypeLabel = (type) => {
        const labels = {
            chat: 'Chat',
            screen: 'Screen Capture',
            voice: 'Voice Input',
            action: 'Action',
            plugin: 'Plugin',
            error: 'Error'
        };
        return labels[type] || 'Activity';
    };

    const truncateText = (text, maxLength = 100) => {
        if (!text) return '';
        if (text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    };

    return (
        <div className="history-panel">
            <div className="history-header">
                <h3 className="history-title">
                    <span className="history-title-line" />
                    Recent Activity
                    <span className="history-title-line" />
                </h3>
                <span className="history-count">{history.length} items</span>
            </div>

            <div className="history-list">
                {history.slice(0, 20).map((item) => (
                    <div key={item.id} className={`history-item type-${item.type}`}>
                        <div className="history-item-icon">
                            {getTypeIcon(item.type)}
                        </div>

                        <div className="history-item-content">
                            <div className="history-item-header">
                                <span className="history-item-type">{getTypeLabel(item.type)}</span>
                                <span className="history-item-time">
                                    {formatDate(item.timestamp)} • {formatTime(item.timestamp)}
                                </span>
                            </div>

                            {item.type === 'chat' && (
                                <>
                                    <p className="history-item-query">
                                        <span className="query-prefix">You:</span> {truncateText(item.query, 80)}
                                    </p>
                                    <p className="history-item-response">
                                        <span className="response-prefix">JARVIS:</span> {truncateText(item.response, 120)}
                                    </p>
                                </>
                            )}

                            {item.type === 'screen' && (
                                <p className="history-item-text">
                                    {truncateText(item.text, 150) || 'Screen captured'}
                                </p>
                            )}

                            {item.type === 'voice' && (
                                <p className="history-item-text">
                                    🎤 {truncateText(item.text, 100) || 'Voice input detected'}
                                </p>
                            )}

                            {item.type === 'action' && (
                                <p className="history-item-text">
                                    {item.action}: {item.result || 'Completed'}
                                </p>
                            )}

                            {item.type === 'plugin' && (
                                <p className="history-item-text">
                                    Plugin: {item.plugin} → {item.command}
                                </p>
                            )}

                            {item.type === 'error' && (
                                <p className="history-item-error">
                                    {item.message}
                                </p>
                            )}

                            {item.model && (
                                <span className="history-item-model">{item.model}</span>
                            )}
                        </div>
                    </div>
                ))}
            </div>

            {history.length > 20 && (
                <div className="history-more">
                    +{history.length - 20} more items
                </div>
            )}
        </div>
    );
};

export default HistoryPanel;
