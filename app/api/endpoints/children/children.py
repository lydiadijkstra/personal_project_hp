# fastapi
from alembic.command import current
from fastapi import APIRouter, Depends, HTTPException

# sqlalchemy
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import current_user

# import
from app.core.dependencies import get_db, oauth2_scheme
from app.schemas.children import Child, ChildCreate, ChildUpdate
from app.models.children import Child as ChildModel
from app.api.endpoints.children import functions as child_functions
from app.api.endpoints.user.functions import get_current_user
from app.api.endpoints.children.functions import (create_new_child, read_all_children, update_child, delete_child)
from app.schemas.user import User


child_module = APIRouter()


# @user_module.get('/')
# async def read_auth_page():
#     return {"msg": "Auth page Initialization done"}


@child_module.post('/', response_model=Child)
async def create_new_child(
    child: ChildCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if a child with the same name exists
    db_child = db.query(ChildModel).filter_by(name=child.name, user_id=current_user.user_id).first()
    if db_child:
        raise HTTPException(status_code=400, detail="Child with this name already exists.")

    # Create the new child record
    new_child = ChildModel(
        name=child.name,
        difficulty=child.difficulty,
        birth_date=child.birth_date,
        user_id=current_user.user_id,
    )
    # new_child = child_functions.create_new_child(db, child, current_user)
    # call the code in functions or delete.

    db.add(new_child)
    db.commit()
    db.refresh(new_child)
    return new_child


"""
>>> This is the buggy create child function, after creating the new one above, the docs are working. <<<

# create new child
@child_module.post('/', response_model=Child)
async def create_new_child(child: ChildCreate, db: Session = Depends(get_db), current_user=Depends(current_user),):
    db_child = child_functions.get_child_by_name(db, child.name, current_user)
    if db_child:
        raise HTTPException(status_code=400, detail="User already exists")
    new_child = child_functions.create_new_child(db, child, current_user)
    return new_child
"""

# get all children
@child_module.get('/', response_model=list[Child])
async def read_all_children(skip: int = 0, limit: int = 100,  db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return child_functions.read_all_children(db, current_user, skip, limit)


# get child by id
@child_module.get('/{child_id}', response_model=Child,
            # dependencies=[Depends(RoleChecker(['admin']))]
            )
async def read_child_by_id(child_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return child_functions.get_child_by_id(db, child_id, current_user)


# update user
@child_module.patch('/{child_id}', response_model=Child,
            #   dependencies=[Depends(RoleChecker(['admin']))]
              )
async def update_child(child_id: int, child: ChildUpdate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    print(f"Received data: {child.model_dump()}")
    return child_functions.update_child(db, child_id, child, current_user)


# delete user
@child_module.delete('/{child_id}',
            #    response_model=Child,
            #    dependencies=[Depends(RoleChecker(['admin']))]
               )
async def delete_child( child_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return child_functions.delete_child(db, child_id, current_user)
