from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.permissions import admin_required
from app.database import get_db
from app.schemas.user_schema import UserListItem, UserDetail, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


@router.get("/", response_model=list[UserListItem], dependencies=[Depends(admin_required)])
def list_users(
        page: int = Query(1, ge=1),
        limit: int = Query(20, ge=1, le=200),
        db: Session = Depends(get_db),
):
    users_list = UserService.list_users(db, page, limit)

    return users_list


@router.get("/{user_id}", response_model=UserDetail, dependencies=[Depends(admin_required)])
def get_user(
        user_id: int,
        db: Session = Depends(get_db),
):
    user = UserService.get_user(db, user_id)

    return user


@router.put("/{user_id}", response_model=UserDetail, dependencies=[Depends(admin_required)])
def update_user(
        user_id: int,
        payload: UserUpdate,
        db: Session = Depends(get_db),
):
    user_update = UserService.update_user(db, user_id, payload.model_dump(exclude_unset=True))

    return user_update


@router.patch("/{user_id}/disable", response_model=UserDetail, dependencies=[Depends(admin_required)])
def disable_user(
        user_id: int,
        db: Session = Depends(get_db),
):
    disabled = UserService.disable_user(db, user_id)

    return disabled


@router.patch("/{user_id}/enable", response_model=UserDetail, dependencies=[Depends(admin_required)])
def enable_user(
        user_id: int,
        db: Session = Depends(get_db),
):

    enabled = UserService.enable_user(db, user_id)

    return enabled

