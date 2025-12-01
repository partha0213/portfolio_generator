from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from dotenv import load_dotenv

# Load environment variables FIRST before importing other modules
load_dotenv()

from database import init_db
from routers import resume, chat, auth, history, lovable_generate, assets
from limiter import limiter
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

app = FastAPI(
    title="Portfolio Generator V2 API",
    version="2.0.0",
    description="AI-powered portfolio generator with Lovable-style LLM generation",
    swagger_ui_parameters={"persistAuthorization": True},
    redirect_slashes=False #Keep auth between refreshes
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
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(history.router, prefix="/api/history", tags=["history"])
app.include_router(lovable_generate.router, tags=["lovable-generation"])
app.include_router(resume.router, prefix="/api/resume", tags=["resume"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(assets.router, tags=["assets"])

# ✅ FIXED: Custom OpenAPI schema with Bearer token
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Portfolio Generator V2 API",
        version="2.0.0",
        description="AI-powered portfolio generator with multi-stack support",
        routes=app.routes,
    )
    
    # Define security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter JWT token (without 'Bearer' prefix)"
        }
    }
    
    # ✅ CRITICAL FIX: Apply security to all protected endpoints
    for path, path_item in openapi_schema["paths"].items():
        # Skip auth endpoints (login, signup, etc.)
        if "/auth/" in path:
            continue
        
        # Apply Bearer security to all other endpoints
        for method in path_item:
            if method in ["get", "post", "put", "delete", "patch"]:
                if "security" not in openapi_schema["paths"][path][method]:
                    openapi_schema["paths"][path][method]["security"] = [{"Bearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

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
