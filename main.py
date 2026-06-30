"""
Email Webhook Main Entry Point

Standalone FastAPI application for the email webhook service.
Can be run independently or integrated with the main application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import asyncio

from routes.webhook import router
from routes.users import router as users_router
from config.firebase_config import initialize_firebase
from services.email_poller import email_poller

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Initialize Firebase on startup
    firebase_initialized = False
    try:
        initialize_firebase()
        firebase_initialized = True
        print("✅ Firebase initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize Firebase: {e}")
        print("⚠️  Application will start without Firebase functionality")
        print("📝 To fix this, please set up Firebase credentials:")
        print("   1. Create a .env file with Firebase configuration")
        print("   2. See GMAIL_SETUP.md for detailed instructions")
    
    # Start email polling in background (only if Firebase is available)
    email_polling_task = None
    if firebase_initialized:
        try:
            if email_poller.poll_enabled:
                email_polling_task = asyncio.create_task(email_poller.start_polling())
                print("✅ Email polling started successfully")
            else:
                print("ℹ️ Email polling is disabled")
        except Exception as e:
            print(f"❌ Failed to start email polling: {e}")
    else:
        print("ℹ️ Email polling disabled due to Firebase initialization failure")
    
    yield
    
    # Cleanup on shutdown
    print("🔄 Shutting down email webhook service...")
    if email_polling_task:
        email_polling_task.cancel()
        try:
            await email_polling_task
        except asyncio.CancelledError:
            pass

def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Email Webhook Service",
        description="A comprehensive email webhook system that receives email data and stores it in Firebase",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure this properly for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include webhook routes
    app.include_router(router)
    app.include_router(users_router)
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Email Webhook Service",
            "version": "1.0.0",
            "status": "running",
            "endpoints": {
                "webhook": "/webhook/email",
                "emails": "/webhook/emails",
                "user_emails": "/webhook/users/{user_id}/emails",
                "register_mailbox": "/webhook/users/{user_id}/email-account",
                "health": "/webhook/health",
                "docs": "/docs"
            }
        }
    
    return app

# Create the app instance
app = create_app()

if __name__ == "__main__":
    uvicorn.run(
        "email-webhook.main:app",
        host="0.0.0.0",
        port=8001,  # Different port from main app
        reload=True,
        log_level="info"
    )
