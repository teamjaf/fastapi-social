from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.connection import (
    ConnectionResponse, ConnectionStatusResponse, ConnectionStatsResponse,
    ConnectionSuggestion, ConnectionSuggestionListResponse, ConnectionListResponse,
    MutualConnectionResponse, ConnectionStatus
)
from app.schemas.profile import ProfilePublic
from app.repositories.connection import ConnectionRepository
from app.repositories.user import UserRepository
from app.utils.auth import verify_token

router = APIRouter()
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> int:
    """Get current user ID from JWT token"""
    email = verify_token(credentials.credentials)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user.id


@router.post(
    "/request/{user_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Send Connection Request",
    description="Send a connection request to another user"
)
def send_connection_request(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Send a connection request to another user"""
    if current_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot send connection request to yourself"
        )
    
    # Check if target user exists
    user_repo = UserRepository(db)
    target_user = user_repo.get_user_by_id(user_id)
    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    connection_repo = ConnectionRepository(db)
    
    # Check if connection already exists
    existing_connection = connection_repo.get_connection_between_users(current_user_id, user_id)
    if existing_connection:
        if existing_connection.status == ConnectionStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Connection request already pending"
            )
        elif existing_connection.status == ConnectionStatus.ACCEPTED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Users are already connected"
            )
        elif existing_connection.status == ConnectionStatus.BLOCKED:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot send request to blocked user"
            )
    
    # Create connection request
    connection = connection_repo.create_connection(current_user_id, user_id)
    return connection


@router.post(
    "/accept/{connection_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Accept Connection Request",
    description="Accept a pending connection request"
)
def accept_connection_request(
    connection_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Accept a pending connection request"""
    connection_repo = ConnectionRepository(db)
    
    connection = connection_repo.update_connection_status(
        connection_id, ConnectionStatus.ACCEPTED, current_user_id
    )
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found or you don't have permission to accept it"
        )
    
    return connection


