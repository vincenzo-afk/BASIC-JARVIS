import React, { useState, useRef, useCallback, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

/**
 * Enhanced VoiceInput Component with Hands-Free Mode
 * Features: Push-to-talk, Hands-Free Loop, Audio Visualization
 */
const VoiceInput = ({
    onTranscription,
    onResponse,
    onError,
    onListeningChange,
    model = 'llama3.1:8b',
    autoSpeak = true,
    isEnabled = true
}) => {
    const [isRecording, setIsRecording] = useState(false);
    const [isProcessing, setIsProcessing] = useState(false);
    const [audioLevel, setAudioLevel] = useState(0);
    const [status, setStatus] = useState('idle'); // idle, recording, processing, speaking, complete, error
    const [permissionGranted, setPermissionGranted] = useState(false);
    const [lastTranscription, setLastTranscription] = useState('');
    const [handsFreeMode, setHandsFreeMode] = useState(false);

    const mediaRecorderRef = useRef(null);
    const audioChunksRef = useRef([]);
    const analyserRef = useRef(null);
    const animationFrameRef = useRef(null);
    const streamRef = useRef(null);
    const audioContextRef = useRef(null);
    const audioRef = useRef(null);

    // Check for microphone permission
    useEffect(() => {
        checkMicrophonePermission();
        return () => {
            stopAllAudio();
        };
    }, []);

    // Notify parent of listening state changes
    useEffect(() => {
        onListeningChange?.(isRecording);
    }, [isRecording, onListeningChange]);

    // Auto-restart recording if in hands-free mode
    useEffect(() => {
        let timeout;
        if (handsFreeMode && status === 'idle' && !isRecording && !isProcessing && isEnabled) {
            // Wait a brief moment before listening again to avoid picking up own echo
            timeout = setTimeout(() => {
                startRecording();
            }, 1000);
        }
        return () => clearTimeout(timeout);
    }, [handsFreeMode, status, isRecording, isProcessing, isEnabled]);

    const checkMicrophonePermission = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            setPermissionGranted(true);
            stream.getTracks().forEach(track => track.stop());
        } catch (error) {
            console.error('Microphone permission denied:', error);
            setPermissionGranted(false);
            onError?.('Microphone permission denied');
        }
    };

    const stopAllAudio = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
        }
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
        stopPlayback();
    };

    const startAudioLevelMonitor = (stream) => {
        if (!audioContextRef.current) {
            audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
        }

        const source = audioContextRef.current.createMediaStreamSource(stream);
        analyserRef.current = audioContextRef.current.createAnalyser();
        analyserRef.current.fftSize = 256;
        source.connect(analyserRef.current);

        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);

        const updateLevel = () => {
            if (!analyserRef.current) return;
            analyserRef.current.getByteFrequencyData(dataArray);

            // Calculate average level
            let sum = 0;
            for (let i = 0; i < dataArray.length; i++) {
                sum += dataArray[i];
            }
            const average = sum / dataArray.length;

            // Normalize to 0-1 range with some boost
            const normalized = Math.min(1, (average / 128) * 1.5);
            setAudioLevel(normalized);

            animationFrameRef.current = requestAnimationFrame(updateLevel);
        };

        updateLevel();
    };

    const stopAudioLevelMonitor = () => {
        if (animationFrameRef.current) {
            cancelAnimationFrame(animationFrameRef.current);
        }
        setAudioLevel(0);
    };

    const startRecording = useCallback(async () => {
        if (isRecording || isProcessing) return;

        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            streamRef.current = stream;

            const mediaRecorder = new MediaRecorder(stream);
            audioChunksRef.current = [];

            mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    audioChunksRef.current.push(event.data);
                }
            };

            mediaRecorder.onstop = () => {
                processRecording();
            };

            mediaRecorderRef.current = mediaRecorder;
            mediaRecorder.start(100);

            startAudioLevelMonitor(stream);
            setIsRecording(true);
            setStatus('recording');

        } catch (error) {
            console.error('Error starting recording:', error);
            onError?.(`Microphone error: ${error.message}`);
            setStatus('error');
        }
    }, [isRecording, isProcessing, onError]);

    const stopRecording = useCallback(() => {
        if (mediaRecorderRef.current && isRecording) {
            try {
                mediaRecorderRef.current.stop();
            } catch (err) {
                console.error('Error stopping recorder:', err);
            }

            if (streamRef.current) {
                streamRef.current.getTracks().forEach(track => track.stop());
            }

            stopAudioLevelMonitor();
            setIsRecording(false);
        }
    }, [isRecording]);

    const processRecording = async () => {
        if (audioChunksRef.current.length === 0) {
            setStatus('idle');
            return;
        }

        setIsProcessing(true);
        setStatus('processing');

        try {
            const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });

            // Check minimum size (avoid sending empty/tiny recordings)
            if (audioBlob.size < 1000) {
                setStatus('idle');
                setIsProcessing(false);
                return;
            }

            const formData = new FormData();
            formData.append('file', audioBlob, 'recording.webm');
            formData.append('model', model);
            formData.append('speak_response', autoSpeak ? 'true' : 'false');

            const response = await axios.post(`${API_BASE}/voice/voice-chat`, formData, {
                headers: { 'Content-Type': 'multipart/form-data' },
                timeout: 120000
            });

            const data = response.data;

            if (data.success) {
                setLastTranscription(data.transcription);
                onTranscription?.(data.transcription);

                onResponse?.({
                    text: data.response,
                    transcription: data.transcription,
                    model: data.model,
                    audioUrl: data.audio_url
                });

                // Play audio response
                if (data.audio_url && autoSpeak) {
                    await playAudioResponse(`http://localhost:8000${data.audio_url}`);
                }

                setStatus('complete');
            } else {
                throw new Error(data.error || 'Processing failed');
            }

        } catch (error) {
            console.error('Error processing audio:', error);

            let errorMsg = 'Failed to process audio';
            if (error.code === 'ECONNREFUSED') {
                errorMsg = 'Backend not running';
            } else if (error.response?.status === 503) {
                errorMsg = 'Speech service unavailable';
            } else if (error.message) {
                errorMsg = error.message;
            }

            onError?.(errorMsg);
            setStatus('error');
        } finally {
            setIsProcessing(false);
            audioChunksRef.current = [];

            // If not hands-free or if error, go to idle after delay
            // If hands-free, the useEffect will trigger restart when status becomes idle
            setTimeout(() => {
                if (status !== 'speaking') {
                    setStatus('idle');
                }
            }, 2000);
        }
    };

    const playAudioResponse = async (url) => {
        return new Promise((resolve) => {
            setStatus('speaking');

            audioRef.current = new Audio(url);

            audioRef.current.onended = () => {
                setStatus('idle');
                resolve();
            };

            audioRef.current.onerror = () => {
                console.error('Error playing audio');
                setStatus('idle');
                resolve();
            };

            audioRef.current.play().catch(err => {
                console.error('Playback error:', err);
                setStatus('idle');
                resolve();
            });
        });
    };

    const stopPlayback = () => {
        if (audioRef.current) {
            audioRef.current.pause();
            audioRef.current.currentTime = 0;
            setStatus('idle');
        }
    };

    const toggleRecording = useCallback(() => {
        if (status === 'speaking') {
            stopPlayback();
        } else if (isRecording) {
            stopRecording();
        } else {
            startRecording();
        }
    }, [isRecording, status, startRecording, stopRecording]);

    const toggleHandsFree = useCallback(() => {
        setHandsFreeMode(prev => {
            const newState = !prev;
            if (!newState) {
                stopRecording();
                stopPlayback();
            } else {
                // Start immediately if turning on
                startRecording();
            }
            return newState;
        });
    }, [startRecording, stopRecording]);

    // Keyboard shortcuts
    useEffect(() => {
        const handleKeyDown = (e) => {
            // Ctrl+Space to start recording (push-to-talk)
            if (e.code === 'Space' && e.ctrlKey && !isRecording && !isProcessing && isEnabled && !handsFreeMode) {
                e.preventDefault();
                startRecording();
            }
            // Ctrl+M to toggle mute/recording
            if (e.code === 'KeyM' && e.ctrlKey) {
                e.preventDefault();
                toggleRecording();
            }
        };

        const handleKeyUp = (e) => {
            // Release Ctrl+Space to stop (push-to-talk)
            if (e.code === 'Space' && isRecording && !handsFreeMode) {
                e.preventDefault();
                stopRecording();
            }
        };

        window.addEventListener('keydown', handleKeyDown);
        window.addEventListener('keyup', handleKeyUp);

        return () => {
            window.removeEventListener('keydown', handleKeyDown);
            window.removeEventListener('keyup', handleKeyUp);
        };
    }, [isRecording, isProcessing, isEnabled, handsFreeMode, startRecording, stopRecording, toggleRecording]);

    if (!isEnabled) return null;

    const getStatusColor = () => {
        switch (status) {
            case 'recording': return 'var(--color-red)';
            case 'processing': return 'var(--color-yellow)';
            case 'speaking': return 'var(--color-cyan)';
            case 'complete': return 'var(--color-green)';
            case 'error': return 'var(--color-red)';
            default: return 'var(--color-text-muted)';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'recording': return 'Listening...';
            case 'processing': return 'Processing...';
            case 'speaking': return 'Speaking...';
            case 'complete': return 'Done ✓';
            case 'error': return 'Error ⚠';
            default: return 'Click or Ctrl+Space';
        }
    };

    return (
        <div className={`voice-input ${handsFreeMode ? 'hands-free-active' : ''}`}>
            <div className="voice-controls">
                <button
                    className={`voice-button ${status}`}
                    onClick={toggleRecording}
                    disabled={isProcessing && status !== 'speaking'}
                    title={getStatusText()}
                >
                    {isProcessing && status !== 'speaking' ? (
                        <div className="voice-spinner" />
                    ) : status === 'speaking' ? (
                        <SpeakingIcon />
                    ) : isRecording ? (
                        <MicActiveIcon level={audioLevel} />
                    ) : (
                        <MicIcon />
                    )}
                </button>

                <button
                    className={`hands-free-btn ${handsFreeMode ? 'active' : ''}`}
                    onClick={toggleHandsFree}
                    title="Toggle Hands-Free Mode"
                >
                    {handsFreeMode ? '🎧 On' : '🎧 Off'}
                </button>
            </div>

            {isRecording && (
                <div className="voice-indicator">
                    <div
                        className="voice-level-bar"
                        style={{ transform: `scaleX(${audioLevel})` }}
                    />
                </div>
            )}

            <div className="voice-info">
                <span className="voice-status" style={{ color: getStatusColor() }}>
                    {handsFreeMode ? 'Hands-Free: ' : ''}{getStatusText()}
                </span>
                {lastTranscription && status === 'idle' && (
                    <span className="voice-last-text" title={lastTranscription}>
                        "{lastTranscription.substring(0, 30)}{lastTranscription.length > 30 ? '...' : ''}"
                    </span>
                )}
            </div>

            {!permissionGranted && (
                <button
                    className="voice-permission-btn"
                    onClick={checkMicrophonePermission}
                >
                    🎤 Enable Mic
                </button>
            )}
        </div>
    );
};

// Icons
const MicIcon = () => (
    <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
);

const MicActiveIcon = ({ level = 0 }) => (
    <div className="mic-active">
        <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24">
            <path d="M12 14a3 3 0 003-3V5a3 3 0 00-6 0v6a3 3 0 003 3z" />
            <path d="M19 11a7 7 0 01-14 0H3a9 9 0 0018 0h-2z" />
            <path d="M12 19v3M8 22h8" strokeWidth={2} stroke="currentColor" fill="none" strokeLinecap="round" />
        </svg>
        <div
            className="mic-pulse"
            style={{
                transform: `scale(${1 + level * 0.5})`,
                opacity: 0.3 + level * 0.5
            }}
        />
    </div>
);

const SpeakingIcon = () => (
    <svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
            d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15H4a1 1 0 01-1-1v-4a1 1 0 011-1h1.586l4.707-4.707C10.923 3.663 12 4.109 12 5v14c0 .891-1.077 1.337-1.707.707L5.586 15z" />
    </svg>
);

export default VoiceInput;
