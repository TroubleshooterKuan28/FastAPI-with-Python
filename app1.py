from typing import Optional
from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel
from dataclasses import dataclass

app = FastAPI()

@dataclass
class Homework:
    title: str
    body: str
    pinned_group: str
    header_url: Optional[str] = None

FAKE_DATABASE = {
    "Python-101": Homework(
        title="Основы ООП",
        body="Реализовать класс и создать несколько экземпляров",
        pinned_group="Python-101",
        header_url="https://w7.pngwing.com/pngs/823/157/png-transparent-round-blue-and-red-illustration-header-page-footer-header-background-frame-blue-computer-network-thumbnail.png"
    ),
    "Web-Dev": Homework(
        title="Верстка сайта",
        body="Сверстать адаптивную шапку сайта на Flexbox",
        pinned_group="Web-Dev",
        header_url=None
    )
}

VALID_API_KEY = "mykeysecretAPI_key_20102807"

class HomeworkRequest(BaseModel):
    group: str

@app.post("/api/get_homework")
def get_homework(
    payload: HomeworkRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
):
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Отсутствует API-ключ в заголовке запроса (X-API-Key)"
        )
    if x_api_key != VALID_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный API-ключ"
        )
    
    requested_group = payload.group
    if requested_group not in FAKE_DATABASE:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Группа с названием '{requested_group}' не найдена в базе данных"
        )

    homework = FAKE_DATABASE[requested_group]

    return {
        "status": "success",
        "data": {
            "title": homework.title,
            "body": homework.body,
            "pinned_group": homework.pinned_group,
            "header_url": homework.header_url
        }
    }