import React, { useState, useEffect, useRef } from 'react';
import { Scissors, TrendingUp, MessageSquare, Sparkles, Clock, AudioWaveform } from 'lucide-react';

export const HeroVideoAnimation = () => {
  const [animationState, setAnimationState] = useState('raw');
  const videoRef = useRef(null);
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    const timeline = [
      { state: 'raw', duration: 2500 },
      { state: 'suggestions', duration: 5000 },
      { state: 'editing', duration: 3000 },
      { state: 'final', duration: 2500 },
      { state: 'loop', duration: 1000 }
    ];

    let currentIndex = 0;
    let startTime = Date.now();

    const animate = () => {
      const currentPhase = timeline[currentIndex];
      const elapsed = Date.now() - startTime;
      const phaseProgress = Math.min(elapsed / currentPhase.duration, 1);
      
      setProgress(phaseProgress);

      if (elapsed >= currentPhase.duration) {
        currentIndex = (currentIndex + 1) % timeline.length;
        startTime = Date.now();
        setAnimationState(timeline[currentIndex].state);
      }

      requestAnimationFrame(animate);
    };

    const animationFrame = requestAnimationFrame(animate);
    return () => cancelAnimationFrame(animationFrame);
  }, []);

  return (
    <div className="relative w-full max-w-md mx-auto h-[600px] flex items-center justify-center">
      {/* Floating Suggestions Around Phone */}
      {animationState === 'suggestions' && (
        <>
          {/* Format/Hook Guidance - Top Left */}
          <div 
            className="absolute top-0 left-0 glass-card p-3 rounded-xl border border-primary/30 shadow-xl max-w-[200px] z-20"
            style={{
              animation: 'slide-in-left 0.6s ease-out',
              animationDelay: '0.3s',
              animationFillMode: 'backwards'
            }}
          >
            <div className="flex items-start gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary/20 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
              <div>
                <p className="text-foreground text-xs font-sans font-semibold">Format Match</p>
                <p className="text-muted-foreground text-[10px] font-sans">YC Demo Day Classic</p>
              </div>
            </div>
          </div>

          {/* Cut Suggestions - Top Right */}
          <div 
            className="absolute top-8 right-0 glass-card p-3 rounded-xl border border-secondary/30 shadow-xl max-w-[200px] z-20"
            style={{
              animation: 'slide-in-right 0.6s ease-out',
              animationDelay: '0.8s',
              animationFillMode: 'backwards'
            }}
          >
            <div className="flex items-start gap-2">
              <div className="w-8 h-8 rounded-lg bg-secondary/20 flex items-center justify-center flex-shrink-0">
                <Scissors className="w-4 h-4 text-secondary" />
              </div>
              <div>
                <p className="text-foreground text-xs font-sans font-semibold">Cut Suggestions</p>
                <p className="text-muted-foreground text-[10px] font-sans">3 optimal cuts detected</p>
              </div>
            </div>
          </div>

          {/* Trending Audio - Bottom Left */}
          <div 
            className="absolute bottom-16 left-0 glass-card p-3 rounded-xl border border-accent/30 shadow-xl max-w-[200px] z-20"
            style={{
              animation: 'slide-in-left 0.6s ease-out',
              animationDelay: '1.3s',
              animationFillMode: 'backwards'
            }}
          >
            <div className="flex items-start gap-2">
              <div className="w-8 h-8 rounded-lg bg-accent/20 flex items-center justify-center flex-shrink-0">
                <TrendingUp className="w-4 h-4 text-accent-foreground" />
              </div>
              <div>
                <p className="text-foreground text-xs font-sans font-semibold">Trending Audio</p>
                <p className="text-muted-foreground text-[10px] font-sans">Upbeat energetic track</p>
              </div>
            </div>
          </div>
        </>
      )}

      {/* Phone Mockup Container - Smaller Size */}
      <div className="relative z-10">
        {/* Phone Frame */}
        <div className="relative bg-card rounded-[2rem] p-2 shadow-2xl border-[8px] border-card w-[240px]">
          {/* Notch */}
          <div className="absolute top-0 left-1/2 -translate-x-1/2 w-20 h-4 bg-card rounded-b-2xl z-10"></div>
          
          {/* Screen Container */}
          <div className="relative bg-background rounded-[1.5rem] overflow-hidden aspect-[9/16]">
            {/* Video */}
            <video
              ref={videoRef}
              className="absolute inset-0 w-full h-full object-cover"
              src="/demo-video.MOV"
              autoPlay
              loop
              muted
              playsInline
            />

            {/* Overlay Effects */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Raw State - Minimal timeline */}
              {(animationState === 'raw' || animationState === 'loop') && (
                <div 
                  className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2 animate-fade-in"
                  style={{
                    animation: animationState === 'loop' ? 'fade-out 1s ease-out' : 'fade-in 0.6s ease-out'
                  }}
                >
                  <div className="w-full h-0.5 bg-white/20 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-white rounded-full transition-all duration-300"
                      style={{ width: `${progress * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Suggestions State - Timeline with markers inside phone */}
              {animationState === 'suggestions' && (
                <div className="absolute inset-0 animate-fade-in z-10">
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 z-10">
                    <div className="relative">
                      <div className="relative w-full h-1 bg-white/30 rounded-full overflow-hidden">
                        <div className="absolute left-[20%] top-0 w-0.5 h-full bg-accent shadow-glow-neon" />
                        <div className="absolute left-[45%] top-0 w-0.5 h-full bg-accent shadow-glow-neon" />
                        <div className="absolute left-[70%] top-0 w-0.5 h-full bg-accent shadow-glow-neon" />
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Editing State */}
              {animationState === 'editing' && (
                <div className="absolute inset-0 animate-fade-in">
                  {/* Text caption */}
                  <div 
                    className="absolute top-1/2 left-2 right-2 -translate-y-1/2 text-center"
                    style={{
                      animation: 'scale-in 0.4s ease-out',
                      animationDelay: '0.2s',
                      animationFillMode: 'backwards'
                    }}
                  >
                    <div className="inline-block bg-white/95 backdrop-blur-sm px-3 py-1.5 rounded-xl shadow-lg border border-primary/20">
                      <p className="text-foreground text-[10px] font-sans font-bold">When it finally works 🤯</p>
                    </div>
                  </div>

                  {/* Timeline with glowing markers */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                    <div className="relative w-full h-1 bg-white/20 rounded-full overflow-hidden">
                      <div className="absolute inset-0 bg-gradient-to-r from-primary via-secondary to-accent opacity-50 animate-shimmer" />
                      <div className="absolute left-[20%] top-0 w-1 h-full bg-primary rounded-full shadow-glow animate-pulse-glow" />
                      <div className="absolute left-[45%] top-0 w-1 h-full bg-secondary rounded-full shadow-glow animate-pulse-glow" style={{ animationDelay: '0.2s' }} />
                      <div className="absolute left-[70%] top-0 w-1 h-full bg-accent rounded-full shadow-glow-neon animate-pulse-glow" style={{ animationDelay: '0.4s' }} />
                    </div>
                  </div>

                  {/* Music waveform */}
                  <div 
                    className="absolute top-2 left-2 right-2 glass-card p-1 rounded-lg border border-white/20"
                    style={{
                      animation: 'fade-in 0.6s ease-out',
                      animationDelay: '0.5s',
                      animationFillMode: 'backwards'
                    }}
                  >
                    <div className="flex items-center gap-1">
                      <AudioWaveform className="w-3 h-3 text-white" />
                      <div className="flex-1 flex items-end gap-0.5 h-3">
                        {[3, 7, 4, 8, 5, 9, 6, 4, 7, 3, 5, 8].map((height, i) => (
                          <div
                            key={i}
                            className="flex-1 bg-primary/60 rounded-full transition-all duration-200"
                            style={{
                              height: `${height * 8}%`,
                              animation: `wave-pulse 0.8s ease-in-out infinite`,
                              animationDelay: `${i * 0.05}s`
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Final State */}
              {animationState === 'final' && (
                <div 
                  className="absolute inset-0 animate-fade-in"
                  style={{
                    animation: 'fade-in 0.6s ease-out'
                  }}
                >
                  <div className="absolute top-2 left-1/2 -translate-x-1/2 glass-card px-2 py-1 rounded-full border border-primary/30 shadow-lg">
                    <div className="flex items-center gap-1">
                      <div className="w-1.5 h-1.5 bg-primary rounded-full" />
                      <span className="text-foreground text-[10px] font-sans font-semibold">Optimized</span>
                    </div>
                  </div>

                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                    <div className="w-full h-0.5 bg-white/20 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-primary to-secondary rounded-full"
                        style={{ width: `${progress * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Glow effect behind phone */}
        <div className="absolute -inset-3 bg-gradient-to-br from-primary/20 via-secondary/10 to-accent/20 blur-2xl -z-10 animate-pulse-glow" />
      </div>

      {/* Phase indicator dots */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 flex justify-center gap-1.5">
        {['raw', 'suggestions', 'editing', 'final'].map((state) => (
          <div
            key={state}
            className={`w-1.5 h-1.5 rounded-full transition-all duration-300 ${
              animationState === state
                ? 'bg-primary w-6'
                : 'bg-muted-foreground/30'
            }`}
          />
        ))}
      </div>
    </div>
  );
};
