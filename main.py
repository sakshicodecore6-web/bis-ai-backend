# main.py
from dotenv import load_dotenv
load_dotenv()
from routers import auth_routes, planner_routes, lab_routes, impact_routes, newsletter_routes, audit_routes, copilot_routes, product_routes

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import create_db_and_tables


app = FastAPI(title="BIS-AI Backend")
app.include_router(auth_routes.router)
app.include_router(planner_routes.router)
app.include_router(lab_routes.router)
app.include_router(impact_routes.router)
app.include_router(newsletter_routes.router)
app.include_router(audit_routes.router)
app.include_router(copilot_routes.router)
app.include_router(product_routes.router)

origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:5175",
    "https://bis-ai-frontend.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.get("/health")
def health_check():
    return {"status": "ok"}


