from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api import schemas
from api import models


async def create_task(db: AsyncSession, task_create: schemas.TaskCreate) -> models.Task:
    task = models.Task(**task_create.dict())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, task_create: schemas.TaskCreate, task: models.Task) -> models.Task:
    task.title = task_create.title
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task: models.Task) -> None:
    await db.delete(task)
    await db.commit()


async def get_task(db: AsyncSession, task_id: int) -> models.Task | None:
    result = await (
        db.execute(
            select(
                models.Task
            ).filter(models.Task.id == task_id)
        )
    )
    tasks = result.one_or_none()
    if tasks is None:
        return None
    return tasks[0]


async def get_tasks_with_done(db: AsyncSession) -> list[tuple[int, str, bool]]:
    result = await (
        db.execute(
            select(
                models.Task.id,
                models.Task.title,
                models.Done.id.isnot(None).label("done"),
            ).outerjoin(models.Done)
        )
    )
    return result.all()


async def create_done(db: AsyncSession, task_id: int) -> models.Done:
    done = models.Done(id=task_id)
    db.add(done)
    await db.commit()
    await db.refresh(done)
    return done


async def delete_done(db: AsyncSession, done: models.Done) -> None:
    await db.delete(done)
    await db.commit()


async def get_done(db: AsyncSession, task_id: int) -> models.Done | None:
    result = await (
        db.execute(
            select(
                models.Done
            ).filter(models.Done.id == task_id)
        )
    )
    dones = result.one_or_none()
    if dones is None:
        return None
    return dones[0]
