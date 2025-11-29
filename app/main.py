# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.rate_limit import limiter
from app.database import engine, Base
from app.routers import auth, admin_users, products

app = FastAPI()

# attach limiter to app
app.state.limiter = limiter

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware of SlowAPI
app.add_middleware(SlowAPIMiddleware)

# DB
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(admin_users.router)
app.include_router(products.router)

@app.get("/")
def root():
    return {"message": "Auth API is running"}
