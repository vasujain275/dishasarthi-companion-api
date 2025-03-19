from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routes import collect  # Add collect
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="DishaSarthi Companion API", lifespan=lifespan)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(collect.router)  # Add collect router


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "WiFi Fingerprinting API"}
