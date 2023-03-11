from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from api import database
from api import schemas
from api import repositories as repos


router = APIRouter()


@router.get("/tasks", response_model=list[schemas.Task])
async def list_tasks(db: AsyncSession = Depends(database.get)):
    return await repos.get_tasks_with_done(db)


@router.post("/tasks", response_model=schemas.TaskCreateResponse)
async def create_task(task_body: schemas.TaskCreate, db: AsyncSession = Depends(database.get)):
    return await repos.create_task(db, task_body)


@router.put("/tasks/{task_id}", response_model=schemas.TaskCreateResponse)
async def update_task(task_id: int, task_body: schemas.TaskCreate, db: AsyncSession = Depends(database.get)):
    task = await repos.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task is not found.")
    return await repos.update_task(db, task_body, task)


@router.delete("/tasks/{task_id}", response_model=None)
async def delete_task(task_id: int, db: AsyncSession = Depends(database.get)):
    task = await repos.get_task(db, task_id=task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task is not found.")
    return await repos.delete_task(db, task)


@router.put("/tasks/{task_id}/done", response_model=schemas.DoneResponse)
async def mark_task_as_done(task_id: int, db: AsyncSession = Depends(database.get)):
    done = await repos.get_done(db, task_id)
    if done is not None:
        raise HTTPException(status_code=400, detail="Done already exists.")
    return await repos.create_done(db, task_id)


@router.delete("/tasks/{task_id}/done", response_model=None)
async def unmark_task_as_done(task_id: int, db: AsyncSession = Depends(database.get)):
    done = await repos.get_done(db, task_id)
    if done is None:
        raise HTTPException(status_code=404, detail="Done is not found.")
    return await repos.delete_done(db, done)
