import React, { useState, useRef, useEffect } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { Avatar, AvatarFallback } from './ui/avatar';
import { Sparkles, Upload, X, Send, Video, Image as ImageIcon, FileText, Paperclip, TrendingUp, Wand2, Zap, Rocket, Target, Film, Scissors } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';

export const Workspace = () => {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hey there! 🎬 I\'m your AI content director. Upload your video or footage, and I\'ll coach you through every cut, transition, and creative decision to make it go viral.',
      timestamp: new Date()
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const fileInputRef = useRef(null);
  const textareaRef = useRef(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const quickPrompts = [
    { icon: <Scissors className="w-4 h-4" />, text: 'Direct my cuts and pacing', color: 'bg-primary/10 text-primary border-primary/20' },
    { icon: <Film className="w-4 h-4" />, text: 'Coach my video structure', color: 'bg-secondary/10 text-secondary border-secondary/20' },
    { icon: <Zap className="w-4 h-4" />, text: 'Guide my creative decisions', color: 'bg-accent/20 text-foreground border-accent/30' },
  ];

  const handleFileSelect = (e) => {
    const files = Array.from(e.target.files || []);
    handleFiles(files);
  };

  const handleFiles = (files) => {
    const validFiles = files.filter(file => {
      const isImage = file.type.startsWith('image/');
      const isVideo = file.type.startsWith('video/');
      return isImage || isVideo;
    });

    if (validFiles.length === 0) {
      toast.error('Please upload images or videos only');
      return;
    }

    const newFiles = validFiles.map(file => ({
      id: Math.random().toString(36).substr(2, 9),
      file,
      name: file.name,
      type: file.type.startsWith('image/') ? 'image' : 'video',
      size: (file.size / 1024 / 1024).toFixed(2),
      url: URL.createObjectURL(file)
    }));

    setUploadedFiles(prev => [...prev, ...newFiles]);
    toast.success(`${newFiles.length} file(s) uploaded! 🎉`);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = Array.from(e.dataTransfer.files);
    handleFiles(files);
  };

  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('File removed');
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim() && uploadedFiles.length === 0) {
      toast.error('Please add a message or upload files');
      return;
    }

    const userMessage = {
      role: 'user',
      content: inputValue.trim(),
      files: uploadedFiles,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setUploadedFiles([]);
    setIsProcessing(true);

    setTimeout(() => {
      const aiResponse = generateMockResponse(userMessage);
      setMessages(prev => [...prev, aiResponse]);
      setIsProcessing(false);
      toast.success('Direction ready! 🎬', { description: 'Follow my coaching below.' });
    }, 2000);
  };

  const generateMockResponse = (userMessage) => {
    const hasVideo = userMessage.files?.some(f => f.type === 'video');
    const hasImage = userMessage.files?.some(f => f.type === 'image');

    let response = '';

    if (hasVideo) {
      response = `🎬 **Let's Direct This Video!**\n\nI've analyzed your footage against viral formats. Here's your step-by-step direction:\n\n**🎯 Viral Format: "Hook + Payoff + CTA"**\n- Current trend shelf-life: 🔥 2-3 weeks\n- Best platforms: TikTok, Instagram Reels\n\n**🎬 Shot-by-Shot Direction:**\n\n**CUT 1 (0-3s): The Hook**\n→ Start with close-up of your face\n→ First words: "I built [X] so you don't have to..."\n→ Cut on the word "have" for emphasis\n\n**CUT 2-4 (3-8s): The Problem**\n→ B-roll of the struggle (2-3 second cuts)\n→ Keep text overlay in upper third\n→ Add subtle zoom on each transition\n\n**CUT 5-7 (8-15s): The Payoff**\n→ Show the solution/result\n→ Faster cuts here (1.5-2 seconds each)\n→ End with your product/app in action\n\n**FINAL CUT (15-18s): The CTA**\n→ Back to face, direct eye contact\n→ "Link in bio" or "Follow for more"\n\n**✨ Caption Direction:**\n"POV: You found the hack everyone's been hiding 🤫"\n\n**#️⃣ Hashtags:**\n#contentcreator #viral #tutorial #lifehack\n\nReady to make these cuts? I'll coach you through each one!`;
    } else if (hasImage) {
      response = `🖼️ **Let's Direct This Visual!**\n\nHere's how I'll coach you to maximize engagement:\n\n**🎯 Production Direction:**\n\n**Step 1: Text Overlay**\n→ Add hook text in bold, contrasting color\n→ Position: Upper or lower third (never center)\n→ Font: Sans-serif, 60-80pt\n\n**Step 2: Create Movement**\n→ Option A: Turn into carousel (3-5 slides)\n→ Option B: Use as Reels cover with voiceover\n→ Option C: Add zoom/pan animation\n\n**Step 3: Caption Strategy**\nPick one of these proven hooks:\n1. "Stop scrolling. You need to see this."\n2. "Everyone's doing [X] wrong. Here's the right way."\n3. "This changed everything for me..."\n\n**📱 Platform Direction:**\n- **Instagram:** 4-slide carousel (swipe rate +45%)\n- **TikTok:** Use as thumbnail, add voiceover\n- **YouTube Shorts:** Combine with quick tutorial\n\nLet me know which direction you want to take, and I'll coach you through it!`;
    } else {
      response = `🎬 **Ready to Direct Your Content!**\n\nI'm here to coach you through the entire production process. Here's how we'll work together:\n\n**🎯 What I'll Direct:**\n✓ Shot composition and framing\n✓ Cut timing and pacing\n✓ Transition choices\n✓ Hook structure (first 3 seconds)\n✓ B-roll placement\n✓ Caption and text overlay positioning\n✓ Audio/music cues\n✓ Call-to-action delivery\n\n**🔥 Trending Formats I'll Coach You Through:**\n\n1. **"Episode 1 of [X]"** - Series starter\n   → I'll direct your intro, pacing, and cliffhanger\n\n2. **"POV: [Situation]"** - Relatable scenarios\n   → I'll guide your cuts to match emotional beats\n\n3. **"I tested [X] so you don't have to"** - Tutorial style\n   → I'll coach your demonstration flow and reveals\n\n**📤 Let's Start:**\nUpload your footage or describe what you want to create, and tell me:\n- Target platform (TikTok/Instagram/YouTube)\n- Your niche or topic\n- What you want viewers to do\n\nI'll give you shot-by-shot direction to make it viral!`;
    }

    return {
      role: 'assistant',
      content: response,
      timestamp: new Date()
    };
  };

  const handleQuickPrompt = (promptText) => {
    setInputValue(promptText);
    textareaRef.current?.focus();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-sky relative overflow-hidden gradient-bg-dynamic">
      {/* Dynamic gradient orbs */}
      <div className="gradient-orb-1"></div>
      <div className="gradient-orb-2"></div>
      <div className="gradient-orb-3"></div>
      
      {/* Floating decorative stickers */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-10">
        <div className="floating-sticker top-20 left-[8%] text-5xl animate-float" style={{ animationDelay: '0s' }}>✨</div>
        <div className="floating-sticker top-32 right-[12%] text-4xl animate-float" style={{ animationDelay: '1.5s' }}>🎬</div>
        <div className="floating-sticker bottom-32 left-[15%] text-4xl animate-float" style={{ animationDelay: '3s' }}>🚀</div>
        <div className="floating-sticker top-[45%] right-[20%] text-3xl animate-float" style={{ animationDelay: '2s' }}>💡</div>
        <div className="floating-sticker bottom-24 right-[8%] text-4xl animate-float" style={{ animationDelay: '2.5s' }}>⚡</div>
        <div className="floating-sticker top-[60%] left-[5%] text-3xl animate-float" style={{ animationDelay: '1s' }}>🎯</div>
      </div>

      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button onClick={() => navigate('/')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-5xl font-logo font-bold text-foreground">filmit!</span>
            </button>
            <div className="flex items-center gap-4">
              <Badge className="hidden sm:flex bg-accent/20 text-foreground border-accent/30 hover:bg-accent/30 font-sans">
                <Film className="w-3 h-3 mr-1" />
                AI Director
              </Badge>
              <Avatar className="w-9 h-9 border-2 border-primary/20">
                <AvatarFallback className="bg-gradient-primary text-primary-foreground font-semibold">U</AvatarFallback>
              </Avatar>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8 relative z-10">
        <div className="space-y-6">
          {/* Welcome Card */}
          <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm animate-slide-up relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-primary/5 rounded-full blur-3xl"></div>
            <CardContent className="pt-6 relative">
              <div className="flex items-start gap-4">
                <div className="w-14 h-14 rounded-xl bg-gradient-primary flex items-center justify-center flex-shrink-0 shadow-md">
                  <Film className="w-7 h-7 text-primary-foreground" />
                </div>
                <div className="flex-1">
                  <h2 className="text-3xl font-display font-bold text-foreground mb-2">Your AI Content Director</h2>
                  <p className="text-muted-foreground leading-relaxed text-lg font-sans">
                    Upload your footage and I'll direct your content production—coaching you through every cut, transition, and creative decision based on viral formats.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Chat Messages */}
          <div className="space-y-4 animate-slide-up" style={{ animationDelay: '0.1s' }}>
            {messages.map((message, index) => (
              <div key={index} className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                {message.role === 'assistant' && (
                  <Avatar className="w-10 h-10 border-2 border-primary/20 flex-shrink-0">
                    <AvatarFallback className="bg-gradient-primary text-primary-foreground">
                      <Film className="w-5 h-5" />
                    </AvatarFallback>
                  </Avatar>
                )}
                
                <div className={`flex-1 max-w-3xl ${ message.role === 'user' ? 'flex flex-col items-end' : ''}`}>
                  <Card className={`${
                    message.role === 'user' 
                      ? 'bg-gradient-primary text-primary-foreground border-0 shadow-md' 
                      : 'bg-card/95 backdrop-blur-sm border-border/50 shadow-lg'
                  } card-lift`}>
                    <CardContent className="pt-4 pb-4">
                      {/* Uploaded Files */}
                      {message.files && message.files.length > 0 && (
                        <div className="mb-3 grid grid-cols-2 gap-2">
                          {message.files.map(file => (
                            <div key={file.id} className="relative rounded-lg overflow-hidden bg-muted/20 border border-border/30">
                              {file.type === 'image' ? (
                                <img src={file.url} alt={file.name} className="w-full h-32 object-cover" />
                              ) : (
                                <video src={file.url} className="w-full h-32 object-cover" />
                              )}
                              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-2">
                                <p className="text-xs text-white font-medium truncate">{file.name}</p>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Message Content */}
                      <div className={`prose prose-sm max-w-none ${
                        message.role === 'user' ? 'prose-invert' : ''
                      }`}>
                        {message.content.split('\n').map((line, i) => (
                          <p key={i} className="mb-2 last:mb-0 whitespace-pre-wrap font-sans leading-relaxed">{line}</p>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                  <span className="text-xs text-muted-foreground mt-1.5 font-sans">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>

                {message.role === 'user' && (
                  <Avatar className="w-10 h-10 border-2 border-primary/20 flex-shrink-0">
                    <AvatarFallback className="bg-muted text-muted-foreground font-semibold">U</AvatarFallback>
                  </Avatar>
                )}
              </div>
            ))}

            {/* Processing Indicator */}
            {isProcessing && (
              <div className="flex gap-3 justify-start animate-bounce-in">
                <Avatar className="w-10 h-10 border-2 border-primary/20">
                  <AvatarFallback className="bg-gradient-primary text-primary-foreground">
                    <Film className="w-5 h-5" />
                  </AvatarFallback>
                </Avatar>
                <Card className="bg-card/95 backdrop-blur-sm border-border/50 shadow-lg">
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-center gap-2">
                      <div className="flex gap-1">
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0s' }}></div>
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                        <div className="w-2 h-2 rounded-full bg-primary animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                      </div>
                      <span className="text-sm text-muted-foreground font-sans">Preparing your direction...</span>
                    </div>
                  </CardContent>
                </Card>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <Card className="border-border/50 shadow-xl bg-card/95 backdrop-blur-sm sticky bottom-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <CardContent className="pt-6">
              {/* Quick Prompts */}
              {messages.length <= 2 && (
                <div className="mb-4">
                  <p className="text-sm text-muted-foreground mb-3 font-sans font-medium">Quick prompts:</p>
                  <div className="flex flex-wrap gap-2">
                    {quickPrompts.map((prompt, i) => (
                      <Button
                        key={i}
                        variant="outline"
                        size="sm"
                        onClick={() => handleQuickPrompt(prompt.text)}
                        className={`${prompt.color} hover:scale-105 transition-all duration-300 font-sans`}
                      >
                        {prompt.icon}
                        <span className="ml-1.5">{prompt.text}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              )}

              {/* File Upload Area */}
              <div
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                className={`mb-4 border-2 border-dashed rounded-xl p-6 transition-all duration-300 ${
                  isDragging 
                    ? 'border-primary bg-primary/5 scale-[1.01] shadow-glow' 
                    : 'border-border/50 hover:border-border hover:bg-muted/20'
                }`}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  multiple
                  accept="image/*,video/*"
                  onChange={handleFileSelect}
                  className="hidden"
                />
                
                {uploadedFiles.length === 0 ? (
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="w-full flex flex-col items-center justify-center gap-2 group"
                  >
                    <div className="w-14 h-14 rounded-xl bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-all duration-300 group-hover:scale-110">
                      <Upload className="w-7 h-7 text-primary" />
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-semibold text-foreground font-sans">Drop your footage here or click to browse</p>
                      <p className="text-xs text-muted-foreground mt-1 font-sans">Upload videos or images • Max 50MB</p>
                    </div>
                  </button>
                ) : (
                  <div className="space-y-3">
                    <div className="flex items-center justify-between mb-3">
                      <p className="text-sm font-semibold text-foreground font-sans flex items-center gap-2">
                        <Badge variant="secondary" className="font-sans">{uploadedFiles.length}</Badge>
                        file(s) uploaded
                      </p>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => fileInputRef.current?.click()}
                        className="font-sans hover:bg-primary/10"
                      >
                        <Paperclip className="w-4 h-4 mr-1" />
                        Add more
                      </Button>
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
                      {uploadedFiles.map(file => (
                        <div key={file.id} className="relative group rounded-lg overflow-hidden border border-border/50 card-lift">
                          {file.type === 'image' ? (
                            <img src={file.url} alt={file.name} className="w-full h-24 object-cover" />
                          ) : (
                            <div className="w-full h-24 bg-muted flex items-center justify-center">
                              <Video className="w-8 h-8 text-muted-foreground" />
                            </div>
                          )}
                          <button
                            onClick={() => removeFile(file.id)}
                            className="absolute top-1 right-1 w-6 h-6 rounded-full bg-destructive text-destructive-foreground opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center hover:scale-110"
                          >
                            <X className="w-4 h-4" />
                          </button>
                          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/60 to-transparent p-1.5">
                            <p className="text-xs text-white font-medium truncate">{file.name}</p>
                            <p className="text-xs text-white/70">{file.size} MB</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Text Input */}
              <div className="flex gap-2">
                <Textarea
                  ref={textareaRef}
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Tell me what you're creating... (e.g., 'I need direction for a TikTok about language learning apps')"
                  className="min-h-[80px] resize-none focus:ring-primary font-sans text-base"
                  disabled={isProcessing}
                />
                <Button
                  onClick={handleSendMessage}
                  disabled={isProcessing || (!inputValue.trim() && uploadedFiles.length === 0)}
                  className="bg-gradient-primary hover:shadow-glow self-end px-5 h-[80px] transition-all duration-300"
                >
                  <Send className="w-5 h-5" />
                </Button>
              </div>

              <p className="text-xs text-muted-foreground mt-2 font-sans">
                <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">Enter</kbd> to send, <kbd className="px-1.5 py-0.5 rounded bg-muted text-muted-foreground text-xs">Shift + Enter</kbd> for new line
              </p>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
};