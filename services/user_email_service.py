"""
User Email Account Service

Manages per-user email credentials stored in the Firestore users collection.
Each user with email + app_password can have their inbox polled and stored in Firebase.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import logging

from config.firebase_config import get_firestore_client
from services.email_config import EmailConfig

logger = logging.getLogger(__name__)

PASSWORD_FIELDS = ("app_password", "appPassword", "email_password", "emailPassword")


class UserEmailService:
    """Service for managing user email accounts in Firestore"""

    def __init__(self):
        self.db = get_firestore_client()
        self.users_collection = "users"

    def _extract_password(self, user_data: Dict[str, Any]) -> Optional[str]:
        for field in PASSWORD_FIELDS:
            value = user_data.get(field)
            if value and str(value).strip():
                return str(value).strip()
        return None

    def _build_account(self, user_id: str, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        email = user_data.get("email")
        password = self._extract_password(user_data)

        if not email or not password:
            return None

        if user_data.get("email_polling_enabled") is False:
            return None

        imap_config = EmailConfig.get_imap_config_for_email(
            email,
            custom_host=user_data.get("email_host"),
            custom_port=user_data.get("email_port"),
            custom_use_ssl=user_data.get("email_use_ssl"),
        )

        return {
            "user_id": user_id,
            "email": str(email).strip(),
            "password": password,
            "host": imap_config["host"],
            "port": imap_config["port"],
            "use_ssl": imap_config["use_ssl"],
            "first_name": user_data.get(
                "firstName", user_data.get("username", user_data.get("name", ""))
            ),
        }

    async def get_polling_accounts(self) -> List[Dict[str, Any]]:
        """Return all users eligible for IMAP polling."""
        accounts: List[Dict[str, Any]] = []

        try:
            docs = self.db.collection(self.users_collection).stream()
            for doc in docs:
                user_data = doc.to_dict() or {}
                account = self._build_account(doc.id, user_data)
                if account:
                    accounts.append(account)
        except Exception as e:
            logger.error(f"Error loading user email accounts: {e}")

        logger.info(f"Found {len(accounts)} user email account(s) for polling")
        return accounts

    async def get_account_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get polling account config for a specific user."""
        try:
            doc = self.db.collection(self.users_collection).document(user_id).get()
            if not doc.exists:
                return None
            return self._build_account(doc.id, doc.to_dict() or {})
        except Exception as e:
            logger.error(f"Error loading email account for user {user_id}: {e}")
            return None

    async def register_email_account(
        self,
        user_id: str,
        email: str,
        app_password: str,
        email_polling_enabled: bool = True,
        email_host: Optional[str] = None,
        email_port: Optional[int] = None,
        email_use_ssl: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Register or update email credentials on an existing user document.
        Called when a user connects their mailbox during account setup.
        """
        user_ref = self.db.collection(self.users_collection).document(user_id)
        user_doc = user_ref.get()

        if not user_doc.exists:
            raise ValueError(f"User {user_id} not found")

        update_data: Dict[str, Any] = {
            "email": email.strip(),
            "app_password": app_password.strip(),
            "email_polling_enabled": email_polling_enabled,
            "email_account_updated_at": datetime.now(timezone.utc),
        }

        if email_host is not None:
            update_data["email_host"] = email_host
        if email_port is not None:
            update_data["email_port"] = email_port
        if email_use_ssl is not None:
            update_data["email_use_ssl"] = email_use_ssl

        user_ref.update(update_data)

        imap_config = EmailConfig.get_imap_config_for_email(
            email,
            custom_host=email_host,
            custom_port=email_port,
            custom_use_ssl=email_use_ssl,
        )

        return {
            "user_id": user_id,
            "email": email.strip(),
            "email_polling_enabled": email_polling_enabled,
            "imap_config": imap_config,
        }

    async def get_email_account_status(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Return email account status without exposing the password."""
        try:
            doc = self.db.collection(self.users_collection).document(user_id).get()
            if not doc.exists:
                return None

            user_data = doc.to_dict() or {}
            has_password = self._extract_password(user_data) is not None
            email = user_data.get("email")

            return {
                "user_id": user_id,
                "email": email,
                "email_polling_enabled": user_data.get("email_polling_enabled", True),
                "has_credentials": bool(email and has_password),
                "last_polled_at": user_data.get("email_last_polled_at"),
                "last_poll_status": user_data.get("email_last_poll_status"),
                "last_poll_error": user_data.get("email_last_poll_error"),
            }
        except Exception as e:
            logger.error(f"Error getting email account status for user {user_id}: {e}")
            return None

    async def update_poll_status(
        self,
        user_id: str,
        status: str,
        error: Optional[str] = None,
        emails_fetched: int = 0,
    ) -> None:
        """Record the result of the latest poll for a user."""
        try:
            update_data: Dict[str, Any] = {
                "email_last_polled_at": datetime.now(timezone.utc),
                "email_last_poll_status": status,
                "email_last_poll_emails": emails_fetched,
            }
            if error:
                update_data["email_last_poll_error"] = error
            else:
                update_data["email_last_poll_error"] = None

            self.db.collection(self.users_collection).document(user_id).update(update_data)
        except Exception as e:
            logger.error(f"Error updating poll status for user {user_id}: {e}")
