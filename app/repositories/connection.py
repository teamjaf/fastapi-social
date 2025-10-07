from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from app.models.connection import Connection
from app.models.user import User
from app.schemas.connection import ConnectionStatus, ConnectionCreate, ConnectionUpdate
from app.schemas.profile import ProfilePublic
from datetime import datetime


class ConnectionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_connection(self, requester_id: int, addressee_id: int) -> Connection:
        """Create a new connection request"""
        connection = Connection(
            requester_id=requester_id,
            addressee_id=addressee_id,
            status=ConnectionStatus.PENDING
        )
        self.db.add(connection)
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def get_connection_by_id(self, connection_id: int) -> Optional[Connection]:
        """Get connection by ID with user details"""
        return self.db.query(Connection).options(
            joinedload(Connection.requester),
            joinedload(Connection.addressee)
        ).filter(Connection.id == connection_id).first()

    def get_connection_between_users(self, user1_id: int, user2_id: int) -> Optional[Connection]:
        """Get connection between two users (in either direction)"""
        return self.db.query(Connection).options(
            joinedload(Connection.requester),
            joinedload(Connection.addressee)
        ).filter(
            or_(
                and_(Connection.requester_id == user1_id, Connection.addressee_id == user2_id),
                and_(Connection.requester_id == user2_id, Connection.addressee_id == user1_id)
            )
        ).first()

    def update_connection_status(self, connection_id: int, status: ConnectionStatus, user_id: int) -> Optional[Connection]:
        """Update connection status (accept/reject/block)"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            return None
        
        # Check if user has permission to update this connection
        if status in [ConnectionStatus.ACCEPTED, ConnectionStatus.REJECTED]:
            if connection.addressee_id != user_id:
                return None
        elif status == ConnectionStatus.BLOCKED:
            if connection.requester_id != user_id and connection.addressee_id != user_id:
                return None
        
        connection.status = status
        connection.updated_at = datetime.utcnow()
        if status in [ConnectionStatus.ACCEPTED, ConnectionStatus.REJECTED]:
            connection.responded_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(connection)
        return connection

    def delete_connection(self, connection_id: int, user_id: int) -> bool:
        """Delete a connection (cancel request or remove connection)"""
        connection = self.get_connection_by_id(connection_id)
        if not connection:
            return False
        
        # Check if user has permission to delete this connection
        if connection.status == ConnectionStatus.PENDING:
            if connection.requester_id != user_id:
                return False
        else:
            if connection.requester_id != user_id and connection.addressee_id != user_id:
                return False
        
        self.db.delete(connection)
        self.db.commit()
        return True

    def remove_connection_between_users(self, user1_id: int, user2_id: int) -> bool:
        """Remove connection between two users"""
        connection = self.get_connection_between_users(user1_id, user2_id)
        if not connection:
            return False
        
        self.db.delete(connection)
        self.db.commit()
        return True

    def get_user_connections(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Connection]:
        """Get all accepted connections for a user"""
        return self.db.query(Connection).options(
            joinedload(Connection.requester),
            joinedload(Connection.addressee)
        ).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        ).offset(offset).limit(limit).all()

    def get_pending_requests_received(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Connection]:
        """Get pending connection requests received by user"""
        return self.db.query(Connection).options(
            joinedload(Connection.requester),
            joinedload(Connection.addressee)
        ).filter(
            and_(
                Connection.addressee_id == user_id,
                Connection.status == ConnectionStatus.PENDING
            )
        ).order_by(desc(Connection.created_at)).offset(offset).limit(limit).all()

    def get_pending_requests_sent(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Connection]:
        """Get pending connection requests sent by user"""
        return self.db.query(Connection).options(
            joinedload(Connection.requester),
            joinedload(Connection.addressee)
        ).filter(
            and_(
                Connection.requester_id == user_id,
                Connection.status == ConnectionStatus.PENDING
            )
        ).order_by(desc(Connection.created_at)).offset(offset).limit(limit).all()

    def get_connection_status(self, user1_id: int, user2_id: int) -> Optional[Connection]:
        """Get connection status between two users"""
        return self.get_connection_between_users(user1_id, user2_id)

    def get_mutual_connections(self, user1_id: int, user2_id: int, limit: int = 20, offset: int = 0) -> List[User]:
        """Get mutual connections between two users"""
        # Get user1's connections
        user1_connections = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user1_id,
                    Connection.addressee_id == user1_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        ).subquery()
        
        # Get user2's connections
        user2_connections = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user2_id,
                    Connection.addressee_id == user2_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        ).subquery()
        
        # Find mutual connections
        mutual_user_ids = self.db.query(
            func.coalesce(
                func.case(
                    (user1_connections.c.requester_id == user1_id, user1_connections.c.addressee_id),
                    else_=user1_connections.c.requester_id
                ),
                func.case(
                    (user2_connections.c.requester_id == user2_id, user2_connections.c.addressee_id),
                    else_=user2_connections.c.requester_id
                )
            )
        ).filter(
            and_(
                func.coalesce(
                    func.case(
                        (user1_connections.c.requester_id == user1_id, user1_connections.c.addressee_id),
                        else_=user1_connections.c.requester_id
                    ),
                    func.case(
                        (user2_connections.c.requester_id == user2_id, user2_connections.c.addressee_id),
                        else_=user2_connections.c.requester_id
                    )
                ).in_(
                    self.db.query(
                        func.case(
                            (user2_connections.c.requester_id == user2_id, user2_connections.c.addressee_id),
                            else_=user2_connections.c.requester_id
                        )
                    )
                )
            )
        ).offset(offset).limit(limit).all()
        
        # Get user objects for mutual connections
        if mutual_user_ids:
            user_ids = [uid[0] for uid in mutual_user_ids]
            return self.db.query(User).filter(User.id.in_(user_ids)).all()
        return []

    def get_connection_suggestions(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Get connection suggestions based on mutual connections, university, major"""
        # Get user's current connections to exclude
        current_connections = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status.in_([ConnectionStatus.ACCEPTED, ConnectionStatus.PENDING, ConnectionStatus.BLOCKED])
            )
        ).all()
        
        connected_user_ids = set()
        for conn in current_connections:
            if conn.requester_id == user_id:
                connected_user_ids.add(conn.addressee_id)
            else:
                connected_user_ids.add(conn.requester_id)
        
        connected_user_ids.add(user_id)  # Exclude self
        
        # Get user's profile for matching
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return []
        
        # Base query for potential connections
        suggestions_query = self.db.query(User).filter(
            and_(
                User.id.notin_(connected_user_ids),
                User.is_active == True
            )
        )
        
        # Add scoring based on common attributes
        suggestions = []
        for potential_user in suggestions_query.offset(offset).limit(limit * 2).all():  # Get more to filter
            score = 0.0
            mutual_count = 0
            common_interests = []
            
            # Check mutual connections
            mutual_connections = self.get_mutual_connections(user_id, potential_user.id, limit=100)
            mutual_count = len(mutual_connections)
            score += mutual_count * 10  # High weight for mutual connections
            
            # Check common university
            if user.university and potential_user.university and user.university.lower() == potential_user.university.lower():
                score += 20
                common_university = True
            else:
                common_university = False
            
            # Check common major
            if user.major and potential_user.major and user.major.lower() == potential_user.major.lower():
                score += 15
                common_major = True
            else:
                common_major = False
            
            # Check common interests
            if user.interests and potential_user.interests:
                user_interests = [i.lower() for i in user.interests]
                potential_interests = [i.lower() for i in potential_user.interests]
                common_interests = [i for i in user_interests if i in potential_interests]
                score += len(common_interests) * 5
            
            # Only include suggestions with some score
            if score > 0:
                suggestions.append({
                    'user': potential_user,
                    'mutual_connections_count': mutual_count,
                    'common_university': common_university,
                    'common_major': common_major,
                    'common_interests': common_interests,
                    'suggestion_score': score
                })
        
        # Sort by score and return top results
        suggestions.sort(key=lambda x: x['suggestion_score'], reverse=True)
        return suggestions[:limit]

    def get_connection_stats(self, user_id: int) -> Dict[str, int]:
        """Get connection statistics for a user"""
        # Total accepted connections
        total_connections = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        ).count()
        
        # Pending requests received
        pending_received = self.db.query(Connection).filter(
            and_(
                Connection.addressee_id == user_id,
                Connection.status == ConnectionStatus.PENDING
            )
        ).count()
        
        # Pending requests sent
        pending_sent = self.db.query(Connection).filter(
            and_(
                Connection.requester_id == user_id,
                Connection.status == ConnectionStatus.PENDING
            )
        ).count()
        
        # Blocked users
        blocked_users = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status == ConnectionStatus.BLOCKED
            )
        ).count()
        
        return {
            'total_connections': total_connections,
            'pending_received': pending_received,
            'pending_sent': pending_sent,
            'blocked_users': blocked_users
        }

    def block_user(self, blocker_id: int, blocked_id: int) -> Optional[Connection]:
        """Block a user"""
        # Check if connection already exists
        existing_connection = self.get_connection_between_users(blocker_id, blocked_id)
        
        if existing_connection:
            # Update existing connection to blocked
            existing_connection.status = ConnectionStatus.BLOCKED
            existing_connection.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(existing_connection)
            return existing_connection
        else:
            # Create new blocked connection
            connection = Connection(
                requester_id=blocker_id,
                addressee_id=blocked_id,
                status=ConnectionStatus.BLOCKED
            )
            self.db.add(connection)
            self.db.commit()
            self.db.refresh(connection)
            return connection

    def unblock_user(self, unblocker_id: int, unblocked_id: int) -> bool:
        """Unblock a user"""
        connection = self.get_connection_between_users(unblocker_id, unblocked_id)
        if not connection or connection.status != ConnectionStatus.BLOCKED:
            return False
        
        self.db.delete(connection)
        self.db.commit()
        return True
