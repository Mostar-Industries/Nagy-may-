# Setup script for Mastomys Detection Inference System (Windows PowerShell)

Write-Host "🚀 Setting up Mastomys Detection Inference System" -ForegroundColor Cyan
Write-Host ""

# 1. Check Node.js
Write-Host "1️⃣ Checking Node.js..." -ForegroundColor Yellow
if (Get-Command node -ErrorAction SilentlyContinue) {
    $nodeVersion = node -v
    Write-Host "✓ Node.js $nodeVersion found" -ForegroundColor Green
} else {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# 2. Check Python
Write-Host ""
Write-Host "2️⃣ Checking Python..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonVersion = python --version
    Write-Host "✓ $pythonVersion found" -ForegroundColor Green
} else {
    Write-Host "❌ Python not found. Please install Python 3.8+" -ForegroundColor Red
    exit 1
}

# 3. Install Python dependencies
Write-Host ""
Write-Host "3️⃣ Installing Python dependencies..." -ForegroundColor Yellow
Set-Location backend\ml_service

if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
}

.\venv\Scripts\Activate.ps1
python -m pip install --quiet --upgrade pip
python -m pip install --quiet ultralytics pillow numpy
Write-Host "✓ Python dependencies installed" -ForegroundColor Green
Set-Location ..\..

# 4. Check YOLO model
Write-Host ""
Write-Host "4️⃣ Checking YOLO model..." -ForegroundColor Yellow
$modelPath = "backend\ml_service\models"
if (-not (Test-Path $modelPath)) {
    New-Item -ItemType Directory -Path $modelPath -Force | Out-Null
}

if (Test-Path "$modelPath\mastomys_natalensis.pt") {
    Write-Host "✓ Custom model found" -ForegroundColor Green
} elseif (Test-Path "$modelPath\yolov8n.pt") {
    Write-Host "✓ YOLOv8n model found" -ForegroundColor Green
} else {
    Write-Host "⚠ No model found. Will download YOLOv8n on first run" -ForegroundColor Yellow
}

# 5. Check database
Write-Host ""
Write-Host "5️⃣ Checking database configuration..." -ForegroundColor Yellow
if (Test-Path ".env") {
    $envContent = Get-Content .env -Raw
    
    if ($envContent -match "DATABASE_URL") {
        Write-Host "✓ DATABASE_URL configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ DATABASE_URL not found in .env" -ForegroundColor Yellow
    }
    
    if ($envContent -match "NEXT_PUBLIC_SUPABASE_URL") {
        Write-Host "✓ Supabase configured" -ForegroundColor Green
    } else {
        Write-Host "⚠ Supabase not configured (realtime features disabled)" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠ .env file not found" -ForegroundColor Yellow
}

# 6. Initialize database
Write-Host ""
Write-Host "6️⃣ Database schema..." -ForegroundColor Yellow
Write-Host "Run this command to initialize the detections table:"
Write-Host "  psql `$env:DATABASE_URL -f scripts\init-detections-table.sql" -ForegroundColor Cyan
Write-Host ""

# 7. Create temp directories
Write-Host "7️⃣ Creating temp directories..." -ForegroundColor Yellow
if (-not (Test-Path "temp\uploads")) {
    New-Item -ItemType Directory -Path "temp\uploads" -Force | Out-Null
}
Write-Host "✓ Temp directories created" -ForegroundColor Green

# 8. Summary
Write-Host ""
Write-Host "✅ Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Initialize database: psql `$env:DATABASE_URL -f scripts\init-detections-table.sql"
Write-Host "  2. Start dev server: pnpm dev"
Write-Host "  3. Test inference: POST to /api/detections/inference"
Write-Host "  4. View docs: cat INFERENCE_SETUP.md"
Write-Host ""
Write-Host "Happy detecting! 🧬" -ForegroundColor Magenta
