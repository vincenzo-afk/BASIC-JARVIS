import React, { useEffect, useRef, useCallback } from 'react';

const Waveform = ({ isActive = false, color = '#22d3ee', barCount = 40 }) => {
    const canvasRef = useRef(null);
    const animationRef = useRef(null);
    const barsRef = useRef([]);
    const timeRef = useRef(0);

    // Initialize bars
    const initBars = useCallback(() => {
        barsRef.current = [];
        for (let i = 0; i < barCount; i++) {
            barsRef.current.push({
                height: 5 + Math.random() * 15,
                targetHeight: 10 + Math.random() * 30,
                velocity: 0,
                phase: Math.random() * Math.PI * 2
            });
        }
    }, [barCount]);

    useEffect(() => {
        initBars();
    }, [initBars]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        const barWidth = 4;
        const gap = 3;
        const totalWidth = barCount * (barWidth + gap);

        // Set canvas size
        canvas.width = totalWidth + 20;
        canvas.height = 80;

        const animate = () => {
            timeRef.current += 0.016; // ~60fps
            ctx.clearRect(0, 0, canvas.width, canvas.height);

            const centerY = canvas.height / 2;

            barsRef.current.forEach((bar, i) => {
                if (isActive) {
                    // Active state: Dynamic movement
                    const diff = bar.targetHeight - bar.height;
                    bar.velocity += diff * 0.15;
                    bar.velocity *= 0.75; // Damping
                    bar.height += bar.velocity;

                    // Randomly change target
                    if (Math.random() < 0.03) {
                        bar.targetHeight = 15 + Math.random() * 50;
                    }
                } else {
                    // Idle state: Gentle wave
                    const wave = Math.sin(timeRef.current * 1.5 + bar.phase + i * 0.15);
                    bar.height = 8 + wave * 5;
                }

                // Clamp height
                bar.height = Math.max(3, Math.min(bar.height, 60));

                const x = i * (barWidth + gap) + 10;
                const halfHeight = bar.height / 2;

                // Create gradient
                const gradient = ctx.createLinearGradient(
                    x, centerY - halfHeight,
                    x, centerY + halfHeight
                );

                const alpha = isActive ? 0.9 : 0.6;
                gradient.addColorStop(0, color);
                gradient.addColorStop(0.5, `${color}${Math.round(alpha * 255).toString(16).padStart(2, '0')}`);
                gradient.addColorStop(1, color);

                // Shadow glow
                ctx.shadowColor = color;
                ctx.shadowBlur = isActive ? 12 : 4;

                // Draw bar
                ctx.fillStyle = gradient;
                ctx.beginPath();

                // Rounded rectangle
                const radius = barWidth / 2;
                const top = centerY - halfHeight;
                const bottom = centerY + halfHeight;

                ctx.moveTo(x + radius, top);
                ctx.lineTo(x + barWidth - radius, top);
                ctx.quadraticCurveTo(x + barWidth, top, x + barWidth, top + radius);
                ctx.lineTo(x + barWidth, bottom - radius);
                ctx.quadraticCurveTo(x + barWidth, bottom, x + barWidth - radius, bottom);
                ctx.lineTo(x + radius, bottom);
                ctx.quadraticCurveTo(x, bottom, x, bottom - radius);
                ctx.lineTo(x, top + radius);
                ctx.quadraticCurveTo(x, top, x + radius, top);
                ctx.closePath();

                ctx.fill();
            });

            // Reset shadow
            ctx.shadowBlur = 0;

            animationRef.current = requestAnimationFrame(animate);
        };

        animate();

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [isActive, color, barCount]);

    return (
        <div className="waveform-container">
            <canvas
                ref={canvasRef}
                className={`waveform-canvas ${isActive ? 'active' : ''}`}
            />
            {isActive && (
                <div className="waveform-label">Listening...</div>
            )}
        </div>
    );
};

export default Waveform;
