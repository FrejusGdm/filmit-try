const API_BASE_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Helper function to generate session ID
export const getSessionId = () => {
  let sessionId = localStorage.getItem('filmit_session_id');
  if (!sessionId) {
    sessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    localStorage.setItem('filmit_session_id', sessionId);
  }
  return sessionId;
};

// Chunked video upload
export const uploadVideoChunked = async (file, onProgress) => {
  const CHUNK_SIZE = 1024 * 1024; // 1MB chunks
  const totalChunks = Math.ceil(file.size / CHUNK_SIZE);
  const sessionId = getSessionId();
  
  for (let i = 0; i < totalChunks; i++) {
    const start = i * CHUNK_SIZE;
    const end = Math.min(start + CHUNK_SIZE, file.size);
    const chunk = file.slice(start, end);
    
    // Convert chunk to base64
    const base64Chunk = await new Promise((resolve) => {
      const reader = new FileReader();
      reader.onload = () => {
        const base64 = reader.result.split(',')[1];
        resolve(base64);
      };
      reader.readAsDataURL(chunk);
    });
    
    // Upload chunk
    const response = await fetch(`${API_BASE_URL}/api/videos/upload-chunk`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        chunk_index: i,
        total_chunks: totalChunks,
        chunk_data: base64Chunk,
        session_id: sessionId,
        filename: file.name
      })
    });
    
    const result = await response.json();
    
    if (onProgress) {
      onProgress({
        uploaded: i + 1,
        total: totalChunks,
        percentage: Math.round(((i + 1) / totalChunks) * 100)
      });
    }
    
    // Return video metadata on completion
    if (result.status === 'completed') {
      return result;
    }
  }
};

// Get trending data
export const getTrendingData = async () => {
  const response = await fetch(`${API_BASE_URL}/api/trends/current?hashtag_limit=20`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// Analyze video
export const analyzeVideo = async (videoId, userContext, targetAudience) => {
  const response = await fetch(`${API_BASE_URL}/api/videos/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      video_id: videoId,
      user_context: userContext,
      target_platform: 'TikTok',
      target_audience: targetAudience
    })
  });
  return response.json();
};

// Get suggestions for video
export const getSuggestions = async (videoId) => {
  const response = await fetch(`${API_BASE_URL}/api/suggestions/${videoId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// Accept/reject suggestion
export const handleSuggestionAction = async (suggestionId, action, feedback = null) => {
  const response = await fetch(`${API_BASE_URL}/api/suggestions/action`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      suggestion_id: suggestionId,
      action: action,
      feedback: feedback
    })
  });
  return response.json();
};

// Send chat message
export const sendChatMessage = async (message, videoId = null) => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      message: message,
      video_id: videoId
    })
  });
  return response.json();
};

// Get chat history
export const getChatHistory = async () => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/chat/history/${sessionId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// List videos for session
export const listVideos = async () => {
  const sessionId = getSessionId();
  const response = await fetch(`${API_BASE_URL}/api/videos/list/${sessionId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// ===== DIRECTOR AI WORKFLOW API =====

// Create new Director project
export const createDirectorProject = async (userGoal, productType = 'general', targetPlatform = 'YouTube') => {
  const response = await fetch(`${API_BASE_URL}/api/director/project`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      user_goal: userGoal,
      product_type: productType,
      target_platform: targetPlatform
    })
  });
  return response.json();
};

// Send message to Director
export const sendDirectorMessage = async (projectId, message) => {
  const response = await fetch(`${API_BASE_URL}/api/director/message`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      message: message
    })
  });
  return response.json();
};

// Upload video segment for Director project
export const uploadDirectorSegment = async (projectId, segmentName, file, onProgress) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await fetch(
    `${API_BASE_URL}/api/director/upload-segment?project_id=${projectId}&segment_name=${encodeURIComponent(segmentName)}`,
    {
      method: 'POST',
      body: formData
    }
  );
  
  return response.json();
};

// Get Director project details
export const getDirectorProject = async (projectId) => {
  const response = await fetch(`${API_BASE_URL}/api/director/project/${projectId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  return response.json();
};

// Get segment analysis (automatic AI analysis of uploaded segment)
export const getSegmentAnalysis = async (projectId, segmentName) => {
  const response = await fetch(
    `${API_BASE_URL}/api/director/segment-analysis/${projectId}/${encodeURIComponent(segmentName)}`,
    {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' }
    }
  );
  return response.json();
};

// Assemble project video with ffmpeg
export const assembleProjectVideo = async (projectId, options = {}) => {
  const response = await fetch(`${API_BASE_URL}/api/director/assemble`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, options })
  });
  return response.json();
};

// Shot Management APIs

// Update a shot
export const updateShot = async (projectId, shotIndex, updates) => {
  const response = await fetch(`${API_BASE_URL}/api/director/shot/update`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      shot_index: shotIndex,
      ...updates
    })
  });
  return response.json();
};

// Add a new shot
export const addShot = async (projectId, shotData) => {
  const response = await fetch(`${API_BASE_URL}/api/director/shot/add`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      shot: shotData
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to add shot');
  }
  
  return response.json();
};

// Get assembly status
export const getAssemblyStatus = async (assemblyId) => {
  const response = await fetch(`${API_BASE_URL}/api/director/assembly-status/${assemblyId}`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get assembly status');
  }
  
  return response.json();
};

// Download assembled video
export const downloadAssembledVideo = async (assemblyId) => {
  const response = await fetch(`${API_BASE_URL}/api/director/download/${assemblyId}`, {
    method: 'GET'
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to download video');
  }
  
  // Create blob and download
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `filmit_video_${assemblyId}.mp4`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
  document.body.removeChild(a);
};

// Delete a shot
export const deleteShot = async (projectId, shotIndex) => {
  const response = await fetch(`${API_BASE_URL}/api/director/shot/delete`, {
    method: 'DELETE',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      shot_index: shotIndex
    })
  });
  return response.json();
};

// Reorder shots
export const reorderShots = async (projectId, shotList) => {
  const response = await fetch(`${API_BASE_URL}/api/director/shot/reorder`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      project_id: projectId,
      shot_list: shotList
    })
  });
  return response.json();
};
