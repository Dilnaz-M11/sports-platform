from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Sports Analytics Platform API",
    description="API для анализа эффективности спортивных тренировок",
    version="1.0.0"
)

# Правильная настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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