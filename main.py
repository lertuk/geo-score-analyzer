from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re

app = FastAPI()

# Дозволяємо фронтенду стукати на цей API (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

class TextPayload(BaseModel):
    text: str

@app.post("/api/analyze")
def analyze_text(payload: TextPayload):
    text = payload.text
    
    # 1. Рахуємо абзаци (ділимо по будь-яких переносах і відкидаємо порожні)
    paragraphs = len([p for p in re.split(r'\n+', text) if p.strip()])
    
    # 2. Рахуємо цифри та числа (спрощений пошук будь-яких цифр)
    numbers = len(re.findall(r'\d+', text))
    
    # 3. Рахуємо елементи списків (дефіс, зірочка або цифра з крапкою будь-де в тексті)
    list_items = len(re.findall(r'[-*•]\s|\d+\.\s', text))
    
    # 4. Шукаємо Markdown-заголовки (дві або три решітки з пробілом)
    headers = len(re.findall(r'#{2,3}\s', text))
    
    # 5. Шукаємо посилання (просто перевіряємо наявність http)
    links = len(re.findall(r'http[s]?://', text))
    
    # Нова система балів (макс 100, по 20 балів за кожен критерій)
    score = 0
    if paragraphs >= 3: 
        score += 20
    if numbers >= 3: 
        score += 20
    if list_items >= 1: 
        score += 20
    if headers >= 1: 
        score += 20
    if links >= 1: 
        score += 20

    score = min(score, 100) # Максимум 100 балів
    
    # Формуємо динамічну рекомендацію
    recommendation = (
        "Текст ідеально оптимізований для ШІ!" 
        if score == 100 
        else "Додайте більше маркованих списків, підзаголовків (##) та хоча б одне посилання на джерело."
    )

    return {
        "score": score,
        "stats": {
            "paragraphs": paragraphs,
            "numbers": numbers,
            "list_items": list_items,
            "headers": headers,
            "links": links
        },
        "recommendation": recommendation
    }