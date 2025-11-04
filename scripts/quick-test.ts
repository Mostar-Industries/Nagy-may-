#!/usr/bin/env tsx
/**
 * Quick Detection System Test
 * Checks configuration and connectivity
 */

console.log('🧪 Quick Detection System Test\n')

// 1. Check Environment Variables
console.log('1️⃣ Environment Configuration:')
const envVars = [
  'NEXT_PUBLIC_SUPABASE_URL',
  'NEXT_PUBLIC_SUPABASE_ANON_KEY',
  'DATABASE_URL'
]

let envConfigured = true
envVars.forEach(varName => {
  const value = process.env[varName]
  const status = value ? '✅' : '❌'
  const display = value ? `${value.substring(0, 20)}...` : 'Not set'
  console.log(`   ${status} ${varName}: ${display}`)
  if (!value) envConfigured = false
})

console.log('\n2️⃣ File System Check:')
const fs = require('fs')
const path = require('path')

const criticalFiles = [
  'hooks/use-realtime-detections.ts',
  'app/api/detections/route.ts',
  'app/api/detections/stream/route.ts',
  'lib/db/detection-writer.ts',
  'components/recent-detections.tsx',
  'components/cesium-map.tsx'
]

let allFilesExist = true
criticalFiles.forEach(file => {
  const filePath = path.join(process.cwd(), file)
  const exists = fs.existsSync(filePath)
  const status = exists ? '✅' : '❌'
  console.log(`   ${status} ${file}`)
  if (!exists) allFilesExist = false
})

console.log('\n3️⃣ Network Check:')

async function checkPort(port: number, name: string) {
  try {
    const response = await fetch(`http://localhost:${port}`, {
      method: 'GET'
    })
    console.log(`   ✅ ${name} - Port ${port} is accessible`)
    return true
  } catch (error) {
    console.log(`   ❌ ${name} - Port ${port} not accessible`)
    return false
  }
}

async function runNetworkTests() {
  await checkPort(3000, 'Next.js Frontend')
  await checkPort(5001, 'ML Service')
  
  console.log('\n' + '='.repeat(60))
  console.log('📊 Test Summary')
  console.log('='.repeat(60))
  
  if (!envConfigured) {
    console.log('\n⚠️  Environment variables not configured')
    console.log('   Create a .env.local file with:')
    console.log('   - NEXT_PUBLIC_SUPABASE_URL')
    console.log('   - NEXT_PUBLIC_SUPABASE_ANON_KEY')
    console.log('   - DATABASE_URL')
  }
  
  if (!allFilesExist) {
    console.log('\n⚠️  Some critical files are missing')
  }
  
  console.log('\n💡 To start the system:')
  console.log('   1. Configure .env.local with Supabase credentials')
  console.log('   2. Run: npm run dev')
  console.log('   3. Open: http://localhost:3000/monitoring')
  console.log('   4. Test detections and real-time updates')
  
  console.log('\n📚 Documentation:')
  console.log('   - TEST_DETECTION_FLOW.md - Complete testing guide')
  console.log('   - AUTONOMOUS_DETECTION.md - System architecture')
  console.log('   - QUICK_START_AUTONOMOUS.md - Quick start guide\n')
}

runNetworkTests()
