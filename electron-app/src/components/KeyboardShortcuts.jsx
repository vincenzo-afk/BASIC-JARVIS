import React, { useEffect, useState, useCallback } from 'react';

/**
 * Keyboard Shortcuts Panel - Shows all available shortcuts
 */
const KeyboardShortcuts = ({ isOpen, onClose }) => {
    const shortcuts = [
        {
            category: 'General', items: [
                { keys: ['Alt', 'Space'], description: 'Toggle JARVIS window' },
                { keys: ['Esc'], description: 'Close modal / Clear input' },
                { keys: ['Ctrl', ','], description: 'Open Settings' },
                { keys: ['Ctrl', 'P'], description: 'Open Plugins' },
            ]
        },
        {
            category: 'Chat', items: [
                { keys: ['Enter'], description: 'Send message' },
                { keys: ['/'], description: 'Show command suggestions' },
                { keys: ['Ctrl', 'C'], description: 'Cancel generation' },
                { keys: ['↑', '↓'], description: 'Navigate history' },
            ]
        },
        {
            category: 'Voice', items: [
                { keys: ['Ctrl', 'Space'], description: 'Hold to speak' },
                { keys: ['Ctrl', 'M'], description: 'Toggle microphone' },
                { keys: ['Ctrl', 'S'], description: 'Speak last response' },
            ]
        },
        {
            category: 'Actions', items: [
                { keys: ['Ctrl', 'Shift', 'S'], description: 'Capture screen' },
                { keys: ['Ctrl', 'Shift', 'O'], description: 'OCR current screen' },
                { keys: ['Ctrl', 'Shift', 'R'], description: 'Run last workflow' },
            ]
        },
    ];

    // Handle keyboard shortcut to open this panel
    useEffect(() => {
        const handleKeyDown = (e) => {
            // Ctrl+/ or F1 to toggle shortcuts
            if ((e.ctrlKey && e.key === '/') || e.key === 'F1') {
                e.preventDefault();
                onClose?.();
            }
            // Esc to close
            if (e.key === 'Escape' && isOpen) {
                e.preventDefault();
                onClose?.();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [isOpen, onClose]);

    if (!isOpen) return null;

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content shortcuts-modal" onClick={e => e.stopPropagation()}>
                {/* Header */}
                <div className="modal-header">
                    <h2 className="modal-title">⌨️ Keyboard Shortcuts</h2>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                {/* Content */}
                <div className="modal-body shortcuts-body">
                    {shortcuts.map((section, sectionIndex) => (
                        <div key={sectionIndex} className="shortcuts-section">
                            <h3 className="shortcuts-category">{section.category}</h3>
                            <div className="shortcuts-list">
                                {section.items.map((shortcut, itemIndex) => (
                                    <div key={itemIndex} className="shortcut-item">
                                        <div className="shortcut-keys">
                                            {shortcut.keys.map((key, keyIndex) => (
                                                <React.Fragment key={keyIndex}>
                                                    <kbd className="shortcut-key">{key}</kbd>
                                                    {keyIndex < shortcut.keys.length - 1 && (
                                                        <span className="key-separator">+</span>
                                                    )}
                                                </React.Fragment>
                                            ))}
                                        </div>
                                        <span className="shortcut-description">{shortcut.description}</span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {/* Footer */}
                <div className="modal-footer shortcuts-footer">
                    <span className="shortcuts-hint">Press <kbd>F1</kbd> or <kbd>Ctrl+/</kbd> to toggle this panel</span>
                </div>
            </div>
        </div>
    );
};

/**
 * Global Keyboard Shortcut Handler Hook
 */
export const useKeyboardShortcuts = (handlers = {}) => {
    const handleKeyDown = useCallback((e) => {
        const key = e.key.toLowerCase();
        const ctrl = e.ctrlKey || e.metaKey;
        const shift = e.shiftKey;
        const alt = e.altKey;

        // Build shortcut string
        let shortcut = '';
        if (ctrl) shortcut += 'ctrl+';
        if (shift) shortcut += 'shift+';
        if (alt) shortcut += 'alt+';
        shortcut += key;

        // Check if handler exists
        if (handlers[shortcut]) {
            e.preventDefault();
            handlers[shortcut](e);
        }
    }, [handlers]);

    useEffect(() => {
        window.addEventListener('keydown', handleKeyDown);
        return () => window.removeEventListener('keydown', handleKeyDown);
    }, [handleKeyDown]);
};

export default KeyboardShortcuts;
