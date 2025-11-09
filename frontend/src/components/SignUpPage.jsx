import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Separator } from './ui/separator';
import { Eye, EyeOff, Sparkles, TrendingUp, BarChart3, Zap, Film } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const SignUpPage = () => {
  const navigate = useNavigate();
  const { register } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });

  const handleSignUp = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    // Validation
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      toast.error('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    if (formData.username.length < 3) {
      toast.error('Username must be at least 3 characters');
      setIsLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Password must be at least 6 characters');
      setIsLoading(false);
      return;
    }

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      setIsLoading(false);
      return;
    }
    
    const result = await register(formData.username, formData.email, formData.password);
    setIsLoading(false);
    
    if (result.success) {
      setTimeout(() => navigate('/director'), 500);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden gradient-bg-dynamic">
      {/* Navigation */}
      <nav className="border-b border-border/50 bg-background/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <button onClick={() => navigate('/')} className="flex items-center gap-2 hover:opacity-80 transition-opacity">
              <span className="text-5xl font-logo font-bold text-foreground">filmit!</span>
            </button>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="flex items-center justify-center p-4 min-h-[calc(100vh-4rem)] bg-gradient-subtle">
        {/* Dynamic gradient orbs */}
        <div className="gradient-orb-1"></div>
        <div className="gradient-orb-2"></div>
      
      {/* Background decorative elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none z-0">
        <div className="absolute top-20 left-10 w-72 h-72 bg-primary/5 rounded-full blur-3xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-primary/10 rounded-full blur-3xl animate-float" style={{ animationDelay: '1s' }}></div>
        <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-secondary/5 rounded-full blur-3xl animate-float" style={{ animationDelay: '2s' }}></div>
      </div>

      <div className="w-full max-w-6xl relative z-10">
        <div className="grid lg:grid-cols-2 gap-8 lg:gap-12 items-center">
          {/* Left side - Branding */}
          <div className="hidden lg:block space-y-8 animate-slide-up">
            <div className="space-y-6">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-primary/10 rounded-full backdrop-blur-sm border border-primary/20">
                <Film className="w-4 h-4 text-primary" />
                <span className="text-sm font-medium text-primary">AI-Directed Content Production</span>
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-display font-bold leading-tight text-foreground">
                Create Your
                <br />
                <span className="marker-highlight">Free Account</span>
              </h1>
              
              <p className="text-lg text-muted-foreground leading-relaxed max-w-xl font-sans">
                Join filmit! and start transforming your raw footage into viral content. You film it, we'll handle the rest.
              </p>
            </div>

            {/* Feature highlights */}
            <div className="space-y-4">
              <div className="flex items-start gap-3 glass-card p-4 rounded-xl hover:scale-105 transition-transform">
                <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">AI Director</h3>
                  <p className="text-sm text-muted-foreground">Get guided through every shot with AI coaching</p>
                </div>
              </div>

              <div className="flex items-start gap-3 glass-card p-4 rounded-xl hover:scale-105 transition-transform">
                <div className="w-10 h-10 rounded-lg bg-secondary/10 flex items-center justify-center flex-shrink-0">
                  <TrendingUp className="w-5 h-5 text-secondary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Viral Formats</h3>
                  <p className="text-sm text-muted-foreground">Use proven templates that actually work</p>
                </div>
              </div>

              <div className="flex items-start gap-3 glass-card p-4 rounded-xl hover:scale-105 transition-transform">
                <div className="w-10 h-10 rounded-lg bg-accent/10 flex items-center justify-center flex-shrink-0">
                  <BarChart3 className="w-5 h-5 text-accent" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1">Real-time Feedback</h3>
                  <p className="text-sm text-muted-foreground">Get instant analysis on every upload</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right side - Sign Up Form */}
          <div className="animate-slide-up" style={{ animationDelay: '0.1s' }}>
            <Card className="glass-card border-border/50 shadow-2xl">
              <CardHeader className="space-y-1">
                <CardTitle className="text-2xl font-display font-bold text-foreground">Create an account</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Enter your details to get started with filmit!
                </CardDescription>
              </CardHeader>
              <CardContent>
                <form onSubmit={handleSignUp} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="username" className="text-foreground">Username</Label>
                    <Input
                      id="username"
                      placeholder="johndoe"
                      value={formData.username}
                      onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                      className="bg-background/50 border-border/50"
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-foreground">Email</Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="bg-background/50 border-border/50"
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-foreground">Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="••••••••"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="bg-background/50 border-border/50 pr-10"
                        disabled={isLoading}
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                      >
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="text-xs text-muted-foreground">Must be at least 6 characters</p>
                  </div>

                  <div className="space-y-2">
                    <Label htmlFor="confirmPassword" className="text-foreground">Confirm Password</Label>
                    <Input
                      id="confirmPassword"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="••••••••"
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      className="bg-background/50 border-border/50"
                      disabled={isLoading}
                    />
                  </div>

                  <Button 
                    type="submit" 
                    className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <><Zap className="mr-2 h-4 w-4 animate-pulse" /> Creating account...</>
                    ) : (
                      <>Create account</>
                    )}
                  </Button>
                </form>
              </CardContent>
              <CardFooter className="flex flex-col space-y-4">
                <div className="text-sm text-center text-muted-foreground">
                  Already have an account?{' '}
                  <button 
                    onClick={() => navigate('/login')} 
                    className="text-primary hover:underline font-medium"
                  >
                    Sign in
                  </button>
                </div>
              </CardFooter>
            </Card>
          </div>
        </div>
      </div>
      </div>
    </div>
  );
};
