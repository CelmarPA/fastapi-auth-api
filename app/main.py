from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from .models import LoginAttempt
from .core.rate_limit import limiter
from .core.config import settings
from .database import engine, Base
from .routers import auth


app = FastAPI()

# attach limiter to app
app.state.limiter = limiter
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# optional: custom handler for rate limit exceeded
@app.exception_handler(RateLimitExceeded)
def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests, try again later."}
    )



# Origins allowed — adjustments for your frontends (production + development)
origins = [
    "http://localhost:3000",     # exemplo React dev
    "http://127.0.0.1:3000",
    # "https://your-production-domain.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins= origins,     # do not leave ["*"] in production
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"]

)

# Create the tables
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Auth API is running"}