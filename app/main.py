from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database import engine, Base
from app.routes import collect, output, predict
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
app.include_router(output.router)
app.include_router(predict.router)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "WiFi Fingerprinting API"}
