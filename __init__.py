"""
Email Webhook Package

A comprehensive email webhook system that receives email data and stores it in Firebase.
Integrates with existing invoice processing logic from global_functions.py.
"""

from routes.webhook import router
from config.firebase_config import initialize_firebase

__version__ = "1.0.0"
__author__ = "NIBLOX Team"

__all__ = ["router", "initialize_firebase"]
