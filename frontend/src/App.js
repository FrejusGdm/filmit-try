import { useEffect } from "react";
import "@/App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import axios from "axios";
import { LoginPage } from "./components/LoginPage";
import { SignUpPage } from "./components/SignUpPage";
import { OAuthCallback } from "./components/OAuthCallback";
import { LandingPage } from "./components/LandingPage";
import { WorkspaceEnhanced } from "./components/WorkspaceEnhanced";
import { DirectorHome } from "./components/DirectorHome";
import { ContentStudio } from "./components/ContentStudio";
import { DirectorProjects } from "./components/DirectorProjects";
import { ProtectedRoute } from "./components/ProtectedRoute";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "./components/ui/sonner";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Home = () => {
  const helloWorldApi = async () => {
    try {
      const response = await axios.get(`${API}/`);
      console.log(response.data.message);
    } catch (e) {
      console.error(e, `errored out requesting / api`);
    }
  };

  useEffect(() => {
    helloWorldApi();
  }, []);

  return <LandingPage />;
};

function App() {
  return (
    <div className="App">
      <Toaster position="top-right" richColors />
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignUpPage />} />
            <Route path="/auth/callback" element={<OAuthCallback />} />
            <Route path="/workspace" element={<ProtectedRoute><WorkspaceEnhanced /></ProtectedRoute>} />
            <Route path="/director" element={<ProtectedRoute><DirectorHome /></ProtectedRoute>} />
            <Route path="/director/studio/:projectId" element={<ProtectedRoute><ContentStudio /></ProtectedRoute>} />
            <Route path="/director/projects" element={<ProtectedRoute><DirectorProjects /></ProtectedRoute>} />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;