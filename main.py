from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from database import engine, SessionLocal 
from sqlalchemy.orm import Session
import models

import os
import uvicorn

# FastAPI() 객체 생성
app = FastAPI()

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
async def home(request: Request):
    data = 100
    data2 = "fast api"
    return templates.TemplateResponse("index.html",
                                      {"request": request,
                                       "todos": data, "data2":data2})

@app.post("/add")
async def add():
   # 클라이언트가 textarea에 입력 데이터 넣으면
   # DB 테이블에 저장하고 결과를 html에 렌더링해서 리턴
   print("데이터 넘어옴")
   pass

# python main.py
if __name__ == "__main__":
  uvicorn.run('main:app', 
              host='localhost', port=8000, reload=True)

# models에 정의한 모든 클래스, 연결한 DB엔진에 테이블로 생성
models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        # 마지막에 무조건 닫음
        db.close()

# CLI명령: uvicorn main:app --reload