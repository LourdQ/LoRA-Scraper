'use client';
import React, { useState, useEffect } from 'react';

export default function ScanStatus() {
  const [status, setStatus] = useState('idle');
  const [lastScan, setLastScan] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [modelId, setModelId] = useState('');
  const [modelUrl, setModelUrl] = useState('');
  const [inputMethod, setInputMethod] = useState<'id' | 'url'>('id');
  const [error, setError] = useState<string | null>(null);

  // Rest of status checking effect remains the same...

  const extractModelIdFromUrl = (url: string): string | null => {
    try {
      const match = url.match(/\/models\/(\d+)/);
      return match ? match[1] : null;
    } catch {
      return null;
    }
  };

  const startScan = async () => {
    let idToScan = modelId;

    if (inputMethod === 'url') {
      if (!modelUrl) {
        setError('Please enter a model URL');
        return;
      }
      const extractedId = extractModelIdFromUrl(modelUrl);
      if (!extractedId) {
        setError('Invalid CivitAI URL format');
        return;
      }
      idToScan = extractedId;
    } else if (!modelId) {
      setError('Please enter a model ID');
      return;
    }

    try {
      setError(null);
      setIsLoading(true);

      // Check if model exists
      const checkResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/check-model?modelId=${idToScan}`);
      const checkData = await checkResponse.json();
      
      if (checkData.exists) {
        setError(checkData.message);
        return;
      }

      // Start scan
      const scanResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/start-scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelId: parseInt(idToScan) }),
      });
      
      const scanData = await scanResponse.json();
      
      if (scanData.error) {
        setError(scanData.error);
        setStatus('error');
      } else {
        setStatus('scanning');
        setModelId('');
        setModelUrl('');
      }
    } catch (error) {
      console.error('Failed to start scan:', error);
      setError('Failed to start scan. Please try again.');
      setStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-semibold mb-2">Scanner Status</h2>
      <div className="space-y-2">
        <div>
          <span className="font-medium">Current Status: </span>
          <span className={
            status === 'scanning' ? 'text-green-600' : 
            status === 'error' ? 'text-red-600' : 
            'text-gray-600'
          }>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </span>
        </div>
        {lastScan && (
          <div>
            <span className="font-medium">Last Scan: </span>
            <span className="text-gray-600">
              {new Date(lastScan).toLocaleString()}
            </span>
          </div>
        )}
        {error && (
          <div className="text-red-600 text-sm mt-2 p-2 bg-red-50 rounded">
            {error}
          </div>
        )}
        <div className="mt-4">
          <div className="flex gap-2 mb-4">
            <button
              onClick={() => setInputMethod('id')}
              className={`px-3 py-1 rounded ${
                inputMethod === 'id' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Model ID
            </button>
            <button
              onClick={() => setInputMethod('url')}
              className={`px-3 py-1 rounded ${
                inputMethod === 'url' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-200 text-gray-700'
              }`}
            >
              Model URL
            </button>
          </div>
          {inputMethod === 'id' ? (
            <input
              type="text"
              value={modelId}
              onChange={(e) => {
                setModelId(e.target.value);
                setError(null);
              }}
              placeholder="Enter CivitAI Model ID"
              className="w-full p-2 border rounded mb-2"
              disabled={status === 'scanning'}
            />
          ) : (
            <input
              type="text"
              value={modelUrl}
              onChange={(e) => {
                setModelUrl(e.target.value);
                setError(null);
              }}
              placeholder="Enter CivitAI Model URL"
              className="w-full p-2 border rounded mb-2"
              disabled={status === 'scanning'}
            />
          )}
          <button 
            className={`w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors ${
              isLoading || status === 'scanning' ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={startScan}
            disabled={isLoading || status === 'scanning'}
          >
            {isLoading ? 'Starting...' : 
             status === 'scanning' ? 'Scanning...' : 
             'Start Scan'}
          </button>
        </div>
      </div>
    </div>
  );
}
