import React, { useState, useEffect } from 'react';

interface ScanResult {
  id: string;
  timestamp: string;
  modelId: number;
  modelName: string;
  author: string;
  foundItems: number;
  status: 'success' | 'error';
}

export default function ResultsList() {
  const [latestResult, setLatestResult] = useState<ScanResult | null>(null);

  // Single effect for fetching the latest result
  useEffect(() => {
    const fetchLatestResult = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scan-status?latest=true`);
        const data = await response.json();
        if (data.result) {
          setLatestResult(data.result);
        }
      } catch (err) {
        console.error('Failed to fetch latest result:', err);
      }
    };

    fetchLatestResult();
  }, []);

  if (!latestResult) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Scan Results</h2>
        <p className="text-gray-500">No recent scans available.</p>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Scan Results</h2>
      <div className={`p-4 border rounded hover:bg-gray-50 transition-colors ${
        latestResult.status === 'success' ? 'border-green-500' : 'border-red-500'
      }`}>
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="font-medium text-lg">
              {latestResult.modelName || `Model ${latestResult.modelId}`}
            </h3>
            {latestResult.author && (
              <p className="text-sm text-gray-600">
                by {latestResult.author}
              </p>
            )}
          </div>
          <span className={`px-2 py-1 rounded text-sm ${
            latestResult.status === 'success'
              ? 'bg-green-100 text-green-800'
              : 'bg-red-100 text-red-800'
          }`}>
            {latestResult.status}
          </span>
        </div>
        <div className="text-sm text-gray-600 space-y-1">
          <div className="flex justify-between">
            <span>Model ID:</span>
            <span className="font-medium">{latestResult.modelId}</span>
          </div>
          <div className="flex justify-between">
            <span>Examples found:</span>
            <span className="font-medium">{latestResult.foundItems}</span>
          </div>
          <div className="flex justify-between">
            <span>Scanned:</span>
            <span className="font-medium">
              {new Date(latestResult.timestamp).toLocaleString()}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
