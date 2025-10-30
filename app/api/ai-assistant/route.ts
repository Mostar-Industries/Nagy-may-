
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  const { prompt } = await request.json();

  if (!prompt) {
    return NextResponse.json({ error: 'Prompt is required' }, { status: 400 });
  }

  if (!process.env.HUGGINGFACE_API_KEY) {
    return NextResponse.json({ error: 'Hugging Face API key is not configured' }, { status: 500 });
  }

  try {
    const response = await fetch(
      'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2',
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${process.env.HUGGINGFACE_API_KEY}`,
        },
        body: JSON.stringify({ inputs: prompt }),
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      console.error('Hugging Face API error:', errorText);
      return NextResponse.json({ error: `Failed to fetch from Hugging Face API: ${errorText}` }, { status: response.status });
    }

    const data = await response.json();
    // The response from the model is an array with a single object containing the generated text.
    const generatedText = data[0]?.generated_text || 'No response from model';

    return NextResponse.json({ response: generatedText });

  } catch (error) {
    const message = error instanceof Error ? error.message : 'An unknown error occurred';
    console.error('Error calling Hugging Face API:', message);
    return NextResponse.json({ error: message }, { status: 500 });
  }
}
