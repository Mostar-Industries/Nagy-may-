
/**
 * @jest-environment node
 */
import { GET } from '@/app/api/historical-weather/route';
import { NextRequest } from 'next/server';

// Mock the global fetch function
global.fetch = jest.fn();

describe('GET /api/historical-weather', () => {
  afterEach(() => {
    jest.resetAllMocks();
  });

  it('should return historical weather data for a valid request', async () => {
    const mockWeatherData = { daily: { time: ['2023-01-01'], temperature_2m_max: [10] } };
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockWeatherData,
    });

    const req = new NextRequest('http://localhost/api/historical-weather?lat=34.05&lon=-118.24');
    const response = await GET(req);
    const body = await response.json();

    expect(response.status).toBe(200);
    expect(body).toEqual(mockWeatherData);
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('latitude=34.05&longitude=-118.24'));
  });

  it('should return a 400 error if latitude or longitude is missing', async () => {
    const req = new NextRequest('http://localhost/api/historical-weather?lat=34.05');
    const response = await GET(req);
    const body = await response.json();

    expect(response.status).toBe(400);
    expect(body.error).toBe('Latitude and longitude are required');
    expect(fetch).not.toHaveBeenCalled();
  });

  it('should return a 500 error if the external API call fails', async () => {
    (fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
    });

    const req = new NextRequest('http://localhost/api/historical-weather?lat=34.05&lon=-118.24');
    const response = await GET(req);
    const body = await response.json();

    expect(response.status).toBe(500);
    expect(body.error).toBe('Failed to fetch historical weather data');
  });
});
