"""
Settings Configuration for Email Webhook

Environment-based configuration management.
"""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    
    # Firebase Configuration
    FIREBASE_PROJECT_ID: Optional[str] = os.getenv("FIREBASE_PROJECT_ID")
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH: Optional[str] = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
    
    # Firebase Environment Variables (for production)
    FIREBASE_PRIVATE_KEY_ID: Optional[str] = os.getenv("FIREBASE_PRIVATE_KEY_ID")
    FIREBASE_PRIVATE_KEY: Optional[str] = os.getenv("FIREBASE_PRIVATE_KEY")
    FIREBASE_CLIENT_EMAIL: Optional[str] = os.getenv("FIREBASE_CLIENT_EMAIL")
    FIREBASE_CLIENT_ID: Optional[str] = os.getenv("FIREBASE_CLIENT_ID")
    FIREBASE_AUTH_URI: str = os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth")
    FIREBASE_TOKEN_URI: str = os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token")
    FIREBASE_AUTH_PROVIDER_X509_CERT_URL: str = os.getenv(
        "FIREBASE_AUTH_PROVIDER_X509_CERT_URL", 
        "https://www.googleapis.com/oauth2/v1/certs"
    )
    FIREBASE_CLIENT_X509_CERT_URL: Optional[str] = os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
    
    # Application Settings
    APP_NAME: str = "Email Webhook Service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # API Settings
    API_PREFIX: str = "/webhook"
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # File Processing Settings
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))  # 10MB
    ALLOWED_FILE_TYPES: list = os.getenv("ALLOWED_FILE_TYPES", "pdf,jpg,jpeg,png").split(",")
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", "Static")
    
    # Pagination Settings
    DEFAULT_PAGE_SIZE: int = int(os.getenv("DEFAULT_PAGE_SIZE", "10"))
    MAX_PAGE_SIZE: int = int(os.getenv("MAX_PAGE_SIZE", "100"))
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    
    # Security Settings
    JWT_SECRET_KEY: Optional[str] = os.getenv("SECRET_KEY")
    JWT_ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    
    # Email Settings
    INVOICE_EMAIL: Optional[str] = os.getenv("INVOICE_EMAIL")
    INVOICE_PASSWORD: Optional[str] = os.getenv("INVOICE_PASSWORD")
    
    @classmethod
    def validate_firebase_config(cls) -> bool:
        """Validate Firebase configuration"""
        return bool(
            cls.FIREBASE_SERVICE_ACCOUNT_KEY_PATH or 
            (cls.FIREBASE_PROJECT_ID and cls.FIREBASE_PRIVATE_KEY and cls.FIREBASE_CLIENT_EMAIL)
        )
    
    @classmethod
    def get_firebase_credentials(cls) -> dict:
        """Get Firebase credentials for environment variable authentication"""
        if not cls.FIREBASE_PROJECT_ID:
            raise ValueError("FIREBASE_PROJECT_ID is required for environment variable authentication")
        
        return {
            "type": "service_account",
            "project_id": cls.FIREBASE_PROJECT_ID,
            "private_key_id": cls.FIREBASE_PRIVATE_KEY_ID,
            "private_key": cls.FIREBASE_PRIVATE_KEY.replace('\\n', '\n') if cls.FIREBASE_PRIVATE_KEY else None,
            "client_email": cls.FIREBASE_CLIENT_EMAIL,
            "client_id": cls.FIREBASE_CLIENT_ID,
            "auth_uri": cls.FIREBASE_AUTH_URI,
            "token_uri": cls.FIREBASE_TOKEN_URI,
            "auth_provider_x509_cert_url": cls.FIREBASE_AUTH_PROVIDER_X509_CERT_URL,
            "client_x509_cert_url": cls.FIREBASE_CLIENT_X509_CERT_URL
        }

# Global settings instance
settings = Settings()
