'use client';
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
  const [results, setResults] = useState<ScanResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  // Single effect for fetching results
  useEffect(() => {
    const fetchResults = async () => {
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/scan-status`);
        const data = await response.json();
        if (data.results) {
          // Show newest results first
          setResults(data.results.reverse());
          setError(null);
        }
      } catch (err) {
        console.error('Failed to fetch results:', err);
        setError('Failed to load scan results');
      }
    };

    // Initial fetch
    fetchResults();

    // Set up polling interval
    const intervalId = setInterval(fetchResults, 3000);

    // Cleanup on unmount
    return () => clearInterval(intervalId);
  }, []);

  if (error) {
    return (
      <div className="p-4 border rounded-lg bg-white shadow-sm">
        <h2 className="text-xl font-semibold mb-4">Scan Results</h2>
        <div className="text-red-600 text-sm p-2 bg-red-50 rounded">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 border rounded-lg bg-white shadow-sm">
      <h2 className="text-xl font-semibold mb-4">Scan Results</h2>
      {results.length === 0 ? (
        <p className="text-gray-500">No scans performed yet.</p>
      ) : (
        <div className="space-y-4">
          {results.map((result) => (
            <div 
              key={result.id}
              className="p-4 border rounded hover:bg-gray-50 transition-colors"
            >
              <div className="flex justify-between items-start mb-2">
                <div>
                  <h3 className="font-medium text-lg">
                    {result.modelName || `Model ${result.modelId}`}
                  </h3>
                  {result.author && (
                    <p className="text-sm text-gray-600">
                      by {result.author}
                    </p>
                  )}
                </div>
                <span className={`px-2 py-1 rounded text-sm ${
                  result.status === 'success' 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {result.status}
                </span>
              </div>
              <div className="text-sm text-gray-600 space-y-1">
                <div className="flex justify-between">
                  <span>Model ID:</span>
                  <span className="font-medium">{result.modelId}</span>
                </div>
                <div className="flex justify-between">
                  <span>Examples found:</span>
                  <span className="font-medium">{result.foundItems}</span>
                </div>
                <div className="flex justify-between">
                  <span>Scanned:</span>
                  <span className="font-medium">
                    {new Date(result.timestamp).toLocaleString()}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
