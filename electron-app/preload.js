const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld('electronAPI', {
    // Window controls
    minimizeWindow: () => ipcRenderer.send('window-minimize'),
    maximizeWindow: () => ipcRenderer.send('window-maximize'),
    closeWindow: () => ipcRenderer.send('window-close'),
    hideWindow: () => ipcRenderer.send('window-hide'),

    // App info
    getAppInfo: () => ipcRenderer.invoke('get-app-info'),

    // Event listeners
    onOpenSettings: (callback) => {
        ipcRenderer.on('open-settings', callback);
        return () => ipcRenderer.removeListener('open-settings', callback);
    },

    onFocusInput: (callback) => {
        ipcRenderer.on('focus-input', callback);
        return () => ipcRenderer.removeListener('focus-input', callback);
    },

    // Platform info
    platform: process.platform,

    // Notification
    showNotification: (title, body) => {
        new Notification(title, { body });
    }
});

// Expose version info
contextBridge.exposeInMainWorld('versions', {
    node: () => process.versions.node,
    chrome: () => process.versions.chrome,
    electron: () => process.versions.electron
});

console.log('[Preload] JARVIS preload script loaded');
