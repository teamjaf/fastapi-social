# Friend Connection System Test Script
# Make sure your FastAPI server is running on http://localhost:9090

$baseUrl = "http://localhost:9090/api/v1"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "=== Friend Connection System Test ===" -ForegroundColor Green

# Step 1: Register Test Users
Write-Host "`n1. Registering test users..." -ForegroundColor Yellow

$user1 = @{
    email = "john.doe@university.edu"
    username = "johndoe"
    password = "password123"
    full_name = "John Doe"
    university = "Tech University"
} | ConvertTo-Json

$user2 = @{
    email = "jane.smith@university.edu"
    username = "janesmith"
    password = "password123"
    full_name = "Jane Smith"
    university = "Tech University"
} | ConvertTo-Json

$user3 = @{
    email = "bob.wilson@university.edu"
    username = "bobwilson"
    password = "password123"
    full_name = "Bob Wilson"
    university = "State University"
} | ConvertTo-Json

try {
    $response1 = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $user1 -Headers $headers
    Write-Host "✓ User 1 (John Doe) registered: ID $($response1.id)" -ForegroundColor Green
    
    $response2 = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $user2 -Headers $headers
    Write-Host "✓ User 2 (Jane Smith) registered: ID $($response2.id)" -ForegroundColor Green
    
    $response3 = Invoke-RestMethod -Uri "$baseUrl/auth/register" -Method POST -Body $user3 -Headers $headers
    Write-Host "✓ User 3 (Bob Wilson) registered: ID $($response3.id)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Users might already exist, continuing..." -ForegroundColor Yellow
}

# Step 2: Login Users
Write-Host "`n2. Logging in users..." -ForegroundColor Yellow

$login1 = @{
    username = "johndoe"
    password = "password123"
} | ConvertTo-Json

$login2 = @{
    username = "janesmith"
    password = "password123"
} | ConvertTo-Json

try {
    $token1 = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $login1 -Headers $headers
    $token2 = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $login2 -Headers $headers
    
    $authHeaders1 = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($token1.access_token)"
    }
    
    $authHeaders2 = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($token2.access_token)"
    }
    
    Write-Host "✓ User 1 logged in successfully" -ForegroundColor Green
    Write-Host "✓ User 2 logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 3: Test Connection Requests
Write-Host "`n3. Testing connection requests..." -ForegroundColor Yellow

try {
    # User 1 sends connection request to User 2
    $connection1 = Invoke-RestMethod -Uri "$baseUrl/connections/request/2" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 sent connection request to User 2: ID $($connection1.id)" -ForegroundColor Green
    
    # User 1 sends connection request to User 3
    $connection2 = Invoke-RestMethod -Uri "$baseUrl/connections/request/3" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 sent connection request to User 3: ID $($connection2.id)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Connection requests might already exist" -ForegroundColor Yellow
}

# Step 4: Check Pending Requests
Write-Host "`n4. Checking pending requests..." -ForegroundColor Yellow

try {
    $pendingReceived = Invoke-RestMethod -Uri "$baseUrl/connections/requests/received" -Method GET -Headers $authHeaders2
    Write-Host "✓ User 2 has $($pendingReceived.total) pending requests received" -ForegroundColor Green
    
    $pendingSent = Invoke-RestMethod -Uri "$baseUrl/connections/requests/sent" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($pendingSent.total) pending requests sent" -ForegroundColor Green
} catch {
    Write-Host "❌ Error checking pending requests: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Accept Connection Request
Write-Host "`n5. Accepting connection request..." -ForegroundColor Yellow

try {
    $acceptResponse = Invoke-RestMethod -Uri "$baseUrl/connections/accept/1" -Method POST -Headers $authHeaders2
    Write-Host "✓ User 2 accepted connection request from User 1" -ForegroundColor Green
    Write-Host "  Connection status: $($acceptResponse.status)" -ForegroundColor Cyan
} catch {
    Write-Host "⚠ Connection might already be accepted or not found" -ForegroundColor Yellow
}

# Step 6: Check Connection Status
Write-Host "`n6. Checking connection status..." -ForegroundColor Yellow

try {
    $status = Invoke-RestMethod -Uri "$baseUrl/connections/status/1" -Method GET -Headers $authHeaders2
    Write-Host "✓ Connection status between User 2 and User 1: $($status.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Error checking connection status: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Get My Connections
Write-Host "`n7. Getting user connections..." -ForegroundColor Yellow

try {
    $connections = Invoke-RestMethod -Uri "$baseUrl/connections/my-connections" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($connections.total) connections" -ForegroundColor Green
    
    $connections2 = Invoke-RestMethod -Uri "$baseUrl/connections/my-connections" -Method GET -Headers $authHeaders2
    Write-Host "✓ User 2 has $($connections2.total) connections" -ForegroundColor Green
} catch {
    Write-Host "❌ Error getting connections: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Get Connection Statistics
Write-Host "`n8. Getting connection statistics..." -ForegroundColor Yellow

try {
    $stats1 = Invoke-RestMethod -Uri "$baseUrl/connections/stats" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 Statistics:" -ForegroundColor Green
    Write-Host "  - Total connections: $($stats1.total_connections)" -ForegroundColor Cyan
    Write-Host "  - Pending received: $($stats1.pending_received)" -ForegroundColor Cyan
    Write-Host "  - Pending sent: $($stats1.pending_sent)" -ForegroundColor Cyan
    Write-Host "  - Blocked users: $($stats1.blocked_users)" -ForegroundColor Cyan
    
    $stats2 = Invoke-RestMethod -Uri "$baseUrl/connections/stats" -Method GET -Headers $authHeaders2
    Write-Host "✓ User 2 Statistics:" -ForegroundColor Green
    Write-Host "  - Total connections: $($stats2.total_connections)" -ForegroundColor Cyan
    Write-Host "  - Pending received: $($stats2.pending_received)" -ForegroundColor Cyan
    Write-Host "  - Pending sent: $($stats2.pending_sent)" -ForegroundColor Cyan
    Write-Host "  - Blocked users: $($stats2.blocked_users)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Error getting statistics: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 9: Get Connection Suggestions
Write-Host "`n9. Getting connection suggestions..." -ForegroundColor Yellow

try {
    $suggestions = Invoke-RestMethod -Uri "$baseUrl/connections/suggestions" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($suggestions.total) connection suggestions" -ForegroundColor Green
    if ($suggestions.suggestions.Count -gt 0) {
        Write-Host "  Top suggestion: $($suggestions.suggestions[0].user.full_name) (Score: $($suggestions.suggestions[0].suggestion_score))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Error getting suggestions: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 10: Test Blocking (Optional)
Write-Host "`n10. Testing user blocking..." -ForegroundColor Yellow

try {
    $blockResponse = Invoke-RestMethod -Uri "$baseUrl/connections/block/3" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 blocked User 3" -ForegroundColor Green
    
    # Try to unblock
    Invoke-RestMethod -Uri "$baseUrl/connections/unblock/3" -Method DELETE -Headers $authHeaders1
    Write-Host "✓ User 1 unblocked User 3" -ForegroundColor Green
} catch {
    Write-Host "⚠ Blocking test skipped (might not be needed)" -ForegroundColor Yellow
}

Write-Host "`n=== Test Complete! ===" -ForegroundColor Green
Write-Host "Check the Swagger UI at http://localhost:9090/docs for more detailed testing" -ForegroundColor Cyan
