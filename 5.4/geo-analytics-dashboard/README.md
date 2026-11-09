# ІАС Геопросторового Моніторингу ЗСУ (Демо)

Повнофункціональний вебдашборд на стеку PostgreSQL/PostGIS -> Python 3.12 -> FastAPI -> React + TypeScript + Leaflet + milsymbol.

## Запуск системи
1. cd geo-analytics-dashboard
2. docker compose up --build

## Порти
- Frontend Web-Dashboard: http://localhost:5173
- FastAPI Backend: http://localhost:8000/api/v1/health
- Swagger UI (/docs): http://localhost:8000/docs
- PostgreSQL/PostGIS: localhost:5432
