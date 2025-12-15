from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, func
from sqlalchemy.orm import Session

from .database import get_db
from .models import Resident
from .schemas import ResidentCreate, ResidentUpdate, ResidentOut, ResidentListResponse
from .routers_auth import get_current_admin

router = APIRouter(prefix="/api/residents", tags=["Residents"])


def _paginate(query, page: int, page_size: int):
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return total, items


# PUBLIC_INTERFACE
@router.get(
    "",
    response_model=ResidentListResponse,
    summary="List residents",
    description="Returns a paginated list of residents. Supports optional case-insensitive search across name, email, phone, and address.",
)
def list_residents(
    db: Session = Depends(get_db),
    q: Optional[str] = Query(None, description="Search query for name, email, phone, or address"),
    page: int = Query(1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
):
    query = db.query(Resident)
    if q:
        pattern = f"%{q.lower()}%"
        query = query.filter(
            or_(
                func.lower(Resident.first_name).like(pattern),
                func.lower(Resident.last_name).like(pattern),
                func.lower(Resident.email).like(pattern),
                func.lower(Resident.phone).like(pattern),
                func.lower(Resident.address).like(pattern),
            )
        )
    query = query.order_by(Resident.last_name.asc(), Resident.first_name.asc(), Resident.id.asc())
    total, items = _paginate(query, page, page_size)
    data = [ResidentOut.model_validate(item) for item in items]
    return {
        "data": data,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "items": len(data),
        },
    }


# PUBLIC_INTERFACE
@router.post(
    "",
    response_model=ResidentOut,
    status_code=201,
    summary="Create resident",
    description="Create a new resident. Requires authentication.",
)
def create_resident(payload: ResidentCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    resident = Resident(**payload.model_dump())
    db.add(resident)
    db.commit()
    db.refresh(resident)
    return ResidentOut.model_validate(resident)


# PUBLIC_INTERFACE
@router.get(
    "/{resident_id}",
    response_model=ResidentOut,
    summary="Get resident by ID",
    description="Retrieve a resident by their unique identifier.",
)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    return ResidentOut.model_validate(resident)


# PUBLIC_INTERFACE
@router.put(
    "/{resident_id}",
    response_model=ResidentOut,
    summary="Update resident",
    description="Update an existing resident with full payload. Requires authentication.",
)
def update_resident(
    resident_id: int, payload: ResidentCreate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)
):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    for k, v in payload.model_dump().items():
        setattr(resident, k, v)
    db.commit()
    db.refresh(resident)
    return ResidentOut.model_validate(resident)


# PUBLIC_INTERFACE
@router.patch(
    "/{resident_id}",
    response_model=ResidentOut,
    summary="Partially update resident",
    description="Partially update resident fields. Requires authentication.",
)
def patch_resident(
    resident_id: int, payload: ResidentUpdate, db: Session = Depends(get_db), _admin=Depends(get_current_admin)
):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    for k, v in payload.model_dump(exclude_unset=True).items():
        setattr(resident, k, v)
    db.commit()
    db.refresh(resident)
    return ResidentOut.model_validate(resident)


# PUBLIC_INTERFACE
@router.delete(
    "/{resident_id}",
    status_code=204,
    summary="Delete resident",
    description="Delete a resident by ID. Requires authentication.",
)
def delete_resident(resident_id: int, db: Session = Depends(get_db), _admin=Depends(get_current_admin)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resident not found")
    db.delete(resident)
    db.commit()
    return None
