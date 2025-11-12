from sqlalchemy.orm import Session
from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate
from typing import List, Optional


def create_client(db: Session, client_data: ClientCreate, user_id: int) -> Client:
    """Create a new client"""
    client = Client(
        **client_data.model_dump(),
        user_id=user_id
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: int, user_id: int) -> Optional[Client]:
    """Get client by ID"""
    return db.query(Client).filter(
        Client.id == client_id,
        Client.user_id == user_id
    ).first()


def get_clients(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Client]:
    """Get list of clients"""
    return db.query(Client).filter(
        Client.user_id == user_id
    ).order_by(Client.created_at.desc()).offset(skip).limit(limit).all()


def update_client(
    db: Session,
    client_id: int,
    user_id: int,
    client_data: ClientUpdate
) -> Optional[Client]:
    """Update a client"""
    client = get_client(db, client_id, user_id)
    if not client:
        return None

    update_data = client_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)

    db.commit()
    db.refresh(client)
    return client


def delete_client(db: Session, client_id: int, user_id: int) -> bool:
    """Delete a client"""
    client = get_client(db, client_id, user_id)
    if not client:
        return False

    db.delete(client)
    db.commit()
    return True
