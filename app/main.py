from fastapi import FastAPI
from .database import engine, Base
from .routers import auth


app = FastAPI()

# Create the tables
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)

@app.get("/")
def root():
    return {"message": "Auth API is running"}