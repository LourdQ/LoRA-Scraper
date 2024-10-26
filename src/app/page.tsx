'use client';

import { useState } from 'react';

export default function Home() {
  const [modelId, setModelId] = useState('');
  const [status, setStatus] = useState(null);

  const handleScan = async () => {
    try {
      const response = await fetch('https://lora-scraper-production.up.railway.app/api/start-scan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ modelId: parseInt(modelId) }),
      });
      const data = await response.json();
      setStatus(data);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <main className="p-4">
      <h1>LoRA Scraper</h1>
      <div>
        <input
          type="text"
          value={modelId}
          onChange={(e) => setModelId(e.target.value)}
          placeholder="Enter Model ID"
        />
        <button onClick={handleScan}>Scan</button>
      </div>
      {status && (
        <pre>
          {JSON.stringify(status, null, 2)}
        </pre>
      )}
    </main>
  );
}
