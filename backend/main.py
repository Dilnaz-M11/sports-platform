from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Sports Analytics Platform API",
    description="API для анализа эффективности спортивных тренировок",
    version="1.0.0"
)

# ✅ ПРАВИЛЬНАЯ НАСТРОЙКА CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://sports-platform-q1ix.vercel.app",  # Ваш домен на Vercel
        "http://localhost:5173",                    # Для локальной разработки
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Платформа анализа спортивных тренировок работает"}

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Импорт маршрутов
from api import api_router
app.include_router(api_router, prefix="/api")