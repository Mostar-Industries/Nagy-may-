
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const lat = searchParams.get('lat');
  const lon = searchParams.get('lon');

  if (!lat || !lon) {
    return NextResponse.json({ error: 'Latitude and longitude are required' }, { status: 400 });
  }

  if (!process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY) {
    return NextResponse.json({ error: 'OpenWeather API key is not configured' }, { status: 500 });
  }

  const url = `https://api.openweathermap.org/data/2.5/weather?lat=${lat}&lon=${lon}&units=metric&appid=${process.env.NEXT_PUBLIC_OPENWEATHER_API_KEY}`;

  try {
    const response = await fetch(url);
    if (!response.ok) {
      const errorText = await response.text();
      return NextResponse.json({ error: `Failed to fetch from OpenWeather API: ${errorText}` }, { status: response.status });
    }
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    const message = error instanceof Error ? error.message : 'An unknown error occurred';
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