@router.post(
    "/reject/{connection_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Reject Connection Request",
    description="Reject a pending connection request"
)
def reject_connection_request(
    connection_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Reject a pending connection request"""
    connection_repo = ConnectionRepository(db)
    
    connection = connection_repo.update_connection_status(
        connection_id, ConnectionStatus.REJECTED, current_user_id
    )
    
    if not connection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found or you don't have permission to reject it"
        )
    
    return connection


@router.delete(
    "/cancel/{connection_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Cancel Connection Request",
    description="Cancel a pending connection request you sent"
)
def cancel_connection_request(
    connection_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Cancel a pending connection request you sent"""
    connection_repo = ConnectionRepository(db)
    
    success = connection_repo.delete_connection(connection_id, current_user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection request not found or you don't have permission to cancel it"
        )


@router.delete(
    "/remove/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Remove Connection",
    description="Remove an existing connection (unfriend)"
)
def remove_connection(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Remove an existing connection (unfriend)"""
    connection_repo = ConnectionRepository(db)
    
    success = connection_repo.remove_connection_between_users(current_user_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Connection not found"
        )


@router.post(
    "/block/{user_id}",
    response_model=ConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Block User",
    description="Block a user (prevents connection requests)"
)
def block_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Block a user (prevents connection requests)"""
    if current_user_id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot block yourself"
        )
    
    # Check if target user exists
    user_repo = UserRepository(db)
    target_user = user_repo.get_user_by_id(user_id)
    if not target_user or not target_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    connection_repo = ConnectionRepository(db)
    connection = connection_repo.block_user(current_user_id, user_id)
    return connection


@router.delete(
    "/unblock/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Unblock User",
    description="Unblock a previously blocked user"
)
def unblock_user(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Unblock a previously blocked user"""
    connection_repo = ConnectionRepository(db)
    
    success = connection_repo.unblock_user(current_user_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User is not blocked"
        )


@router.get(
    "/my-connections",
    response_model=ConnectionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get My Connections",
    description="Get all accepted connections (friends list)"
)
def get_my_connections(
    limit: int = Query(20, ge=1, le=100, description="Number of connections to return"),
    offset: int = Query(0, ge=0, description="Number of connections to skip"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get all accepted connections (friends list)"""
    connection_repo = ConnectionRepository(db)
    
    connections = connection_repo.get_user_connections(current_user_id, limit, offset)
    
    # Get total count
    total = connection_repo.get_connection_stats(current_user_id)['total_connections']
    
    return ConnectionListResponse(
        connections=connections,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/requests/received",
    response_model=ConnectionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Pending Requests (Received)",
    description="Get connection requests sent to you"
)
def get_pending_requests_received(
    limit: int = Query(20, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get connection requests sent to you"""
    connection_repo = ConnectionRepository(db)
    
    connections = connection_repo.get_pending_requests_received(current_user_id, limit, offset)
    
    # Get total count
    total = connection_repo.get_connection_stats(current_user_id)['pending_received']
    
    return ConnectionListResponse(
        connections=connections,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/requests/sent",
    response_model=ConnectionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Pending Requests (Sent)",
    description="Get connection requests you sent"
)
def get_pending_requests_sent(
    limit: int = Query(20, ge=1, le=100, description="Number of requests to return"),
    offset: int = Query(0, ge=0, description="Number of requests to skip"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get connection requests you sent"""
    connection_repo = ConnectionRepository(db)
    
    connections = connection_repo.get_pending_requests_sent(current_user_id, limit, offset)
    
    # Get total count
    total = connection_repo.get_connection_stats(current_user_id)['pending_sent']
    
    return ConnectionListResponse(
        connections=connections,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/status/{user_id}",
    response_model=ConnectionStatusResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Connection Status",
    description="Check connection status with a specific user"
)
def get_connection_status(
    user_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Check connection status with a specific user"""
    connection_repo = ConnectionRepository(db)
    
    connection = connection_repo.get_connection_status(current_user_id, user_id)
    
    if not connection:
        return ConnectionStatusResponse(user_id=user_id, status=None)
    
    return ConnectionStatusResponse(
        user_id=user_id,
        status=connection.status,
        connection_id=connection.id,
        connected_since=connection.created_at if connection.status == ConnectionStatus.ACCEPTED else None
    )


@router.get(
    "/user/{user_id}",
    response_model=List[ProfilePublic],
    status_code=status.HTTP_200_OK,
    summary="Get User's Connections (Public)",
    description="Get a user's connections (friends list)"
)
def get_user_connections(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of connections to return"),
    offset: int = Query(0, ge=0, description="Number of connections to skip"),
    db: Session = Depends(get_db)
):
    """Get a user's connections (friends list)"""
    # Check if user exists
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    connection_repo = ConnectionRepository(db)
    connections = connection_repo.get_user_connections(user_id, limit, offset)
    
    # Extract connected users
    connected_users = []
    for conn in connections:
        if conn.requester_id == user_id:
            connected_users.append(conn.addressee)
        else:
            connected_users.append(conn.requester)
    
    return connected_users


@router.get(
    "/mutual/{user_id}",
    response_model=MutualConnectionResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Mutual Connections",
    description="Get mutual connections with another user"
)
def get_mutual_connections(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of mutual connections to return"),
    offset: int = Query(0, ge=0, description="Number of mutual connections to skip"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get mutual connections with another user"""
    # Check if user exists
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    connection_repo = ConnectionRepository(db)
    mutual_users = connection_repo.get_mutual_connections(current_user_id, user_id, limit, offset)
    
    return MutualConnectionResponse(
        mutual_connections=mutual_users,
        total=len(mutual_users),  # This is approximate, could be improved with a count query
        limit=limit,
        offset=offset
    )


@router.get(
    "/suggestions",
    response_model=ConnectionSuggestionListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Connection Suggestions",
    description="Get friend suggestions based on mutual connections, university, major"
)
def get_connection_suggestions(
    limit: int = Query(20, ge=1, le=100, description="Number of suggestions to return"),
    offset: int = Query(0, ge=0, description="Number of suggestions to skip"),
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get friend suggestions based on mutual connections, university, major"""
    connection_repo = ConnectionRepository(db)
    
    suggestions_data = connection_repo.get_connection_suggestions(current_user_id, limit, offset)
    
    suggestions = []
    for suggestion in suggestions_data:
        suggestions.append(ConnectionSuggestion(
            user=suggestion['user'],
            mutual_connections_count=suggestion['mutual_connections_count'],
            common_university=suggestion['common_university'],
            common_major=suggestion['common_major'],
            common_interests=suggestion['common_interests'],
            suggestion_score=suggestion['suggestion_score']
        ))
    
    return ConnectionSuggestionListResponse(
        suggestions=suggestions,
        total=len(suggestions),
        limit=limit,
        offset=offset
    )


@router.get(
    "/stats",
    response_model=ConnectionStatsResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Connection Statistics",
    description="Get connection statistics for current user"
)
def get_connection_stats(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """Get connection statistics for current user"""
    connection_repo = ConnectionRepository(db)
    stats = connection_repo.get_connection_stats(current_user_id)
    
    return ConnectionStatsResponse(**stats)
