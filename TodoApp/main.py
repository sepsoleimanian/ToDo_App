from typing import Annotated
from fastapi import FastAPI, Depends, Path, HTTPException, status
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from models import todos
from pydantic   import BaseModel, Field
app = FastAPI()
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency =  Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=300)
    priority: int = Field(gt=0, lt=6)
    complete: bool

@app.get("/")
async def read_all(db: db_dependency):
    return db.query(todos).all()

@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(todos).filter(todos.id == todo_id).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail = 'ToDo Note Found')

@app.post("/todo", status_code = status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()

@app.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_to(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(todos).filter(todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail = 'Todo Not Found')
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.complete = todo_request.complete

    db.add(todo_model)
    db.commit()

@app.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(todos).filter(todos.id == todo_id).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail = 'Todo Not Found')
    db.query(todos).filter(todos.id == todo_id).delete()
    db.commit()