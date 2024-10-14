from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

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

# python main.py
if __name__ == "__main__":
  uvicorn.run('main:app', 
              host='localhost', port=8000, reload=True)
  
# CLI명령: uvicorn main:app --reload