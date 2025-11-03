/**
 * Test script for YOLO inference system
 * Usage: tsx scripts/test-inference.ts
 */

import fs from 'fs'
import path from 'path'

const API_BASE = process.env.API_BASE || 'http://localhost:5000'

async function testInference() {
  console.log('🧪 Testing YOLO Inference System\n')
  
  // 1. Test with sample image
  console.log('1️⃣ Testing image inference...')
  
  // Create a minimal test image (1x1 red pixel)
  const testImageBase64 = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8DwHwAFBQIAX8jx0gAAAABJRU5ErkJggg=='
  
  try {
    const response = await fetch(`${API_BASE}/api/detections/inference`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        imageBase64: testImageBase64,
        latitude: 9.0820,
        longitude: 8.6753,
        source: 'test_script',
        confThreshold: 0.3,
        metadata: {
          test: true,
          timestamp: new Date().toISOString()
        }
      })
    })
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${await response.text()}`)
    }
    
    const result = await response.json()
    console.log('✅ Inference successful!')
    console.log('   Image ID:', result.detection.image_id)
    console.log('   Detections:', result.detection.detections.length)
    console.log('   Processing time:', result.detection.processing_time_ms + 'ms')
    console.log('   Saved to:', JSON.stringify(result.detection.saved_to))
    console.log()
  } catch (error) {
    console.error('❌ Inference failed:', error)
    console.log()
  }
  
  // 2. Test SSE stream
  console.log('2️⃣ Testing SSE stream...')
  console.log('   Connecting to', `${API_BASE}/api/detections/stream`)
  console.log('   (Press Ctrl+C to stop)\n')
  
  try {
    const response = await fetch(`${API_BASE}/api/detections/stream`)
    
    if (!response.ok || !response.body) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    
    let buffer = ''
    let messageCount = 0
    
    while (messageCount < 3) { // Read first 3 messages
      const { value, done } = await reader.read()
      
      if (done) {
        console.log('   Stream ended')
        break
      }
      
      buffer += decoder.decode(value, { stream: true })
      
      // Process complete messages
      const lines = buffer.split('\n\n')
      buffer = lines.pop() || ''
      
      for (const line of lines) {
        if (line.startsWith('data:')) {
          const data = line.substring(5).trim()
          try {
            const parsed = JSON.parse(data)
            messageCount++
            console.log(`   📨 Message ${messageCount}:`, parsed.type || 'unknown')
            if (parsed.type === 'detection') {
              console.log('      Species:', parsed.data.environmental_context?.detections?.[0]?.species)
            }
          } catch {
            // Skip non-JSON messages like heartbeats
          }
        }
      }
    }
    
    reader.cancel()
    console.log('✅ SSE stream working!')
    console.log()
  } catch (error) {
    console.error('❌ SSE stream failed:', error)
    console.log()
  }
  
  // 3. Test detection retrieval
  console.log('3️⃣ Testing detection retrieval...')
  
  try {
    const response = await fetch(`${API_BASE}/api/detections`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`)
    }
    
    const detections = await response.json()
    console.log('✅ Retrieved detections!')
    console.log('   Total:', detections.length)
    if (detections.length > 0) {
      console.log('   Latest:', detections[0].detection_timestamp)
      console.log('   Source:', detections[0].source)
    }
    console.log()
  } catch (error) {
    console.error('❌ Retrieval failed:', error)
    console.log()
  }
  
  console.log('🎉 Test complete!')
}

testInference().catch(console.error)
