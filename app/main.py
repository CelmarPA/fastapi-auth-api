from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from .core.rate_limit import limiter
from .core.config import settings
from .database import engine, Base
from .routers import auth, admin

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
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Auth API is running"}
