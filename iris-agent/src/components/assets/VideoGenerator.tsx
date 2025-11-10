"""
VideoGenerator Component
VEO3 video generation with weekly limits (2 times per week)
"""

import React, { useState, useEffect } from 'react';
import { 
  PlayIcon, 
  ClockIcon, 
  FilmIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon
} from '@heroicons/react/24/outline';
import { mcpClient, VideoGenerationRequest, VideoGenerationResponse, VideoGenerationLimit } from '../../lib/api';

const VideoGenerator: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [style, setStyle] = useState<'reel' | 'short' | 'standard'>('reel');
  const [duration, setDuration] = useState(30);
  const [aspectRatio, setAspectRatio] = useState<'9:16' | '16:9' | '1:1'>('9:16');
  const [quality, setQuality] = useState<'standard' | 'hd' | '4k'>('hd');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generationStatus, setGenerationStatus] = useState<string>('');
  const [videoResult, setVideoResult] = useState<VideoGenerationResponse | null>(null);
  const [limitInfo, setLimitInfo] = useState<VideoGenerationLimit | null>(null);
  const [generationHistory, setGenerationHistory] = useState<VideoGenerationResponse[]>([]);

  useEffect(() => {
    loadLimitInfo();
    loadGenerationHistory();
  }, []);

  const loadLimitInfo = async () => {
    try {
      const limit = await mcpClient.getVideoGenerationLimit();
      if (limit) {
        setLimitInfo(limit);
      }
    } catch (error) {
      console.error('Error loading limit info:', error);
    }
  };

  const loadGenerationHistory = async () => {
    try {
      const history = await mcpClient.getVideoGenerationHistory(10);
      setGenerationHistory(history);
    } catch (error) {
      console.error('Error loading generation history:', error);
    }
  };

  const generateVideo = async () => {
    if (!prompt.trim()) {
      alert('Please enter a video prompt');
      return;
    }

    if (limitInfo && limitInfo.remaining_count <= 0) {
      alert('Weekly limit reached. Please wait for the reset date.');
      return;
    }

    setIsGenerating(true);
    setGenerationStatus('Initializing video generation...');
    setVideoResult(null);

    try {
      const request: VideoGenerationRequest = {
        prompt: prompt.trim(),
        style,
        duration,
        aspect_ratio: aspectRatio,
        quality,
        voiceover: false,
        music: false
      };

      const result = await mcpClient.generateVideoVEO3(request);
      
      if (result) {
        setVideoResult(result);
        setGenerationStatus('Video generation started. This may take several minutes.');
        
        // Poll for status updates
        if (result.video_id !== 'error') {
          pollVideoStatus(result.video_id);
        }
      }
    } catch (error) {
      console.error('Error generating video:', error);
      setGenerationStatus('Error generating video. Please try again.');
    } finally {
      setIsGenerating(false);
    }
  };

  const pollVideoStatus = async (videoId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await mcpClient.getVideoGenerationStatus(videoId);
        if (status) {
          setVideoResult(status);
          
          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollInterval);
            setGenerationStatus(
              status.status === 'completed' 
                ? 'Video generation completed!' 
                : 'Video generation failed. Please try again.'
            );
            loadLimitInfo(); // Refresh limit info
            loadGenerationHistory(); // Refresh history
          } else {
            setGenerationStatus(`Status: ${status.status}...`);
          }
        }
      } catch (error) {
        console.error('Error polling video status:', error);
        clearInterval(pollInterval);
      }
    }, 5000); // Poll every 5 seconds
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'processing': case 'pending': return 'text-blue-600 bg-blue-100';
      case 'failed': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  const canGenerate = limitInfo ? limitInfo.remaining_count > 0 : true;

  return (
    <div className="space-y-6">
      {/* Limit Status */}
      {limitInfo && (
        <div className={`p-4 rounded-lg ${canGenerate ? 'bg-green-50' : 'bg-red-50'}`}>
          <div className="flex items-center">
            {canGenerate ? (
              <CheckCircleIcon className="w-5 h-5 text-green-600 mr-2" />
            ) : (
              <ExclamationTriangleIcon className="w-5 h-5 text-red-600 mr-2" />
            )}
            <div>
              <p className={`font-medium ${canGenerate ? 'text-green-800' : 'text-red-800'}`}>
                Weekly Limit: {limitInfo.used_count}/{limitInfo.weekly_limit} used
              </p>
              <p className={`text-sm ${canGenerate ? 'text-green-600' : 'text-red-600'}`}>
                {canGenerate 
                  ? `${limitInfo.remaining_count} generations remaining` 
                  : 'Limit reached. Resets on ' + new Date(limitInfo.reset_date).toLocaleDateString()
                }
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Generation Form */}
      <div className="bg-white p-6 rounded-lg shadow">
        <h3 className="text-lg font-semibold mb-4 flex items-center">
          <FilmIcon className="w-5 h-5 mr-2" />
          Generate Video with VEO3
        </h3>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Video Prompt
            </label>
            <textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              placeholder="Describe the video you want to generate..."
              disabled={isGenerating || !canGenerate}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Style
              </label>
              <select
                value={style}
                onChange={(e) => setStyle(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isGenerating}
              >
                <option value="reel">Reel (9:16)</option>
                <option value="short">Short (1:1)</option>
                <option value="standard">Standard (16:9)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Duration (seconds)
              </label>
              <input
                type="number"
                value={duration}
                onChange={(e) => setDuration(parseInt(e.target.value) || 30)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                min="10"
                max="120"
                disabled={isGenerating}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Quality
              </label>
              <select
                value={quality}
                onChange={(e) => setQuality(e.target.value as any)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={isGenerating}
              >
                <option value="standard">Standard</option>
                <option value="hd">HD</option>
                <option value="4k">4K</option>
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Aspect Ratio
            </label>
            <select
              value={aspectRatio}
              onChange={(e) => setAspectRatio(e.target.value as any)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isGenerating}
            >
              <option value="9:16">9:16 (Vertical)</option>
              <option value="16:9">16:9 (Horizontal)</option>
              <option value="1:1">1:1 (Square)</option>
            </select>
          </div>

          <button
            onClick={generateVideo}
            disabled={isGenerating || !canGenerate || !prompt.trim()}
            className="w-full flex items-center justify-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isGenerating ? (
              <>
                <ClockIcon className="w-4 h-4 mr-2 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <PlayIcon className="w-4 h-4 mr-2" />
                Generate Video
              </>
            )}
          </button>
        </div>

        {/* Generation Status */}
        {(isGenerating || generationStatus) && (
          <div className="mt-4 p-3 bg-blue-50 rounded-lg">
            <p className="text-blue-800 text-sm">{generationStatus}</p>
          </div>
        )}
      </div>

      {/* Video Result */}
      {videoResult && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Generation Result</h3>
          
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Status:</span>
              <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(videoResult.status)}`}>
                {videoResult.status}
              </span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Video ID:</span>
              <span className="font-mono text-sm">{videoResult.video_id}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Duration:</span>
              <span>{formatDuration(videoResult.duration || 0)}</span>
            </div>
            
            {videoResult.video_url && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Video URL:</span>
                <a
                  href={videoResult.video_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View Video
                </a>
              </div>
            )}
            
            {videoResult.thumbnail_url && (
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Thumbnail:</span>
                <a
                  href={videoResult.thumbnail_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  View Thumbnail
                </a>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Generation History */}
      {generationHistory.length > 0 && (
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Recent Generations</h3>
          
          <div className="space-y-3">
            {generationHistory.slice(0, 5).map((video) => (
              <div key={video.video_id} className="border rounded-lg p-3">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <p className="text-sm font-medium truncate">{video.prompt}</p>
                    <p className="text-xs text-gray-500">
                      {new Date(video.created_at).toLocaleString()}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(video.status)}`}>
                    {video.status}
                  </span>
                </div>
                
                {video.status === 'completed' && video.video_url && (
                  <div className="mt-2">
                    <a
                      href={video.video_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      View Video
                    </a>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default VideoGenerator;