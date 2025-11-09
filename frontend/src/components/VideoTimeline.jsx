import React, { useState, useRef, useEffect } from 'react';
import { Card, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  Play, Pause, SkipBack, SkipForward, Scissors, Download, 
  ExternalLink, Zap, AlertCircle 
} from 'lucide-react';
import { toast } from 'sonner';

export const VideoTimeline = ({ videoUrl, timestampSuggestions = [], onExport }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const videoRef = useRef(null);
  const timelineRef = useRef(null);

  useEffect(() => {
    const video = videoRef.current;
    if (!video) return;

    const handleTimeUpdate = () => {
      if (!isDragging) {
        setCurrentTime(video.currentTime);
      }
    };

    const handleLoadedMetadata = () => {
      setDuration(video.duration);
    };

    const handleEnded = () => {
      setIsPlaying(false);
    };

    video.addEventListener('timeupdate', handleTimeUpdate);
    video.addEventListener('loadedmetadata', handleLoadedMetadata);
    video.addEventListener('ended', handleEnded);

    return () => {
      video.removeEventListener('timeupdate', handleTimeUpdate);
      video.removeEventListener('loadedmetadata', handleLoadedMetadata);
      video.removeEventListener('ended', handleEnded);
    };
  }, [isDragging]);

  const togglePlayPause = () => {
    const video = videoRef.current;
    if (!video) return;

    if (isPlaying) {
      video.pause();
    } else {
      video.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimelineClick = (e) => {
    const timeline = timelineRef.current;
    const video = videoRef.current;
    if (!timeline || !video) return;

    const rect = timeline.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = x / rect.width;
    const newTime = percentage * duration;

    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleTimelineDrag = (e) => {
    if (!isDragging) return;
    handleTimelineClick(e);
  };

  const skipTime = (seconds) => {
    const video = videoRef.current;
    if (!video) return;

    const newTime = Math.max(0, Math.min(duration, currentTime + seconds));
    video.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const jumpToMarker = (timestamp) => {
    const video = videoRef.current;
    if (!video) return;

    video.currentTime = timestamp;
    setCurrentTime(timestamp);
    
    // Auto-play for preview
    if (!isPlaying) {
      video.play();
      setIsPlaying(true);
    }
  };

  const formatTime = (seconds) => {
    if (!seconds || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getMarkerPosition = (timestamp) => {
    if (!duration) return 0;
    return (timestamp / duration) * 100;
  };

  const exportToEditor = (platform) => {
    const exportData = {
      videoUrl,
      duration,
      markers: timestampSuggestions.map(s => ({
        time: s.timestamp,
        type: s.action,
        description: s.description
      }))
    };

    // Generate export instructions
    let instructions = '';
    if (platform === 'capcut') {
      instructions = generateCapCutInstructions(timestampSuggestions);
    } else if (platform === 'imovie') {
      instructions = generateiMovieInstructions(timestampSuggestions);
    } else if (platform === 'premierepro') {
      instructions = generatePremiereProInstructions(timestampSuggestions);
    }

    // Copy to clipboard
    navigator.clipboard.writeText(instructions);
    toast.success(`${platform.toUpperCase()} instructions copied!`, {
      description: 'Paste into your editor notes'
    });

    if (onExport) {
      onExport(platform, exportData);
    }
  };

  const generateCapCutInstructions = (suggestions) => {
    let instructions = '📱 CapCut Editing Instructions\n\n';
    instructions += '1. Import your video into CapCut\n';
    instructions += '2. Follow these timestamped edits:\n\n';
    
    suggestions.forEach((s, i) => {
      instructions += `${i + 1}. At ${formatTime(s.timestamp)}:\n`;
      instructions += `   Action: ${s.action}\n`;
      instructions += `   ${s.description}\n\n`;
    });
    
    return instructions;
  };

  const generateiMovieInstructions = (suggestions) => {
    let instructions = '🎬 iMovie Editing Instructions\n\n';
    instructions += '1. Import your video into iMovie\n';
    instructions += '2. Use these markers for editing:\n\n';
    
    suggestions.forEach((s, i) => {
      instructions += `Marker ${i + 1} - ${formatTime(s.timestamp)}: ${s.action}\n`;
      instructions += `${s.description}\n\n`;
    });
    
    return instructions;
  };

  const generatePremiereProInstructions = (suggestions) => {
    let instructions = '🎥 Adobe Premiere Pro Editing Instructions\n\n';
    instructions += 'Markers to add:\n\n';
    
    suggestions.forEach((s, i) => {
      instructions += `${formatTime(s.timestamp)} - ${s.action}: ${s.description}\n`;
    });
    
    return instructions;
  };

  const getMarkerColor = (action) => {
    switch (action?.toLowerCase()) {
      case 'cut': return 'bg-red-500';
      case 'trim': return 'bg-orange-500';
      case 'add_text': return 'bg-blue-500';
      case 'transition': return 'bg-purple-500';
      case 'emphasis': return 'bg-yellow-500';
      default: return 'bg-primary';
    }
  };

  return (
    <Card className="border-border/50 shadow-lg bg-card/95 backdrop-blur-sm">
      <CardContent className="pt-6 space-y-4">
        {/* Video Player */}
        <div className="relative rounded-lg overflow-hidden bg-black">
          <video
            ref={videoRef}
            src={videoUrl}
            className="w-full h-auto max-h-[400px] object-contain"
            onClick={togglePlayPause}
          />
          
          {/* Play/Pause Overlay */}
          {!isPlaying && (
            <div 
              className="absolute inset-0 flex items-center justify-center bg-black/20 cursor-pointer"
              onClick={togglePlayPause}
            >
              <div className="w-20 h-20 rounded-full bg-primary/90 flex items-center justify-center hover:bg-primary transition-all">
                <Play className="w-10 h-10 text-primary-foreground ml-1" />
              </div>
            </div>
          )}
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="outline"
              onClick={() => skipTime(-5)}
              className="hover:bg-muted"
            >
              <SkipBack className="w-4 h-4" />
            </Button>
            
            <Button
              size="sm"
              onClick={togglePlayPause}
              className="bg-gradient-primary hover:shadow-glow"
            >
              {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4 ml-0.5" />}
            </Button>
            
            <Button
              size="sm"
              variant="outline"
              onClick={() => skipTime(5)}
              className="hover:bg-muted"
            >
              <SkipForward className="w-4 h-4" />
            </Button>
          </div>

          <div className="flex items-center gap-2 text-sm font-mono text-muted-foreground">
            <span>{formatTime(currentTime)}</span>
            <span>/</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Timeline with Markers */}
        <div className="space-y-2">
          <div
            ref={timelineRef}
            className="relative h-12 bg-muted rounded-lg cursor-pointer group"
            onClick={handleTimelineClick}
            onMouseDown={() => setIsDragging(true)}
            onMouseUp={() => setIsDragging(false)}
            onMouseMove={handleTimelineDrag}
            onMouseLeave={() => setIsDragging(false)}
          >
            {/* Progress Bar */}
            <div 
              className="absolute top-0 left-0 h-full bg-gradient-primary rounded-lg transition-all"
              style={{ width: `${(currentTime / duration) * 100}%` }}
            ></div>

            {/* Markers */}
            {timestampSuggestions.map((suggestion, index) => {
              const position = getMarkerPosition(suggestion.timestamp);
              return (
                <div
                  key={index}
                  className="absolute top-0 h-full flex flex-col items-center cursor-pointer hover:z-10 group/marker"
                  style={{ left: `${position}%` }}
                  onClick={(e) => {
                    e.stopPropagation();
                    jumpToMarker(suggestion.timestamp);
                  }}
                >
                  {/* Marker Line */}
                  <div className={`w-1 h-full ${getMarkerColor(suggestion.action)} opacity-70 group-hover/marker:opacity-100 transition-opacity`}></div>
                  
                  {/* Marker Icon */}
                  <div className={`absolute -top-2 w-6 h-6 rounded-full ${getMarkerColor(suggestion.action)} border-2 border-background flex items-center justify-center transform -translate-x-1/2 left-1/2 shadow-lg group-hover/marker:scale-125 transition-transform`}>
                    <Scissors className="w-3 h-3 text-white" />
                  </div>

                  {/* Tooltip */}
                  <div className="absolute -top-16 left-1/2 transform -translate-x-1/2 bg-popover border border-border rounded-lg px-3 py-2 shadow-xl opacity-0 group-hover/marker:opacity-100 transition-opacity pointer-events-none whitespace-nowrap z-20">
                    <p className="text-xs font-semibold text-foreground">{formatTime(suggestion.timestamp)}</p>
                    <p className="text-xs text-muted-foreground">{suggestion.action}</p>
                  </div>
                </div>
              );
            })}

            {/* Playhead */}
            <div 
              className="absolute top-0 h-full w-0.5 bg-foreground shadow-lg transform -translate-x-1/2"
              style={{ left: `${(currentTime / duration) * 100}%` }}
            >
              <div className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-foreground rounded-full border-2 border-background"></div>
            </div>
          </div>

          {/* Legend */}
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="text-muted-foreground font-semibold">Markers:</span>
            <Badge variant="outline" className="bg-red-500/10 border-red-500/30 text-red-700">
              <div className="w-2 h-2 rounded-full bg-red-500 mr-1"></div>
              Cut
            </Badge>
            <Badge variant="outline" className="bg-orange-500/10 border-orange-500/30 text-orange-700">
              <div className="w-2 h-2 rounded-full bg-orange-500 mr-1"></div>
              Trim
            </Badge>
            <Badge variant="outline" className="bg-blue-500/10 border-blue-500/30 text-blue-700">
              <div className="w-2 h-2 rounded-full bg-blue-500 mr-1"></div>
              Add Text
            </Badge>
            <Badge variant="outline" className="bg-purple-500/10 border-purple-500/30 text-purple-700">
              <div className="w-2 h-2 rounded-full bg-purple-500 mr-1"></div>
              Transition
            </Badge>
            <Badge variant="outline" className="bg-yellow-500/10 border-yellow-500/30 text-yellow-700">
              <div className="w-2 h-2 rounded-full bg-yellow-500 mr-1"></div>
              Emphasis
            </Badge>
          </div>
        </div>

        {/* Export Options */}
        {timestampSuggestions.length > 0 && (
          <div className="pt-4 border-t border-border/50">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <Download className="w-4 h-4 text-primary" />
                <span className="text-sm font-semibold text-foreground">Export to Editor:</span>
              </div>
              <Badge variant="secondary" className="text-xs">
                {timestampSuggestions.length} markers
              </Badge>
            </div>
            
            <div className="flex flex-wrap gap-2">
              <Button
                size="sm"
                variant="outline"
                onClick={() => exportToEditor('capcut')}
                className="hover:bg-primary/10 hover:border-primary/30"
              >
                <ExternalLink className="w-3 h-3 mr-1.5" />
                CapCut
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => exportToEditor('imovie')}
                className="hover:bg-primary/10 hover:border-primary/30"
              >
                <ExternalLink className="w-3 h-3 mr-1.5" />
                iMovie
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => exportToEditor('premierepro')}
                className="hover:bg-primary/10 hover:border-primary/30"
              >
                <ExternalLink className="w-3 h-3 mr-1.5" />
                Premiere Pro
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => exportToEditor('generic')}
                className="hover:bg-primary/10 hover:border-primary/30"
              >
                <ExternalLink className="w-3 h-3 mr-1.5" />
                Copy All
              </Button>
            </div>
          </div>
        )}

        {/* Info */}
        <div className="flex items-start gap-2 p-3 bg-muted/30 rounded-lg">
          <AlertCircle className="w-4 h-4 text-muted-foreground mt-0.5 flex-shrink-0" />
          <p className="text-xs text-muted-foreground leading-relaxed">
            Click markers to jump to that timestamp. Use export buttons to copy editing instructions for your preferred video editor.
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
