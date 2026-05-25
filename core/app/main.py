from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, analyze, history, analytics, sentences

app = FastAPI(
    title="Vi-Sense API",
    description="Vietnamese Sentiment Analysis API",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(analyze.router, prefix="/analyze", tags=["Analysis"])
app.include_router(history.router, prefix="/history", tags=["History"])
app.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
app.include_router(sentences.router, prefix="/sentences", tags=["Sentences"])

@app.get("/")
async def root():
    return {"message": "Welcome to Vi-Sense API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}