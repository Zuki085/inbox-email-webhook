"""
Email Polling Service

Polls email accounts for new emails and stores them in Firebase.
Supports multiple user mailboxes from Firestore, with legacy single-mailbox env fallback.
"""

import imaplib
import email
import asyncio
import os
import base64
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import logging

from models.schemas import EmailDataSchema, EmailAttachmentSchema
from services.firebase_service import FirebaseService
from services.user_email_service import UserEmailService
from config.settings import settings

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)


class EmailPoller:
    """Service for polling email accounts and storing emails in Firebase"""

    def __init__(self):
        self.firebase_service = FirebaseService()
        self.user_email_service = UserEmailService()
        self.poll_interval = int(os.getenv("EMAIL_POLL_INTERVAL", "60"))
        self.poll_enabled = os.getenv("EMAIL_POLL_ENABLED", "true").lower() == "true"

        self.legacy_username = os.getenv("EMAIL_USERNAME")
        self.legacy_password = os.getenv("EMAIL_PASSWORD")
        self.legacy_host = os.getenv("EMAIL_HOST", "imap.gmail.com")
        self.legacy_port = int(os.getenv("EMAIL_PORT", "993"))
        self.legacy_use_ssl = os.getenv("EMAIL_USE_SSL", "true").lower() == "true"

        logger.info(f"Email polling enabled: {self.poll_enabled}")
        logger.info(f"Poll interval: {self.poll_interval} seconds")

    def _get_legacy_account(self) -> Optional[Dict[str, Any]]:
        """Fallback single-mailbox config from environment variables."""
        if not self.legacy_username or not self.legacy_password:
            return None

        return {
            "user_id": "legacy_env",
            "email": str(self.legacy_username).strip(),
            "password": str(self.legacy_password).strip(),
            "host": self.legacy_host,
            "port": self.legacy_port,
            "use_ssl": self.legacy_use_ssl,
            "first_name": "legacy",
        }

    async def _get_accounts_to_poll(self) -> List[Dict[str, Any]]:
        accounts = await self.user_email_service.get_polling_accounts()
        if accounts:
            return accounts

        legacy = self._get_legacy_account()
        if legacy:
            logger.info("No Firestore user accounts found; using legacy EMAIL_USERNAME env config")
            return [legacy]

        logger.warning("No email accounts configured for polling")
        return []

    async def start_polling(self):
        """Start the email polling loop"""
        if not self.poll_enabled:
            logger.info("Email polling is disabled")
            return

        logger.info(f"Starting multi-user email polling every {self.poll_interval} seconds")

        while True:
            try:
                await self.poll_emails()
                await asyncio.sleep(self.poll_interval)
            except Exception as e:
                logger.error(f"Error in email polling loop: {e}")
                await asyncio.sleep(30)

    async def poll_emails(self):
        """Poll all configured user mailboxes for new emails."""
        accounts = await self._get_accounts_to_poll()
        if not accounts:
            return

        for account in accounts:
            try:
                await self.poll_mailbox(account)
            except Exception as e:
                logger.error(f"Error polling mailbox {account['email']}: {e}")
                if account["user_id"] != "legacy_env":
                    await self.user_email_service.update_poll_status(
                        account["user_id"], "error", str(e)
                    )

    async def poll_mailbox(self, account: Dict[str, Any]):
        """Poll a single user's mailbox and store new emails in Firebase."""
        username = account["email"]
        password = account["password"]
        owner_user_id = account["user_id"]
        emails_stored = 0

        logger.info(f"Polling mailbox for {username} (user: {owner_user_id})")

        try:
            if account["use_ssl"]:
                mail = imaplib.IMAP4_SSL(account["host"], account["port"])
            else:
                mail = imaplib.IMAP4(account["host"], account["port"])

            mail.login(username, password)
            mail.select("INBOX")

            status, messages = mail.search(None, "UNSEEN")
            if status != "OK":
                logger.error(f"Failed to search emails for {username}")
                mail.close()
                mail.logout()
                return

            email_ids = messages[0].split()
            logger.info(f"Found {len(email_ids)} new email(s) for {username}")

            for email_id in email_ids:
                try:
                    stored = await self.process_email(
                        mail, email_id, owner_user_id=owner_user_id, mailbox_email=username
                    )
                    if stored:
                        emails_stored += 1
                except Exception as e:
                    logger.error(f"Error processing email {email_id} for {username}: {e}")

            mail.close()
            mail.logout()

            if owner_user_id != "legacy_env":
                await self.user_email_service.update_poll_status(
                    owner_user_id, "success", emails_fetched=emails_stored
                )

        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP error for {username}: {e}")
            if owner_user_id != "legacy_env":
                await self.user_email_service.update_poll_status(
                    owner_user_id, "error", str(e)
                )
            raise

    async def process_email(
        self,
        mail: imaplib.IMAP4_SSL,
        email_id: bytes,
        owner_user_id: Optional[str] = None,
        mailbox_email: Optional[str] = None,
    ) -> bool:
        """Process a single email and store it in Firebase. Returns True if stored."""
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        if status != "OK":
            logger.error(f"Failed to fetch email {email_id}")
            return False

        raw_email = msg_data[0][1]
        email_message = email.message_from_bytes(raw_email)
        email_data = await self.parse_email(
            email_message,
            owner_user_id=owner_user_id,
            mailbox_email=mailbox_email,
        )

        if not email_data:
            return False

        if owner_user_id and owner_user_id != "legacy_env":
            if await self.firebase_service.email_exists(
                email_data.message_id, owner_user_id
            ):
                logger.info(
                    f"Skipping duplicate email {email_data.message_id} for user {owner_user_id}"
                )
                mail.store(email_id, "+FLAGS", "\\Seen")
                return False

        try:
            email_id_str = await self.firebase_service.store_email(email_data)
            logger.info(f"Stored email {email_id_str} for mailbox {mailbox_email}")
            mail.store(email_id, "+FLAGS", "\\Seen")
            return True
        except Exception as e:
            logger.error(f"Error storing email in Firebase: {e}")
            raise

    async def parse_email(
        self,
        email_message,
        owner_user_id: Optional[str] = None,
        mailbox_email: Optional[str] = None,
    ) -> Optional[EmailDataSchema]:
        """Parse email message and extract data"""
        try:
            subject = email_message.get("Subject", "")
            from_email = email_message.get("From", "")
            to_email = email_message.get("To", "") or mailbox_email or ""
            cc_email = email_message.get("Cc", "") or None
            bcc_email = email_message.get("Bcc", "") or None
            message_id = email_message.get("Message-ID", "")
            date_str = email_message.get("Date", "")

            try:
                from email.utils import parsedate_to_datetime
                received_at = parsedate_to_datetime(date_str)
            except Exception:
                received_at = datetime.now(timezone.utc)

            body = ""
            html_body = ""

            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        continue
                    if content_type == "text/plain":
                        body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
                    elif content_type == "text/html":
                        html_body = part.get_payload(decode=True).decode("utf-8", errors="ignore")
            else:
                content_type = email_message.get_content_type()
                if content_type == "text/plain":
                    body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")
                elif content_type == "text/html":
                    html_body = email_message.get_payload(decode=True).decode("utf-8", errors="ignore")

            attachments = []
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_disposition = str(part.get("Content-Disposition"))
                    if "attachment" in content_disposition:
                        try:
                            filename = part.get_filename()
                            if filename:
                                content_type = part.get_content_type()
                                payload = part.get_payload(decode=True)
                                if payload is None:
                                    continue
                                size = len(payload)
                                data = base64.b64encode(payload).decode("utf-8")
                                attachments.append(
                                    EmailAttachmentSchema(
                                        filename=filename,
                                        content_type=content_type,
                                        size=size,
                                        data=data,
                                    )
                                )
                        except Exception as e:
                            logger.error(f"Error processing attachment: {e}")

            return EmailDataSchema(
                subject=subject,
                from_email=from_email,
                to_email=to_email,
                cc_email=cc_email,
                bcc_email=bcc_email,
                body=body,
                html_body=html_body if html_body else None,
                attachments=attachments if attachments else None,
                received_at=received_at,
                message_id=message_id,
                user_token=None,
                owner_user_id=owner_user_id if owner_user_id != "legacy_env" else None,
                mailbox_email=mailbox_email,
            )

        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            return None

    async def get_active_account_count(self) -> int:
        accounts = await self._get_accounts_to_poll()
        return len(accounts)


email_poller = EmailPoller()
