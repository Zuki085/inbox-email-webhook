"""
Firebase Configuration Module

Handles Firebase Admin SDK initialization and provides Firestore client.
Supports both service account key file and environment variable authentication.
"""

import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class FirebaseConfig:
    """Firebase configuration manager"""
    
    _app: Optional[firebase_admin.App] = None
    _db: Optional[firestore.Client] = None
    
    @classmethod
    def initialize_firebase(cls) -> firestore.Client:
        """
        Initialize Firebase Admin SDK and return Firestore client
        
        Returns:
            firestore.Client: Firestore database client
            
        Raises:
            Exception: If Firebase initialization fails
        """
        if cls._app is None:
            try:
                # Check if any Firebase credentials are available
                service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY_PATH")
                project_id = os.getenv("FIREBASE_PROJECT_ID")
                
                if not service_account_path and not project_id:
                    raise Exception(
                        "❌ Firebase configuration not found!\n\n"
                        "Please set up Firebase credentials by choosing one of these options:\n\n"
                        "Option 1 - Service Account Key File (Recommended for Development):\n"
                        "  1. Go to Firebase Console → Project Settings → Service Accounts\n"
                        "  2. Generate new private key and download JSON file\n"
                        "  3. Set FIREBASE_SERVICE_ACCOUNT_KEY_PATH=/path/to/your/service-account-key.json\n\n"
                        "Option 2 - Environment Variables (Recommended for Production):\n"
                        "  1. Set FIREBASE_PROJECT_ID=your-firebase-project-id\n"
                        "  2. Set FIREBASE_PRIVATE_KEY_ID=your-private-key-id\n"
                        "  3. Set FIREBASE_PRIVATE_KEY=\"-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n\"\n"
                        "  4. Set FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com\n"
                        "  5. Set FIREBASE_CLIENT_ID=your-client-id\n"
                        "  6. Set FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/...\n\n"
                        "Create a .env file in your project root with these variables.\n"
                        "See GMAIL_SETUP.md for detailed instructions."
                    )
                
                # Option 1: Using service account key file
                if service_account_path:
                    if not os.path.exists(service_account_path):
                        raise Exception(f"Service account key file not found: {service_account_path}")
                    cred = credentials.Certificate(service_account_path)
                    cls._app = firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase initialized with service account key: {service_account_path}")
                    
                # Option 2: Using environment variables (recommended for production)
                elif project_id:
                    # Check if all required environment variables are present
                    required_vars = [
                        "FIREBASE_PRIVATE_KEY_ID",
                        "FIREBASE_PRIVATE_KEY", 
                        "FIREBASE_CLIENT_EMAIL",
                        "FIREBASE_CLIENT_ID",
                        "FIREBASE_CLIENT_X509_CERT_URL"
                    ]
                    missing_vars = [var for var in required_vars if not os.getenv(var)]
                    
                    if missing_vars:
                        raise Exception(
                            f"Missing required Firebase environment variables: {', '.join(missing_vars)}\n"
                            "Please set all required variables for environment variable authentication."
                        )
                    
                    # Create credentials from environment variables
                    cred_dict = {
                        "type": "service_account",
                        "project_id": project_id,
                        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                        "private_key": os.getenv("FIREBASE_PRIVATE_KEY").replace('\\n', '\n'),
                        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                    }
                    
                    cred = credentials.Certificate(cred_dict)
                    cls._app = firebase_admin.initialize_app(cred)
                    print(f"✅ Firebase initialized with environment variables for project: {project_id}")
                    
            except Exception as e:
                raise Exception(f"Failed to initialize Firebase: {str(e)}")
        
        if cls._db is None:
            cls._db = firestore.client()
            
        return cls._db
    
    @classmethod
    def get_firestore_client(cls) -> firestore.Client:
        """
        Get Firestore client instance
        
        Returns:
            firestore.Client: Firestore database client
        """
        if cls._db is None:
            return cls.initialize_firebase()
        return cls._db
    
    
    @classmethod
    def reset(cls):
        """Reset Firebase configuration (useful for testing)"""
        if cls._app:
            firebase_admin.delete_app(cls._app)
            cls._app = None
            cls._db = None

# Convenience functions
def initialize_firebase() -> firestore.Client:
    """Initialize Firebase and return Firestore client"""
    return FirebaseConfig.initialize_firebase()

def get_firestore_client() -> firestore.Client:
    """Get Firestore client instance"""
    return FirebaseConfig.get_firestore_client()
