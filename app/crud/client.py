from sqlalchemy.orm import Session

from app.models.client import Client
from app.schemas.client import ClientCreate, ClientUpdate


def create_client(
    db: Session,
    client: ClientCreate
):
    db_client = Client(**client.model_dump())

    db.add(db_client)
    db.commit()
    db.refresh(db_client)

    return db_client


def get_clients(db: Session):
    return db.query(Client).all()


def get_client(
    db: Session,
    client_id: int
):
    return (
        db.query(Client)
        .filter(Client.id == client_id)
        .first()
    )


def update_client(
    db: Session,
    client_id: int,
    client_update: ClientUpdate
):
    client = get_client(db, client_id)

    if not client:
        return None

    update_data = client_update.model_dump(
        exclude_unset=True
    )

    for key, value in update_data.items():
        setattr(client, key, value)

    db.commit()
    db.refresh(client)

    return client


def delete_client(
    db: Session,
    client_id: int
):
    client = get_client(db, client_id)

    if not client:
        return None

    db.delete(client)
    db.commit()

    return client