from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.database.database import get_db

from app.schemas.client import (
    ClientCreate,
    ClientResponse
)

from app.crud import client as crud
from fastapi import HTTPException
from app.schemas.client import ClientUpdate



router = APIRouter(
    prefix="/clients",
    tags=["Clients"]
)


@router.post(
    "/",
    response_model=ClientResponse
)
def create_client(
    client: ClientCreate,
    db: Session = Depends(get_db)
):
    return crud.create_client(
        db,
        client
    )


@router.get(
    "/",
    response_model=List[ClientResponse]
)
def get_clients(
    db: Session = Depends(get_db)
):
    return crud.get_clients(db)

@router.get(
    "/{client_id}",
    response_model=ClientResponse
)
def get_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = crud.get_client(
        db,
        client_id
    )

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    return client


@router.put(
    "/{client_id}",
    response_model=ClientResponse
)
def update_client(
    client_id: int,
    client_update: ClientUpdate,
    db: Session = Depends(get_db)
):
    client = crud.update_client(
        db,
        client_id,
        client_update
    )

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    return client


@router.delete(
    "/{client_id}"
)
def delete_client(
    client_id: int,
    db: Session = Depends(get_db)
):
    client = crud.delete_client(
        db,
        client_id
    )

    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    return {
        "message": "Client deleted successfully"
    }