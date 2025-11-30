from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from database import init_db
from routers import generate, resume, chat, auth, history
from limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Portfolio Generator V2 API",
    version="2.0.0",
    description="AI-powered portfolio generator with multi-stack support"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with proper prefixes
# Include routers with proper prefixes
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(generate.router, prefix="/api/generate", tags=["generate"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {
        "message": "Portfolio Generator V2 API",
        "version": "2.0.0",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}
