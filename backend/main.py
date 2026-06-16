from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Создаем приложение
app = FastAPI(
    title="Платформа анализа спортивных тренировок",
    description="API для автоматического построения персональных тренировочных планов",
    version="1.0.0"
)

# Настройка CORS (для доступа с фронтенда)
# Временно разрешаем все источники для тестирования
# При деплое заменить "*" на конкретный домен, например "https://sports-platform.vercel.app"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Временно, для теста. Позже замените на домен Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем все роутеры
from api import api_router
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Платформа анализа спортивных тренировок работает"}

@app.get("/health")
def health_check():
    return {"status": "ok"}