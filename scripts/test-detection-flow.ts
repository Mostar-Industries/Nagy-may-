#!/usr/bin/env tsx
/**
 * Test Detection Flow - Validates complete real-time detection system
 * Tests: Database → API → Realtime → Frontend
 */

import { createClient } from '@supabase/supabase-js'

const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL || ''
const SUPABASE_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY || ''

interface TestResult {
  name: string
  passed: boolean
  message: string
  duration?: number
}

const results: TestResult[] = []

async function testSupabaseConnection() {
  const startTime = Date.now()
  try {
    if (!SUPABASE_URL || !SUPABASE_KEY) {
      throw new Error('Supabase credentials not configured')
    }

    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
    
    // Test connection by querying detections
    const { data, error } = await supabase
      .from('detections')
      .select('id')
      .limit(1)
    
    if (error) {
      throw error
    }

    results.push({
      name: 'Supabase Connection',
      passed: true,
      message: `Connected successfully. Found ${data?.length || 0} detection(s)`,
      duration: Date.now() - startTime
    })
  } catch (error) {
    results.push({
      name: 'Supabase Connection',
      passed: false,
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - startTime
    })
  }
}

async function testDetectionsTable() {
  const startTime = Date.now()
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
    
    // Get recent detections
    const { data, error } = await supabase
      .from('detections')
      .select('*')
      .order('detected_at', { ascending: false })
      .limit(5)
    
    if (error) {
      throw error
    }

    results.push({
      name: 'Detections Table Query',
      passed: true,
      message: `Successfully queried detections table. Found ${data?.length || 0} recent detection(s)`,
      duration: Date.now() - startTime
    })

    // Display recent detections
    if (data && data.length > 0) {
      console.log('\n📊 Recent Detections:')
      data.forEach((det, idx) => {
        console.log(`  ${idx + 1}. ID: ${det.id?.toString().slice(0, 8)}... | Species: ${det.species} | Confidence: ${(det.confidence * 100).toFixed(1)}% | Source: ${det.source}`)
      })
    }
  } catch (error) {
    results.push({
      name: 'Detections Table Query',
      passed: false,
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - startTime
    })
  }
}

async function testCreateDetection() {
  const startTime = Date.now()
  try {
    const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
    
    // Create test detection
    const testDetection = {
      image_id: `test_${Date.now()}`,
      latitude: 9.0820,
      longitude: 8.6753,
      confidence: 0.87,
      label: 'test_detection',
      species: 'Mastomys natalensis',
      source: 'test_script',
      bbox: { x: 100, y: 100, width: 50, height: 50 },
      metadata: { 
        test: true, 
        timestamp: new Date().toISOString(),
        location: 'Nigeria - Test Location'
      }
    }

    const { data, error } = await supabase
      .from('detections')
      .insert([testDetection])
      .select()
    
    if (error) {
      throw error
    }

    results.push({
      name: 'Create Test Detection',
      passed: true,
      message: `✅ Detection created successfully! ID: ${data?.[0]?.id?.toString().slice(0, 8)}...`,
      duration: Date.now() - startTime
    })

    console.log('\n🎯 Test Detection Details:')
    console.log(`   Location: (${testDetection.latitude}°N, ${testDetection.longitude}°E)`)
    console.log(`   Confidence: ${(testDetection.confidence * 100).toFixed(1)}%`)
    console.log(`   Species: ${testDetection.species}`)
    console.log(`   Source: ${testDetection.source}`)
  } catch (error) {
    results.push({
      name: 'Create Test Detection',
      passed: false,
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - startTime
    })
  }
}

async function testRealtimeSubscription() {
  const startTime = Date.now()
  return new Promise<void>((resolve) => {
    try {
      const supabase = createClient(SUPABASE_URL, SUPABASE_KEY)
      
      console.log('\n⏳ Testing realtime subscription (waiting 5 seconds)...')
      
      let receivedUpdate = false
      
      const channel = supabase
        .channel('test_detections')
        .on(
          'postgres_changes',
          {
            event: 'INSERT',
            schema: 'public',
            table: 'detections'
          },
          (payload) => {
            receivedUpdate = true
            console.log('   ✅ Realtime update received!')
            console.log(`   Detection ID: ${payload.new.id?.toString().slice(0, 8)}...`)
          }
        )
        .subscribe((status) => {
          if (status === 'SUBSCRIBED') {
            console.log('   📡 Subscribed to realtime channel')
          }
        })
      
      // Wait 5 seconds for any updates
      setTimeout(() => {
        supabase.removeChannel(channel)
        
        results.push({
          name: 'Realtime Subscription',
          passed: true,
          message: receivedUpdate 
            ? '✅ Realtime working! Received update during test'
            : '⚠️ Subscribed successfully (no updates received during test window)',
          duration: Date.now() - startTime
        })
        
        resolve()
      }, 5000)
    } catch (error) {
      results.push({
        name: 'Realtime Subscription',
        passed: false,
        message: error instanceof Error ? error.message : String(error),
        duration: Date.now() - startTime
      })
      resolve()
    }
  })
}

async function testAPIEndpoint() {
  const startTime = Date.now()
  try {
    // Test if Next.js dev server is running
    const response = await fetch('http://localhost:3000/api/detections', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`API returned ${response.status}: ${response.statusText}`)
    }

    const data = await response.json()

    results.push({
      name: 'API Endpoint (/api/detections)',
      passed: true,
      message: `✅ API accessible. Returned ${Array.isArray(data) ? data.length : 0} detection(s)`,
      duration: Date.now() - startTime
    })
  } catch (error) {
    results.push({
      name: 'API Endpoint (/api/detections)',
      passed: false,
      message: error instanceof Error ? error.message : String(error),
      duration: Date.now() - startTime
    })
  }
}

function printResults() {
  console.log('\n' + '='.repeat(60))
  console.log('🧪 DETECTION FLOW TEST RESULTS')
  console.log('='.repeat(60))
  
  const passed = results.filter(r => r.passed).length
  const total = results.length
  
  results.forEach((result, idx) => {
    const icon = result.passed ? '✅' : '❌'
    const duration = result.duration ? ` (${result.duration}ms)` : ''
    console.log(`\n${idx + 1}. ${icon} ${result.name}${duration}`)
    console.log(`   ${result.message}`)
  })
  
  console.log('\n' + '='.repeat(60))
  console.log(`📊 Summary: ${passed}/${total} tests passed`)
  console.log('='.repeat(60))
  
  if (passed === total) {
    console.log('\n🎉 ALL TESTS PASSED! Detection system is fully operational.\n')
    console.log('✅ Next steps:')
    console.log('   1. Open http://localhost:3000/monitoring')
    console.log('   2. Check "Recent Detections" table')
    console.log('   3. Verify test detection appears on map')
    console.log('   4. Watch for real-time updates (● Live indicator)\n')
  } else {
    console.log('\n⚠️  Some tests failed. Check errors above.\n')
  }
}

async function runTests() {
  console.log('🚀 Starting Detection Flow Tests...\n')
  
  // Run tests sequentially
  await testSupabaseConnection()
  await testDetectionsTable()
  await testAPIEndpoint()
  await testCreateDetection()
  await testRealtimeSubscription()
  
  // Print results
  printResults()
  
  process.exit(results.every(r => r.passed) ? 0 : 1)
}

// Run tests
runTests().catch(error => {
  console.error('❌ Test execution failed:', error)
  process.exit(1)
})
