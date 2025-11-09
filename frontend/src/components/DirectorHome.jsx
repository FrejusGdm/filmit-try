import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Textarea } from './ui/textarea';
import { Badge } from './ui/badge';
import { 
  Sparkles, Film, TrendingUp, Rocket, Video, Youtube, Instagram
} from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { createDirectorProject } from '../utils/api';
import { useAuth } from '../context/AuthContext';
import { UserMenu } from './UserMenu';

export const DirectorHome = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [prompt, setPrompt] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [hashtags, setHashtags] = useState('');
  const [references, setReferences] = useState('');

  // Default research seeds for each prompt type - these seed the deep research agent
  const defaultSeeds = {
    'yc_demo': {
      hashtags: '#startups #ycombinator #saas #productlaunch #techstartup',
      references: '@cluely @tryskribe @notion @linear @superhuman (viral YC demo videos & product launches)',
      keywords: 'cluely viral demo, YC demo day format, product launch video, startup pitch video'
    },
    'b2b_youtube': {
      hashtags: '#b2bsaas #productdemo #startups #enterprisesoftware #techexplained',
      references: '@loom @figma @notion @asana @slack (professional B2B product demos)',
      keywords: 'B2B product demo, software walkthrough, enterprise video, SaaS demo'
    },
    'instagram_tutorial': {
      hashtags: '#tutorial #howto #learnontiktok #educationalcontent #tiktoktutorial',
      references: '@mrbeast @mkbhd @levelstofame @teachingtech @skillshare (top tutorial creators)',
      keywords: 'Instagram reels tutorial, educational short video, how-to content'
    },
    'transformation': {
      hashtags: '#beforeandafter #transformation #results #glowup #progresspics',
      references: '@ootdfash @fashionblogger @styleinfluencer @glowup @fitnesstransformation (transformation content)',
      keywords: 'before after video, transformation reel, results video, progress video'
    }
  };

  const samplePrompts = [
    {
      text: "Build me a YC demo video like Cluely",
      icon: <Rocket className="w-4 h-4" />,
      details: "Fast-paced product launch for TikTok",
      color: "bg-pink-500/10 text-pink-600 border-pink-500/20 hover:bg-pink-500/20",
      seedType: 'yc_demo'
    },
    {
      text: "Create a professional B2B product demo for YouTube",
      icon: <Youtube className="w-4 h-4" />,
      details: "Classic YC Demo Day format",
      color: "bg-red-500/10 text-red-600 border-red-500/20 hover:bg-red-500/20",
      seedType: 'b2b_youtube'
    },
    {
      text: "Make an educational tutorial for Instagram Reels",
      icon: <Instagram className="w-4 h-4" />,
      details: "Step-by-step teaching format",
      color: "bg-purple-500/10 text-purple-600 border-purple-500/20 hover:bg-purple-500/20",
      seedType: 'instagram_tutorial'
    },
    {
      text: "Before/After transformation video for TikTok",
      icon: <TrendingUp className="w-4 h-4" />,
      details: "Results-driven viral format",
      color: "bg-green-500/10 text-green-600 border-green-500/20 hover:bg-green-500/20",
      seedType: 'transformation'
    }
  ];

  const handleCreateProject = async (promptText, seedType = null) => {
    if (!promptText.trim()) {
      toast.error('Please describe what you want to create');
      return;
    }

    setIsCreating(true);
    try {
      // Extract platform and product type from prompt (simple heuristic)
      let platform = 'TikTok';
      let productType = 'general';
      
      const lowerPrompt = promptText.toLowerCase();
      if (lowerPrompt.includes('youtube')) platform = 'YouTube';
      else if (lowerPrompt.includes('instagram')) platform = 'Instagram';
      else if (lowerPrompt.includes('tiktok')) platform = 'TikTok';
      
      if (lowerPrompt.includes('b2b') || lowerPrompt.includes('saas') || lowerPrompt.includes('professional')) {
        productType = 'b2b';
      } else if (lowerPrompt.includes('educational') || lowerPrompt.includes('tutorial')) {
        productType = 'educational';
      } else if (lowerPrompt.includes('transformation') || lowerPrompt.includes('before/after')) {
        productType = 'transformation';
      } else {
        productType = 'consumer';
      }

      // Build enhanced prompt with research seeds
      let enhancedPrompt = promptText;
      
      // Get default seeds for this type if user hasn't provided custom ones
      const seeds = seedType ? defaultSeeds[seedType] : null;
      const userHashtags = hashtags.trim();
      const userReferences = references.trim();
      
      // Append research context (behind the scenes)
      if (seeds || userHashtags || userReferences) {
        enhancedPrompt += '\n\n[Research Context for AI Director]:';
        
        if (userHashtags) {
          enhancedPrompt += `\nHashtags to analyze: ${userHashtags}`;
        } else if (seeds?.hashtags) {
          enhancedPrompt += `\nHashtags to analyze: ${seeds.hashtags}`;
        }
        
        if (userReferences) {
          enhancedPrompt += `\nReference creators/videos: ${userReferences}`;
        } else if (seeds?.references) {
          enhancedPrompt += `\nReference creators/videos: ${seeds.references}`;
        }
        
        if (seeds?.keywords && !userHashtags && !userReferences) {
          enhancedPrompt += `\nSearch keywords: ${seeds.keywords}`;
        }
      }

      const result = await createDirectorProject(enhancedPrompt, productType, platform);
      
      // Save project to localStorage
      const projects = JSON.parse(localStorage.getItem('director_projects') || '[]');
      projects.push({
        project_id: result.project_id,
        user_goal: promptText,
        product_type: productType,
        target_platform: platform,
        current_step: result.current_step,
        matched_format: result.matched_format,
        shot_list: result.shot_list,
        created_at: new Date().toISOString()
      });
      localStorage.setItem('director_projects', JSON.stringify(projects));
      
      toast.success('Project created! Redirecting to studio...');
      
      // Redirect to Content Studio with project ID
      setTimeout(() => {
        navigate(`/director/studio/${result.project_id}`);
      }, 500);
      
    } catch (error) {
      console.error('Error creating project:', error);
      toast.error('Failed to create project. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleSamplePromptClick = (sample) => {
    setPrompt(sample.text);
    
    // Auto-fill with default seeds as placeholders
    if (sample.seedType && defaultSeeds[sample.seedType]) {
      const seeds = defaultSeeds[sample.seedType];
      setHashtags(seeds.hashtags);
      setReferences(seeds.references);
      setShowAdvanced(true); // Show the advanced section so user can edit
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
      // Try to detect seed type from prompt text
      const lowerPrompt = prompt.toLowerCase();
      let seedType = null;
      
      if (lowerPrompt.includes('cluely') || lowerPrompt.includes('yc demo')) {
        seedType = 'yc_demo';
      } else if (lowerPrompt.includes('b2b') && lowerPrompt.includes('youtube')) {
        seedType = 'b2b_youtube';
      } else if (lowerPrompt.includes('tutorial') && lowerPrompt.includes('instagram')) {
        seedType = 'instagram_tutorial';
      } else if (lowerPrompt.includes('transformation') || lowerPrompt.includes('before')) {
        seedType = 'transformation';
      }
      
      handleCreateProject(prompt, seedType);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-sky relative overflow-hidden gradient-bg-dynamic">
      {/* Dynamic gradient orbs */}
      <div className="gradient-orb-1"></div>
      <div className="gradient-orb-2"></div>
      <div className="gradient-orb-3"></div>
      
      {/* Floating decorative elements */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden z-10">
        <div className="floating-sticker top-20 left-[8%] text-5xl animate-float" style={{ animationDelay: '0s' }}>🎬</div>
        <div className="floating-sticker top-32 right-[12%] text-4xl animate-float" style={{ animationDelay: '1.5s' }}>🎥</div>
        <div className="floating-sticker bottom-32 left-[15%] text-4xl animate-float" style={{ animationDelay: '3s' }}>✨</div>
        <div className="floating-sticker top-[45%] right-[20%] text-3xl animate-float" style={{ animationDelay: '2s' }}>🚀</div>
      </div>

      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button onClick={() => navigate('/')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-5xl font-logo font-bold text-foreground">filmit!</span>
            </button>
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                onClick={() => navigate('/director/projects')}
                className="text-sm"
              >
                My Projects
              </Button>
              <Badge className="bg-primary/20 text-primary border-primary/30 font-sans">
                <Film className="w-3 h-3 mr-1" />
                Director AI
              </Badge>
              <UserMenu />
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content - Centered */}
      <div className="flex items-center justify-center min-h-[calc(100vh-8rem)] px-4 sm:px-6 lg:px-8 py-12 relative z-20">
        <div className="w-full max-w-4xl space-y-8 animate-slide-up">
          
          {/* Hero Section */}
          <div className="text-center space-y-4">
            <div className="flex justify-center mb-6">
              <div className="w-24 h-24 rounded-3xl bg-gradient-primary flex items-center justify-center shadow-2xl animate-bounce-in">
                <Film className="w-12 h-12 text-primary-foreground" />
              </div>
            </div>
            <h1 className="text-6xl font-display font-bold text-foreground">
              {user ? `${user.username}'s Studio` : 'Your AI Director'}
            </h1>
          </div>

          {/* Main Prompt Card */}
          <Card className="border-border/50 shadow-2xl bg-card/95 backdrop-blur-sm">
            <CardContent className="pt-8 pb-8">
              <div className="space-y-4">
                <Textarea
                  value={prompt}
                  onChange={(e) => setPrompt(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="e.g., 'Create a product demo for my SaaS startup targeting developers on YouTube' or 'Build a viral TikTok showing before/after results'"
                  className="min-h-[120px] resize-none text-base font-sans"
                  disabled={isCreating}
                />

                {/* Advanced Research Options */}
                <div className="border-t border-border pt-4">
                  <button
                    onClick={() => setShowAdvanced(!showAdvanced)}
                    className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors mb-3"
                  >
                    <Sparkles className="w-4 h-4" />
                    <span className="font-semibold">
                      {showAdvanced ? '▼' : '▶'} Add Inspiration
                    </span>
                  </button>

                  {showAdvanced && (
                    <div className="space-y-3 animate-slide-up">
                      <div className="space-y-2">
                        <label className="text-xs font-semibold text-foreground block">
                          Hashtags
                        </label>
                        <input
                          type="text"
                          value={hashtags}
                          onChange={(e) => setHashtags(e.target.value)}
                          placeholder="#startups #ycombinator #saas #productlaunch"
                          className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-transparent"
                          disabled={isCreating}
                        />
                      </div>

                      <div className="space-y-2">
                        <label className="text-xs font-semibold text-foreground block">
                          Creators
                        </label>
                        <input
                          type="text"
                          value={references}
                          onChange={(e) => setReferences(e.target.value)}
                          placeholder="@cluely @tryskribe @notion"
                          className="w-full px-3 py-2 text-sm border border-border rounded-lg bg-background focus:ring-2 focus:ring-primary focus:border-transparent"
                          disabled={isCreating}
                        />
                      </div>
                    </div>
                  )}
                </div>

                <div className="flex items-center justify-between">
                  <p className="text-xs text-muted-foreground">
                    Press <kbd className="px-2 py-1 bg-muted rounded text-xs">⌘ Enter</kbd> to create
                  </p>
                  <Button
                    onClick={() => handleCreateProject(prompt, null)}
                    disabled={isCreating || !prompt.trim()}
                    className="bg-gradient-primary hover:shadow-glow transition-all duration-300"
                    size="lg"
                  >
                    {isCreating ? (
                      <>
                        <Sparkles className="w-4 h-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      <>
                        <Film className="w-4 h-4 mr-2" />
                        Start Project
                      </>
                    )}
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Sample Prompts */}
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {samplePrompts.map((sample, i) => (
                <Card 
                  key={i}
                  className={`border-2 transition-all duration-300 cursor-pointer hover:shadow-lg hover:scale-105 ${sample.color}`}
                  onClick={() => handleSamplePromptClick(sample)}
                >
                  <CardContent className="pt-4 pb-4">
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {sample.icon}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-semibold mb-1">
                          {sample.text}
                        </p>
                        <p className="text-xs opacity-70">
                          {sample.details}
                        </p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Features */}
          <div className="grid grid-cols-3 gap-4 pt-8">
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto">
                <TrendingUp className="w-6 h-6 text-primary" />
              </div>
              <p className="text-sm font-semibold text-foreground">Viral Formats</p>
              <p className="text-xs text-muted-foreground">Match with proven templates</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto">
                <Video className="w-6 h-6 text-primary" />
              </div>
              <p className="text-sm font-semibold text-foreground">Guided Filming</p>
              <p className="text-xs text-muted-foreground">Step-by-step instructions</p>
            </div>
            <div className="text-center space-y-2">
              <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center mx-auto">
                <Sparkles className="w-6 h-6 text-primary" />
              </div>
              <p className="text-sm font-semibold text-foreground">AI Editing</p>
              <p className="text-xs text-muted-foreground">Auto-optimize for platform</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
