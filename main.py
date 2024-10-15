from fastapi import FastAPI, Request, Depends, Form, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import engine, SessionLocal 
from sqlalchemy.orm import Session
import models

import os
import uvicorn

# FastAPI() 객체 생성
app = FastAPI()

# models에 정의한 모든 클래스, 연결한 DB엔진에 테이블로 생성
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

abs_path = os.path.dirname(os.path.realpath(__file__))
# print(abs_path)

# html 템플릿 폴더를 지정하여 jinja템플릿 객체 생성
#templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# localhost:8000/
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # 테이블 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.desc())
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos})

@app.post("/add")
async def add(request: Request, task: str = Form(...), db: Session = Depends(get_db)):
   # 클라이언트가 textarea에 입력 데이터 넣으면
   print(task)
   # 클라이언트에서 넘어온 task를 Todo 객체로 생성
   todo = models.Todo(task=task)
   # 의존성 주입에서 처리함 Depends(get_db) : 엔진객체생성, 세션연결
   # db 테이블에 task 저장하기
   db.add(todo)
   # db에 실제 저장, commit
   db.commit()

   return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/edit/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "todo": todo})

@app.post("/edit/{todo_id}")
async def add(request: Request, todo_id: int, task: str = Form(...), completed: bool = Form(False), db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    todo.task = task
    todo.completed = completed
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# python main.py
if __name__ == "__main__":
  uvicorn.run('main:app', 
              host='localhost', port=8000, reload=True)

# CLI명령: uvicorn main:app --reload