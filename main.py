from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from database import (
    create_task,
    delete_task,
    initialize_database,
    list_tasks,
    update_task_completed,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(title="Taskflow", lifespan=lifespan)
STATIC_DIRECTORY = Path(__file__).resolve().parent / "static"


class TaskCreate(BaseModel):
    title: str = Field(max_length=120)


class TaskCompletionUpdate(BaseModel):
    completed: bool


class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool
    created_at: str


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task_endpoint(task: TaskCreate) -> dict:
    return create_task(task.title)


@app.get("/tasks", response_model=list[TaskResponse])
def list_tasks_endpoint() -> list[dict]:
    return list_tasks()


@app.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task_endpoint(task_id: int, update: TaskCompletionUpdate) -> dict:
    task = update_task_completed(task_id, update.completed)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_endpoint(task_id: int) -> None:
    if not delete_task(task_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")


@app.get("/", include_in_schema=False)
def home() -> FileResponse:
    return FileResponse(STATIC_DIRECTORY / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIRECTORY), name="static")
