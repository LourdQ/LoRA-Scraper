import { NextResponse } from 'next/server';

export async function POST() {
  try {
    // TODO: Call Python script
    const response = await fetch('http://localhost:5000/start-scan', {
      method: 'POST',
    });
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to start scan' },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // TODO: Get scan status from Python backend
    const response = await fetch('http://localhost:5000/scan-status');
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Failed to get scan status' },
      { status: 500 }
    );
  }
}