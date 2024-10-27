import React, { useState, useEffect } from 'react';

interface ScanResult {
  modelId: number;
  modelName: string;
  status: 'success' | 'error';
  errorMessage?: string;
}

export default function ResultsList() {
  const [modelId, setModelId] = useState('');
  const [modelUrl, setModelUrl] = useState('');
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);

  const handleScan = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelId: modelId || modelUrl }),
      });
      const data = await response.json();

      if (data.success) {
        setScanResult({ modelId: data.modelId, modelName: data.modelName, status: 'success' });
      } else if (data.error === 'duplicate') {
        setScanResult({ status: 'error', errorMessage: 'Model already Exists!' });
        setTimeout(() => setScanResult(null), 5000);
      } else {
        setScanResult({ status: 'error', errorMessage: 'This Model can not be found, please check the Model number' });
        setTimeout(() => setScanResult(null), 5000);
      }

      setModelId('');
      setModelUrl('');
    } catch (err) {
      console.error('Failed to scan model:', err);
      setScanResult({ status: 'error', errorMessage: 'An error occurred while scanning the model. Please try again.' });
    }
  };

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Scan Model</h2>
      <div className="space-y-4">
        <div>
          <label htmlFor="modelId" className="block text-sm font-medium text-gray-700">
            Model ID
          </label>
          <input
            type="text"
            id="modelId"
            value={modelId}
            onChange={(e) => setModelId(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Enter CivitAI Model ID"
          />
        </div>
        <div>
          <label htmlFor="modelUrl" className="block text-sm font-medium text-gray-700">
            Model URL
          </label>
          <input
            type="text"
            id="modelUrl"
            value={modelUrl}
            onChange={(e) => setModelUrl(e.target.value)}
            className="w-full p-2 border rounded"
            placeholder="Enter CivitAI Model URL"
          />
        </div>
        <button
          className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          onClick={handleScan}
        >
          Start Scan
        </button>
        {scanResult && (
          <div
            className={`p-4 border rounded ${
              scanResult.status === 'success'
                ? 'bg-green-100 text-green-800'
                : 'bg-red-100 text-red-800'
            }`}
          >
            {scanResult.status === 'success'
              ? `Model ID ${scanResult.modelId} and Model Name ${scanResult.modelName} has been added!`
              : scanResult.errorMessage}
          </div>
        )}
      </div>
    </div>
  );
}
