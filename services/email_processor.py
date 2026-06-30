"""
Email Processing Service

Handles email processing logic including PDF attachment processing
and integration with existing global_functions.py logic.
"""

import os
import base64
from io import BytesIO
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from firebase_admin import firestore

from models.schemas import EmailDataSchema, EmailAttachmentSchema
from config.firebase_config import get_firestore_client

class EmailProcessor:
    """Service for processing email data and attachments"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    async def process_email_with_user_token(
        self, 
        email_data: EmailDataSchema, 
        email_id: str
    ) -> Dict[str, Any]:
        """
        Process email with user token similar to global_functions.py logic
        
        Args:
            email_data: Email data to process
            email_id: Firebase document ID
            
        Returns:
            Dict containing processing results
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from global_functions import get_user_from_token
            from database import get_db
            
            # Get database session
            db_session = next(get_db())
            
            # Get user from token
            user = get_user_from_token(email_data.user_token, db_session)
            
            if user is None:
                # Update Firebase document to mark as unprocessed
                self.db.collection('emails').document(email_id).update({
                    'processed': False,
                    'error': 'Invalid user token',
                    'updated_at': datetime.now(timezone.utc)
                })
                return {
                    'success': False,
                    'error': 'Invalid user token',
                    'user_id': None
                }
            
            # Process attachments if any
            attachment_results = []
            if email_data.attachments:
                for attachment in email_data.attachments:
                    if attachment.filename.endswith('.pdf'):
                        result = await self.process_pdf_attachment(
                            attachment, user.id, email_id
                        )
                        attachment_results.append(result)
            
            # Mark as processed
            self.db.collection('emails').document(email_id).update({
                'processed': True,
                'user_id': user.id,
                'processed_at': datetime.now(timezone.utc),
                'attachment_results': attachment_results,
                'updated_at': datetime.now(timezone.utc)
            })
            
            return {
                'success': True,
                'user_id': user.id,
                'attachment_results': attachment_results
            }
            
        except Exception as e:
            # Update Firebase document with error
            self.db.collection('emails').document(email_id).update({
                'processed': False,
                'error': str(e),
                'updated_at': datetime.now(timezone.utc)
            })
            return {
                'success': False,
                'error': str(e),
                'user_id': None
            }
    
    async def process_pdf_attachment(
        self, 
        attachment: EmailAttachmentSchema, 
        user_id: int, 
        email_id: str
    ) -> Dict[str, Any]:
        """
        Process PDF attachment similar to global_functions.py
        
        Args:
            attachment: PDF attachment data
            user_id: User ID
            email_id: Email document ID
            
        Returns:
            Dict containing processing results
        """
        try:
            # Import here to avoid circular imports
            import sys
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
            from Routers.UploadFile.crud import extract_data_from_pdf, extract_data_from_file
            from database import get_db
            
            # Decode base64 data
            pdf_data = base64.b64decode(attachment.data)
            file_contents = BytesIO(pdf_data)
            
            # Extract data from PDF
            extracted_data = extract_data_from_pdf(Data=file_contents)
            
            if extracted_data == "":
                return {
                    'success': False,
                    'error': 'No data extracted from PDF',
                    'filename': attachment.filename
                }
            
            # Save file locally (similar to global_functions.py)
            file_dir = f"Static/{user_id}/Files"
            if not os.path.exists(file_dir):
                os.makedirs(file_dir)
            
            filepath = f"{file_dir}/{attachment.filename}"
            with open(filepath, 'wb') as f:
                f.write(pdf_data)
            
            # Process the extracted data
            db_session = next(get_db())
            result = extract_data_from_file(
                extractedData=extracted_data,
                file_path=filepath,
                user_id=user_id,
                filename=attachment.filename,
                db=db_session
            )
            
            # Update Firebase with processing result
            self.db.collection('emails').document(email_id).update({
                'pdf_processed': True,
                'extracted_data': extracted_data,
                'file_path': filepath,
                'updated_at': datetime.now(timezone.utc)
            })
            
            return {
                'success': True,
                'filename': attachment.filename,
                'extracted_data': extracted_data,
                'file_path': filepath,
                'result': result
            }
            
        except Exception as e:
            error_msg = f"Error processing PDF attachment: {str(e)}"
            print(error_msg)
            
            # Update Firebase with error
            self.db.collection('emails').document(email_id).update({
                'pdf_processed': False,
                'pdf_error': str(e),
                'updated_at': datetime.now(timezone.utc)
            })
            
            return {
                'success': False,
                'error': str(e),
                'filename': attachment.filename
            }
    
    async def get_processing_status(self, email_id: str) -> Dict[str, Any]:
        """
        Get processing status for an email
        
        Args:
            email_id: Firebase document ID
            
        Returns:
            Dict containing processing status
        """
        try:
            doc = self.db.collection('emails').document(email_id).get()
            
            if not doc.exists:
                return {
                    'success': False,
                    'error': 'Email not found'
                }
            
            data = doc.to_dict()
            return {
                'success': True,
                'email_id': email_id,
                'processed': data.get('processed', False),
                'processed_at': data.get('processed_at'),
                'user_id': data.get('user_id'),
                'error': data.get('error'),
                'pdf_processed': data.get('pdf_processed'),
                'extracted_data': data.get('extracted_data'),
                'file_path': data.get('file_path')
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
