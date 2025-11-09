import React, { useState, useRef, useEffect } from 'react';
import { Music, Play, Pause, Download, RefreshCw, Sparkles, Loader2 } from 'lucide-react';
import { generateMusic, getMusicInfo, getMusicUrl } from '../utils/api';

const MusicSection = ({ projectId }) => {
  const [prompt, setPrompt] = useState('');
  const [duration, setDuration] = useState(30);
  const [isGenerating, setIsGenerating] = useState(false);
  const [musicData, setMusicData] = useState(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const audioRef = useRef(null);

  // Load existing music info on mount
  useEffect(() => {
    loadMusicInfo();
  }, [projectId]);

  const loadMusicInfo = async () => {
    try {
      const info = await getMusicInfo(projectId);
      if (info.has_music) {
        setMusicData({
          filename: info.filename,
          prompt: info.prompt,
          duration_seconds: info.duration_seconds,
          url: getMusicUrl(projectId, info.filename)
        });
        setPrompt(info.prompt);
        setDuration(info.duration_seconds);
      }
    } catch (error) {
      console.error('Error loading music info:', error);
    }
  };

  const handleGenerateMusic = async () => {
    if (!prompt.trim()) {
      alert('Please enter a music prompt');
      return;
    }

    setIsGenerating(true);
    try {
      const result = await generateMusic(projectId, prompt, duration);
      
      if (result.success) {
        // Update music data
        const musicUrl = getMusicUrl(projectId, result.filename);
        setMusicData({
          filename: result.filename,
          prompt: prompt,
          duration_seconds: result.duration_seconds,
          url: musicUrl
        });

        // Reset audio player
        setIsPlaying(false);
        setCurrentTime(0);
      }
    } catch (error) {
      console.error('Error generating music:', error);
      alert(`Failed to generate music: ${error.message}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handlePlayPause = () => {
    if (!audioRef.current) return;

    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
    }
  };

  const handleSeek = (e) => {
    const seekTime = parseFloat(e.target.value);
    if (audioRef.current) {
      audioRef.current.currentTime = seekTime;
      setCurrentTime(seekTime);
    }
  };

  const handleDownload = () => {
    if (!musicData) return;
    
    const link = document.createElement('a');
    link.href = musicData.url;
    link.download = musicData.filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6 mt-6">
      {/* Header */}
      <div className="flex items-center gap-3 mb-6">
        <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-2 rounded-lg">
          <Music className="text-white" size={24} />
        </div>
        <div>
          <h3 className="text-xl font-bold text-gray-900">Background Music</h3>
          <p className="text-sm text-gray-500">Generate AI music for your video</p>
        </div>
      </div>

      {/* Prompt Input */}
      <div className="mb-4">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Music Description
        </label>
        <textarea
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          placeholder="Describe the music you want... e.g., 'Create an upbeat electronic track with energetic vibes for a tech demo video'"
          className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none"
          rows={3}
          disabled={isGenerating}
        />
      </div>

      {/* Duration Selector */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-gray-700 mb-2">
          Duration
        </label>
        <div className="flex gap-2">
          {[10, 20, 30, 60].map((sec) => (
            <button
              key={sec}
              onClick={() => setDuration(sec)}
              disabled={isGenerating}
              className={`flex-1 px-4 py-2 rounded-lg font-medium transition-all ${
                duration === sec
                  ? 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-md'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              } ${isGenerating ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              {sec}s
            </button>
          ))}
        </div>
      </div>

      {/* Generate Button */}
      <button
        onClick={handleGenerateMusic}
        disabled={isGenerating || !prompt.trim()}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-all flex items-center justify-center gap-2 ${
          isGenerating || !prompt.trim()
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 shadow-lg hover:shadow-xl'
        }`}
      >
        {isGenerating ? (
          <>
            <Loader2 className="animate-spin" size={20} />
            Generating Music...
          </>
        ) : musicData ? (
          <>
            <RefreshCw size={20} />
            Regenerate Music
          </>
        ) : (
          <>
            <Sparkles size={20} />
            Generate Music
          </>
        )}
      </button>

      {/* Music Player */}
      {musicData && (
        <div className="mt-6 p-4 bg-gradient-to-r from-purple-50 to-pink-50 rounded-lg border border-purple-200">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Music className="text-purple-600" size={18} />
              <span className="text-sm font-semibold text-gray-700">Generated Music</span>
            </div>
            <span className="text-xs text-gray-500">{musicData.duration_seconds}s</span>
          </div>

          {/* Audio Element */}
          <audio
            ref={audioRef}
            src={musicData.url}
            onTimeUpdate={handleTimeUpdate}
            onEnded={() => setIsPlaying(false)}
            onLoadedMetadata={(e) => {
              // Update duration from actual audio file
              if (e.target.duration) {
                setMusicData(prev => ({
                  ...prev,
                  duration_seconds: e.target.duration
                }));
              }
            }}
          />

          {/* Waveform Visualization */}
          <div className="mb-3">
            <input
              type="range"
              min="0"
              max={musicData.duration_seconds || 0}
              step="0.1"
              value={currentTime}
              onChange={handleSeek}
              className="w-full h-2 bg-purple-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <div className="flex justify-between text-xs text-gray-600 mt-1">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(musicData.duration_seconds)}</span>
            </div>
          </div>

          {/* Controls */}
          <div className="flex items-center gap-2">
            <button
              onClick={handlePlayPause}
              className="flex-1 bg-purple-600 hover:bg-purple-700 text-white py-2 px-4 rounded-lg font-medium transition-all flex items-center justify-center gap-2"
            >
              {isPlaying ? (
                <>
                  <Pause size={18} />
                  Pause
                </>
              ) : (
                <>
                  <Play size={18} />
                  Play
                </>
              )}
            </button>
            <button
              onClick={handleDownload}
              className="bg-gray-200 hover:bg-gray-300 text-gray-700 py-2 px-4 rounded-lg font-medium transition-all flex items-center gap-2"
            >
              <Download size={18} />
              Download
            </button>
          </div>

          {/* Prompt Display */}
          <div className="mt-3 pt-3 border-t border-purple-200">
            <p className="text-xs text-gray-600">
              <span className="font-semibold">Prompt:</span> {musicData.prompt}
            </p>
          </div>
        </div>
      )}
    </div>
  );
};

export default MusicSection;
