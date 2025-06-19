from fastapi import FastAPI
from pydantic_settings import BaseSettings

from app.api.v1.router import api_router # Import the v1 api router

class Settings(BaseSettings):
    project_name: str = "Jijenga Referral System"
    
    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(title=settings.project_name)

# Include the v1 API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Jijenga Referral System"}
