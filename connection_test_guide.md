# Friend Connection System - Testing Guide

## Prerequisites
- FastAPI server running on http://localhost:9090
- Access to terminal/PowerShell

## Step-by-Step Testing

### Step 1: Register Test Users

```bash
# Register User 1 (John Doe)
curl -X POST "http://localhost:9090/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@university.edu",
    "username": "johndoe",
    "password": "password123",
    "full_name": "John Doe",
    "university": "Tech University"
  }'

# Register User 2 (Jane Smith)
curl -X POST "http://localhost:9090/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "jane.smith@university.edu",
    "username": "janesmith",
    "password": "password123",
    "full_name": "Jane Smith",
    "university": "Tech University"
  }'
```

### Step 2: Login and Get Tokens

```bash
# Login User 1
curl -X POST "http://localhost:9090/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "johndoe",
    "password": "password123"
  }'

# Login User 2
curl -X POST "http://localhost:9090/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "janesmith",
    "password": "password123"
  }'
```

**Copy the access_token from both responses!**

### Step 3: Test Connection Endpoints

Replace `YOUR_TOKEN_1` and `YOUR_TOKEN_2` with actual tokens from Step 2.

```bash
# 1. Send connection request (User 1 to User 2)
curl -X POST "http://localhost:9090/api/v1/connections/request/2" \
  -H "Authorization: Bearer YOUR_TOKEN_1" \
  -H "Content-Type: application/json"

# 2. Check pending requests received (User 2)
curl -X GET "http://localhost:9090/api/v1/connections/requests/received" \
  -H "Authorization: Bearer YOUR_TOKEN_2"

# 3. Accept connection request (User 2 accepts from User 1)
curl -X POST "http://localhost:9090/api/v1/connections/accept/1" \
  -H "Authorization: Bearer YOUR_TOKEN_2" \
  -H "Content-Type: application/json"

# 4. Check connection status
curl -X GET "http://localhost:9090/api/v1/connections/status/1" \
  -H "Authorization: Bearer YOUR_TOKEN_2"

# 5. Get my connections
curl -X GET "http://localhost:9090/api/v1/connections/my-connections" \
  -H "Authorization: Bearer YOUR_TOKEN_1"

# 6. Get connection statistics
curl -X GET "http://localhost:9090/api/v1/connections/stats" \
  -H "Authorization: Bearer YOUR_TOKEN_1"

# 7. Get connection suggestions
curl -X GET "http://localhost:9090/api/v1/connections/suggestions" \
  -H "Authorization: Bearer YOUR_TOKEN_1"
```

## PowerShell Commands (Alternative)

```powershell
# Register User 1
$user1 = @{
    email = "john.doe@university.edu"
    username = "johndoe"
    password = "password123"
    full_name = "John Doe"
    university = "Tech University"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:9090/api/v1/auth/register" -Method POST -Body $user1 -ContentType "application/json"

# Login User 1
$login1 = @{
    username = "johndoe"
    password = "password123"
} | ConvertTo-Json

$token1 = Invoke-RestMethod -Uri "http://localhost:9090/api/v1/auth/login" -Method POST -Body $login1 -ContentType "application/json"

# Test connection stats
$headers = @{
    "Authorization" = "Bearer $($token1.access_token)"
}

Invoke-RestMethod -Uri "http://localhost:9090/api/v1/connections/stats" -Method GET -Headers $headers
```

## Expected Responses

### Connection Stats Response:
```json
{
  "total_connections": 0,
  "pending_received": 0,
  "pending_sent": 0,
  "blocked_users": 0
}
```

### Connection Request Response:
```json
{
  "id": 1,
  "requester": {
    "id": 1,
    "username": "johndoe",
    "full_name": "John Doe",
    "university": "Tech University"
  },
  "addressee": {
    "id": 2,
    "username": "janesmith",
    "full_name": "Jane Smith",
    "university": "Tech University"
  },
  "status": "pending",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00",
  "responded_at": null
}
```

## Common Issues & Solutions

1. **401 Unauthorized**: Make sure you're using a valid JWT token
2. **404 Not Found**: Check if the user ID exists
3. **400 Bad Request**: Connection might already exist
4. **403 Forbidden**: You don't have permission for this action

## Quick Test Checklist

- [ ] Health endpoint works
- [ ] User registration works
- [ ] User login works
- [ ] Connection stats endpoint works
- [ ] Send connection request works
- [ ] Accept connection request works
- [ ] Get connections list works
- [ ] Connection suggestions work
