# Simple Connection System Test
$baseUrl = "http://localhost:9090/api/v1"

Write-Host "=== Simple Connection Test ===" -ForegroundColor Green

# Test 1: Health Check
Write-Host "`n1. Testing health endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✓ Health check passed: $($health.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Register a test user
Write-Host "`n2. Registering test user..." -ForegroundColor Yellow
$userData = @{
    email = "testuser@university.edu"
    username = "testuser123"
    password = "password123"
    full_name = "Test User"
    university = "Test University"
} | ConvertTo-Json

$headers = @{
    "Content-Type" = "application/json"
}

try {
    $user = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $userData -Headers $headers
    Write-Host "✓ User registered: $($user.username) (ID: $($user.id))" -ForegroundColor Green
} catch {
    Write-Host "⚠ User might already exist, trying to login..." -ForegroundColor Yellow
}

# Test 3: Login
Write-Host "`n3. Logging in..." -ForegroundColor Yellow
$loginData = @{
    username = "testuser123"
    password = "password123"
} | ConvertTo-Json

try {
    $login = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $loginData -Headers $headers
    Write-Host "✓ Login successful!" -ForegroundColor Green
    
    $authHeaders = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($login.access_token)"
    }
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 4: Get connection statistics
Write-Host "`n4. Testing connection statistics..." -ForegroundColor Yellow
try {
    $stats = Invoke-RestMethod -Uri "$baseUrl/connections/stats" -Method GET -Headers $authHeaders
    Write-Host "✓ Connection stats retrieved:" -ForegroundColor Green
    Write-Host "  - Total connections: $($stats.total_connections)" -ForegroundColor Cyan
    Write-Host "  - Pending received: $($stats.pending_received)" -ForegroundColor Cyan
    Write-Host "  - Pending sent: $($stats.pending_sent)" -ForegroundColor Cyan
    Write-Host "  - Blocked users: $($stats.blocked_users)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Connection stats failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Get my connections
Write-Host "`n5. Testing get my connections..." -ForegroundColor Yellow
try {
    $connections = Invoke-RestMethod -Uri "$baseUrl/connections/my-connections" -Method GET -Headers $authHeaders
    Write-Host "✓ My connections retrieved: $($connections.total) total" -ForegroundColor Green
} catch {
    Write-Host "❌ Get connections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Get connection suggestions
Write-Host "`n6. Testing connection suggestions..." -ForegroundColor Yellow
try {
    $suggestions = Invoke-RestMethod -Uri "$baseUrl/connections/suggestions" -Method GET -Headers $authHeaders
    Write-Host "✓ Connection suggestions retrieved: $($suggestions.total) suggestions" -ForegroundColor Green
} catch {
    Write-Host "❌ Connection suggestions failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Basic Tests Complete! ===" -ForegroundColor Green
Write-Host "For full testing, use the Swagger UI at: http://localhost:9090/docs" -ForegroundColor Cyan
