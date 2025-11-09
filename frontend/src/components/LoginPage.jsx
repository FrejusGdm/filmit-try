import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './ui/card';
import { Separator } from './ui/separator';
import { Eye, EyeOff, Sparkles, TrendingUp, BarChart3, Zap, Film, Scissors } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export const LoginPage = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { login } = useAuth();
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });

  const handleSocialLogin = (provider) => {
    const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    
    if (provider === 'Google') {
      // Redirect to backend OAuth endpoint
      window.location.href = `${BACKEND_URL}/api/auth/oauth/google`;
    } else {
      toast.info(`${provider} login`, {
        description: 'Currently only Google OAuth is supported. Other providers coming soon!'
      });
    }
  };

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    if (!formData.email || !formData.password) {
      toast.error('Please fill in all fields');
      setIsLoading(false);
      return;
    }
    
    const result = await login(formData.email, formData.password);
    setIsLoading(false);
    
    if (result.success) {
      // Redirect to the page they tried to access, or to director home
      const from = location.state?.from?.pathname || '/director';
      setTimeout(() => navigate(from), 500);
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
                Your AI
                <br />
                <span className="marker-highlight">Content Director</span>
              </h1>
              
              <p className="text-lg text-muted-foreground leading-relaxed max-w-xl font-sans">
                Get coached through every creative decision. AI that directs your cuts, pacing, and structure based on viral formats.
              </p>
            </div>

            <div className="space-y-4">
              <div className="group flex items-start gap-4 p-5 bg-card rounded-xl border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-md">
                <div className="w-12 h-12 rounded-xl bg-gradient-primary flex items-center justify-center flex-shrink-0 shadow-sm group-hover:shadow-glow transition-shadow duration-300">
                  <Scissors className="w-6 h-6 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1 text-lg">Cut-by-Cut Coaching</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">AI guides every editing decision, from hook timing to B-roll placement</p>
                </div>
              </div>
              
              <div className="group flex items-start gap-4 p-5 bg-card rounded-xl border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-md">
                <div className="w-12 h-12 rounded-xl bg-secondary/90 flex items-center justify-center flex-shrink-0 shadow-sm">
                  <Film className="w-6 h-6 text-secondary-foreground" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1 text-lg">Viral Format Direction</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">Step-by-step guidance using proven structures that are trending now</p>
                </div>
              </div>
              
              <div className="group flex items-start gap-4 p-5 bg-card rounded-xl border border-border/50 hover:border-primary/30 transition-all duration-300 hover:shadow-md">
                <div className="w-12 h-12 rounded-xl bg-primary/10 border border-primary/20 flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-6 h-6 text-primary" />
                </div>
                <div>
                  <h3 className="font-semibold text-foreground mb-1 text-lg">Creative Decision Support</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">Real-time coaching on pacing, transitions, and engagement tactics</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right side - Login Form */}
          <div className="animate-slide-up" style={{ animationDelay: '0.2s' }}>
            <Card className="border-border/50 shadow-xl backdrop-blur-sm bg-card/95">
              <CardHeader className="space-y-2 pb-6">
                <div className="lg:hidden mb-4">
                  <h1 className="text-3xl font-bold text-foreground mb-2">
                    Welcome to <span className="font-logo text-primary">filmit!</span>
                  </h1>
                </div>
                <CardTitle className="text-2xl font-bold text-foreground">Sign in to your account</CardTitle>
                <CardDescription className="text-muted-foreground">
                  Connect your platforms and let AI start directing your content
                </CardDescription>
              </CardHeader>
              
              <CardContent className="space-y-6">
                {/* Social Login Icons */}
                <div className="flex justify-center gap-4">
                  {/* Google - Active */}
                  <button
                    onClick={() => handleSocialLogin('Google')}
                    disabled={isLoading}
                    className="group w-14 h-14 rounded-xl border-2 border-border hover:border-primary/50 bg-card flex items-center justify-center transition-all duration-300 hover:shadow-md hover:scale-110 disabled:opacity-50"
                    title="Continue with Google"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24">
                      <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                      <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                      <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                      <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                    </svg>
                  </button>
                  
                  {/* YouTube - Coming Soon */}
                  <button
                    disabled={true}
                    className="relative w-14 h-14 rounded-xl border-2 border-border bg-card flex items-center justify-center opacity-40 cursor-not-allowed"
                    title="YouTube - Coming Soon"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="#999">
                      <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                    </svg>
                  </button>
                  
                  {/* TikTok - Coming Soon */}
                  <button
                    disabled={true}
                    className="relative w-14 h-14 rounded-xl border-2 border-border bg-card flex items-center justify-center opacity-40 cursor-not-allowed"
                    title="TikTok - Coming Soon"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="#999">
                      <path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-5.2 1.74 2.89 2.89 0 0 1 2.31-4.64 2.93 2.93 0 0 1 .88.13V9.4a6.84 6.84 0 0 0-1-.05A6.33 6.33 0 0 0 5 20.1a6.34 6.34 0 0 0 10.86-4.43v-7a8.16 8.16 0 0 0 4.77 1.52v-3.4a4.85 4.85 0 0 1-1-.1z"/>
                    </svg>
                  </button>
                  
                  {/* Instagram - Coming Soon */}
                  <button
                    disabled={true}
                    className="relative w-14 h-14 rounded-xl border-2 border-border bg-card flex items-center justify-center opacity-40 cursor-not-allowed"
                    title="Instagram - Coming Soon"
                  >
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="#999">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/>
                    </svg>
                  </button>
                </div>
                
                {/* Coming Soon Text */}
                <p className="text-center text-xs text-muted-foreground">
                  More platforms coming soon
                </p>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <Separator />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-3 text-muted-foreground font-medium">Or continue with email</span>
                  </div>
                </div>

                {/* Email/Password Form */}
                <form onSubmit={handleEmailLogin} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-foreground font-medium">Email or Username</Label>
                    <Input
                      id="email"
                      type="text"
                      placeholder="name@example.com"
                      value={formData.email}
                      onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                      className="h-11 focus:ring-primary focus:border-primary"
                      disabled={isLoading}
                    />
                  </div>
                  
                  <div className="space-y-2">
                    <Label htmlFor="password" className="text-foreground font-medium">Password</Label>
                    <div className="relative">
                      <Input
                        id="password"
                        type={showPassword ? 'text' : 'password'}
                        placeholder="Enter your password"
                        value={formData.password}
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        className="h-11 pr-10 focus:ring-primary focus:border-primary"
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
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <label className="flex items-center gap-2 cursor-pointer group">
                      <input type="checkbox" className="rounded border-border accent-primary" />
                      <span className="text-muted-foreground group-hover:text-foreground transition-colors">Remember me</span>
                    </label>
                    <button type="button" className="text-primary hover:text-primary-light font-medium transition-colors">
                      Forgot password?
                    </button>
                  </div>

                  <Button
                    type="submit"
                    className="w-full h-12 bg-gradient-primary hover:shadow-glow transition-all duration-300 font-semibold text-base"
                    disabled={isLoading}
                  >
                    {isLoading ? (
                      <span className="flex items-center gap-2">
                        <Zap className="w-4 h-4 animate-pulse" />
                        Signing in...
                      </span>
                    ) : (
                      'Sign in'
                    )}
                  </Button>
                </form>
              </CardContent>
              
              <CardFooter className="flex flex-col space-y-4 pt-2">
                <Separator />
                
                {/* Skip Auth for Testing Button */}
                <Button
                  type="button"
                  variant="outline"
                  className="w-full border-yellow-500 text-yellow-600 hover:bg-yellow-50 dark:hover:bg-yellow-950/20"
                  onClick={() => navigate('/director?testmode=true')}
                >
                  <Zap className="w-4 h-4 mr-2" />
                  Skip Auth for Testing
                </Button>
                
                <p className="text-center text-sm text-muted-foreground">
                  Don't have an account?{' '}
                  <button 
                    onClick={() => navigate('/signup')}
                    className="text-primary hover:text-primary-light font-semibold transition-colors"
                  >
                    Sign up for free
                  </button>
                </p>
              </CardFooter>
            </Card>
            
            <p className="mt-6 text-center text-xs text-muted-foreground">
              By signing in, you agree to our{' '}
              <button className="text-primary hover:text-primary-light transition-colors">Terms of Service</button>
              {' '}and{' '}
              <button className="text-primary hover:text-primary-light transition-colors">Privacy Policy</button>
            </p>
          </div>
        </div>
      </div>
    </div>
    </div>
  );
};