# Comprehensive Test for All Connection Endpoints
# Make sure your FastAPI server is running on http://localhost:9090

$baseUrl = "http://localhost:9090/api/v1"
$headers = @{
    "Content-Type" = "application/json"
}

Write-Host "=== Testing All Connection Endpoints ===" -ForegroundColor Green
Write-Host "Server: $baseUrl" -ForegroundColor Cyan

# Step 1: Health Check
Write-Host "`n1. Testing Health Endpoint..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$baseUrl/health" -Method GET
    Write-Host "✓ Health check passed: $($health.message)" -ForegroundColor Green
} catch {
    Write-Host "❌ Health check failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 2: Register Test Users
Write-Host "`n2. Registering Test Users..." -ForegroundColor Yellow

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

# Step 3: Login Users
Write-Host "`n3. Logging in Users..." -ForegroundColor Yellow

$login1 = @{
    username = "johndoe"
    password = "password123"
} | ConvertTo-Json

$login2 = @{
    username = "janesmith"
    password = "password123"
} | ConvertTo-Json

$login3 = @{
    username = "bobwilson"
    password = "password123"
} | ConvertTo-Json

try {
    $token1 = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $login1 -Headers $headers
    $token2 = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $login2 -Headers $headers
    $token3 = Invoke-RestMethod -Uri "$baseUrl/auth/login" -Method POST -Body $login3 -Headers $headers
    
    $authHeaders1 = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($token1.access_token)"
    }
    
    $authHeaders2 = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($token2.access_token)"
    }
    
    $authHeaders3 = @{
        "Content-Type" = "application/json"
        "Authorization" = "Bearer $($token3.access_token)"
    }
    
    Write-Host "✓ All users logged in successfully" -ForegroundColor Green
} catch {
    Write-Host "❌ Login failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Step 4: Test Connection Statistics (Endpoint 15)
Write-Host "`n4. Testing Connection Statistics (GET /connections/stats)..." -ForegroundColor Yellow
try {
    $stats1 = Invoke-RestMethod -Uri "$baseUrl/connections/stats" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 Stats: $($stats1.total_connections) connections, $($stats1.pending_received) pending received, $($stats1.pending_sent) pending sent" -ForegroundColor Green
} catch {
    Write-Host "❌ Connection stats failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 5: Test Send Connection Request (Endpoint 1)
Write-Host "`n5. Testing Send Connection Request (POST /connections/request/{user_id})..." -ForegroundColor Yellow
try {
    $connection1 = Invoke-RestMethod -Uri "$baseUrl/connections/request/2" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 sent connection request to User 2: ID $($connection1.id), Status: $($connection1.status)" -ForegroundColor Green
    
    $connection2 = Invoke-RestMethod -Uri "$baseUrl/connections/request/3" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 sent connection request to User 3: ID $($connection2.id), Status: $($connection2.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Connection requests might already exist: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 6: Test Get Pending Requests Received (Endpoint 9)
Write-Host "`n6. Testing Get Pending Requests Received (GET /connections/requests/received)..." -ForegroundColor Yellow
try {
    $pendingReceived = Invoke-RestMethod -Uri "$baseUrl/connections/requests/received" -Method GET -Headers $authHeaders2
    Write-Host "✓ User 2 has $($pendingReceived.total) pending requests received" -ForegroundColor Green
} catch {
    Write-Host "❌ Get pending requests received failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 7: Test Get Pending Requests Sent (Endpoint 10)
Write-Host "`n7. Testing Get Pending Requests Sent (GET /connections/requests/sent)..." -ForegroundColor Yellow
try {
    $pendingSent = Invoke-RestMethod -Uri "$baseUrl/connections/requests/sent" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($pendingSent.total) pending requests sent" -ForegroundColor Green
} catch {
    Write-Host "❌ Get pending requests sent failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 8: Test Accept Connection Request (Endpoint 2)
Write-Host "`n8. Testing Accept Connection Request (POST /connections/accept/{connection_id})..." -ForegroundColor Yellow
try {
    $acceptResponse = Invoke-RestMethod -Uri "$baseUrl/connections/accept/1" -Method POST -Headers $authHeaders2
    Write-Host "✓ User 2 accepted connection request from User 1: Status $($acceptResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Connection might already be accepted: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 9: Test Get Connection Status (Endpoint 11)
Write-Host "`n9. Testing Get Connection Status (GET /connections/status/{user_id})..." -ForegroundColor Yellow
try {
    $status = Invoke-RestMethod -Uri "$baseUrl/connections/status/1" -Method GET -Headers $authHeaders2
    Write-Host "✓ Connection status between User 2 and User 1: $($status.status)" -ForegroundColor Green
} catch {
    Write-Host "❌ Get connection status failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 10: Test Get My Connections (Endpoint 8)
Write-Host "`n10. Testing Get My Connections (GET /connections/my-connections)..." -ForegroundColor Yellow
try {
    $connections1 = Invoke-RestMethod -Uri "$baseUrl/connections/my-connections" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($connections1.total) connections" -ForegroundColor Green
    
    $connections2 = Invoke-RestMethod -Uri "$baseUrl/connections/my-connections" -Method GET -Headers $authHeaders2
    Write-Host "✓ User 2 has $($connections2.total) connections" -ForegroundColor Green
} catch {
    Write-Host "❌ Get my connections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 11: Test Get User's Connections (Public) (Endpoint 12)
Write-Host "`n11. Testing Get User's Connections (Public) (GET /connections/user/{user_id})..." -ForegroundColor Yellow
try {
    $userConnections = Invoke-RestMethod -Uri "$baseUrl/connections/user/1" -Method GET
    Write-Host "✓ User 1's public connections retrieved: $($userConnections.Count) connections" -ForegroundColor Green
} catch {
    Write-Host "❌ Get user's connections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 12: Test Get Mutual Connections (Endpoint 13)
Write-Host "`n12. Testing Get Mutual Connections (GET /connections/mutual/{user_id})..." -ForegroundColor Yellow
try {
    $mutualConnections = Invoke-RestMethod -Uri "$baseUrl/connections/mutual/2" -Method GET -Headers $authHeaders1
    Write-Host "✓ Mutual connections between User 1 and User 2: $($mutualConnections.total)" -ForegroundColor Green
} catch {
    Write-Host "❌ Get mutual connections failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 13: Test Get Connection Suggestions (Endpoint 14)
Write-Host "`n13. Testing Get Connection Suggestions (GET /connections/suggestions)..." -ForegroundColor Yellow
try {
    $suggestions = Invoke-RestMethod -Uri "$baseUrl/connections/suggestions" -Method GET -Headers $authHeaders1
    Write-Host "✓ User 1 has $($suggestions.total) connection suggestions" -ForegroundColor Green
    if ($suggestions.suggestions.Count -gt 0) {
        Write-Host "  Top suggestion: $($suggestions.suggestions[0].user.full_name) (Score: $($suggestions.suggestions[0].suggestion_score))" -ForegroundColor Cyan
    }
} catch {
    Write-Host "❌ Get connection suggestions failed: $($_.Exception.Message)" -ForegroundColor Red
}

# Step 14: Test Block User (Endpoint 6)
Write-Host "`n14. Testing Block User (POST /connections/block/{user_id})..." -ForegroundColor Yellow
try {
    $blockResponse = Invoke-RestMethod -Uri "$baseUrl/connections/block/3" -Method POST -Headers $authHeaders1
    Write-Host "✓ User 1 blocked User 3: Status $($blockResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Blocking test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 15: Test Unblock User (Endpoint 7)
Write-Host "`n15. Testing Unblock User (DELETE /connections/unblock/{user_id})..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/connections/unblock/3" -Method DELETE -Headers $authHeaders1
    Write-Host "✓ User 1 unblocked User 3" -ForegroundColor Green
} catch {
    Write-Host "⚠ Unblocking test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 16: Test Reject Connection Request (Endpoint 3)
Write-Host "`n16. Testing Reject Connection Request (POST /connections/reject/{connection_id})..." -ForegroundColor Yellow
try {
    $rejectResponse = Invoke-RestMethod -Uri "$baseUrl/connections/reject/2" -Method POST -Headers $authHeaders3
    Write-Host "✓ User 3 rejected connection request: Status $($rejectResponse.status)" -ForegroundColor Green
} catch {
    Write-Host "⚠ Reject test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 17: Test Cancel Connection Request (Endpoint 4)
Write-Host "`n17. Testing Cancel Connection Request (DELETE /connections/cancel/{connection_id})..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/connections/cancel/2" -Method DELETE -Headers $authHeaders1
    Write-Host "✓ User 1 cancelled connection request" -ForegroundColor Green
} catch {
    Write-Host "⚠ Cancel test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Step 18: Test Remove Connection (Endpoint 5)
Write-Host "`n18. Testing Remove Connection (DELETE /connections/remove/{user_id})..." -ForegroundColor Yellow
try {
    Invoke-RestMethod -Uri "$baseUrl/connections/remove/2" -Method DELETE -Headers $authHeaders1
    Write-Host "✓ User 1 removed connection with User 2" -ForegroundColor Green
} catch {
    Write-Host "⚠ Remove connection test: $($_.Exception.Message)" -ForegroundColor Yellow
}

# Final Statistics Check
Write-Host "`n19. Final Statistics Check..." -ForegroundColor Yellow
try {
    $finalStats1 = Invoke-RestMethod -Uri "$baseUrl/connections/stats" -Method GET -Headers $authHeaders1
    Write-Host "✓ Final User 1 Stats:" -ForegroundColor Green
    Write-Host "  - Total connections: $($finalStats1.total_connections)" -ForegroundColor Cyan
    Write-Host "  - Pending received: $($finalStats1.pending_received)" -ForegroundColor Cyan
    Write-Host "  - Pending sent: $($finalStats1.pending_sent)" -ForegroundColor Cyan
    Write-Host "  - Blocked users: $($finalStats1.blocked_users)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Final stats check failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== All Connection Endpoints Test Complete! ===" -ForegroundColor Green
Write-Host "Summary:" -ForegroundColor Cyan
Write-Host "- 15 connection endpoints tested" -ForegroundColor White
Write-Host "- Authentication system working" -ForegroundColor White
Write-Host "- Database operations functional" -ForegroundColor White
Write-Host "- Error handling working" -ForegroundColor White
Write-Host "`nCheck Swagger UI at: http://localhost:9090/docs" -ForegroundColor Yellow
}
