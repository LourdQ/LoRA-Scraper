'use client';

import ResultsList from '../components/ResultsList';
import ScanStatus from '../components/ScanStatus';

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto p-4 sm:p-6 lg:p-8">
        <h1 className="text-3xl font-bold mb-8">LoRA Scraper</h1>
        <div className="grid gap-6 md:grid-cols-2">
          <ScanStatus />
          <ResultsList />
        </div>
      </div>
    </main>
  );
}
