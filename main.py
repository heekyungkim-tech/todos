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

# DB 엔진 연결
# -> models.py에 정의한 클래스를 통해 db에 테이블 생성
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

# html 문서를 위한 jinja템플릿 객체 생성
#templates = Jinja2Templates(directory="templates")
templates = Jinja2Templates(directory=f"{abs_path}/templates")

# static 폴더(정적파일 폴더)를 app에 연결
## 정적파일(static) 종류(image, css, js)
# app.mount("/static", StaticFiles(directory=f"static"), name="static")
app.mount("/static", StaticFiles(directory=f"{abs_path}/static"), name="static")

# localhost:8000/
@app.get("/")
async def home(request: Request, db: Session = Depends(get_db)):
    # db 객체 생성, 세션연결하기 <- 의존성 주임으로 처리
    # 테이블 조회
    todos = db.query(models.Todo).order_by(models.Todo.id.desc())

    # db 조회한 결과를 출력함
    # for todo in todos:
    #     print(todo.id, todo.task, todo.completed)

    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": todos})

@app.post("/add")
async def add(request: Request, task: str = Form(...), db: Session = Depends(get_db)):
   # 클라이언트가 textarea에 입력 데이터 넘어온ㄴ것 확인
   print(task)
   # 클라이언트에서 넘어온 task를 Todo 객체로 생성
   todo = models.Todo(task=task)
   # 의존성 주입에서 처리함 Depends(get_db) : 엔진객체생성, 세션연결
   # db 테이블에 task 저장하기
   db.add(todo)
   # db에 실제 저장, commit
   db.commit()
   # home 엔드포인함수로 제어권을 넘김
   return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

@app.get("/delete/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    db.delete(todo)
    db.commit()
    return RedirectResponse(url=app.url_path_for("home"), status_code=status.HTTP_303_SEE_OTHER)

# todo 수정을 위한 조회
@app.get("/edit/{todo_id}")
async def add(request: Request, todo_id: int, db: Session = Depends(get_db)):
    todo = db.query(models.Todo).filter(models.Todo.id == todo_id).first()
    return templates.TemplateResponse("edit.html", {"request": request, "todo": todo})

# todo 업데이트처리
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