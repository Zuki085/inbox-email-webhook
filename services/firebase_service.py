"""
Firebase Service

Handles all Firebase Firestore operations for email data.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from firebase_admin import firestore
from firebase_admin.firestore import Query
import logging

from config.firebase_config import get_firestore_client
from models.schemas import EmailDataSchema, EmailFilterSchema
from services.user_project_service import UserProjectService

logger = logging.getLogger(__name__)

class FirebaseService:
    """Service for Firebase Firestore operations"""
    
    def __init__(self):
        self.db = get_firestore_client()
        self.collection_name = 'emails'
        self.user_project_service = UserProjectService()
    
    async def email_exists(self, message_id: str, owner_user_id: str) -> bool:
        """Check if an email was already stored for this user and message ID."""
        if not message_id or not owner_user_id:
            return False
        try:
            query = (
                self.db.collection(self.collection_name)
                .where("message_id", "==", message_id)
                .where("owner_user_id", "==", owner_user_id)
                .limit(1)
            )
            return len(list(query.stream())) > 0
        except Exception as e:
            logger.error(f"Error checking email duplicate: {e}")
            return False

    async def store_email(self, email_data: EmailDataSchema) -> str:
        """
        Store email data in Firebase
        
        Args:
            email_data: Email data to store
            
        Returns:
            str: Document ID of stored email
        """
        try:
            # Create a document reference
            email_ref = self.db.collection(self.collection_name).document()
            email_id = email_ref.id
            
            # Lookup user and project data
            logger.info(f"Looking up user and project data for email: {email_data.from_email}")
            user_project_data = await self.user_project_service.get_user_and_project_data(email_data.from_email)
            
            # Log lookup results
            first_name = user_project_data['user']['username']  # Note: 'username' key contains firstName value
            user_found = user_project_data['user']['found']
            project_found = user_project_data['project']['found']
            project_name = user_project_data['project']['project'].get('name', 'N/A') if project_found else None
            
            logger.info(f"User lookup result: firstName='{first_name}', found={user_found}")
            logger.info(f"Project lookup result: found={project_found}, project_name='{project_name}'")
            
            # Prepare data for Firebase
            firebase_data = {
                'subject': email_data.subject,
                'from_email': email_data.from_email,
                'to_email': email_data.to_email,
                'cc_email': email_data.cc_email or '',
                'bcc_email': email_data.bcc_email or '',
                'body': email_data.body,
                'html_body': email_data.html_body,
                'received_at': email_data.received_at,
                'message_id': email_data.message_id,
                'user_token': email_data.user_token,
                'owner_user_id': email_data.owner_user_id,
                'mailbox_email': email_data.mailbox_email or email_data.to_email,
                'created_at': datetime.now(timezone.utc),
                'processed': False,
                'isDeleted': False,
                'updated_at': datetime.now(timezone.utc),
                
                # User lookup data (sender_username contains firstName)
                'sender_username': user_project_data['user']['username'],
                'sender_user_id': user_project_data['user']['user_id'],
                'sender_found': user_project_data['user']['found'],
                
                # Project lookup data
                'assigned_project': user_project_data['project']['project'] if user_project_data['project']['found'] else None,
                'project_found': user_project_data['project']['found']
            }
            
            # Add attachments if present
            if email_data.attachments:
                print(f"Processing {len(email_data.attachments)} attachments for email")
                firebase_data['attachments'] = []
                for i, att in enumerate(email_data.attachments):
                    try:
                        # Convert attachment to simple dict to avoid Firebase nested entity issues
                        attachment_dict = {
                            'filename': str(att.filename) if att.filename else '',
                            'content_type': str(att.content_type) if att.content_type else '',
                            'size': int(att.size) if att.size is not None else 0,
                            'data': str(att.data) if att.data else ''
                        }
                        firebase_data['attachments'].append(attachment_dict)
                        print(f"Processed attachment {i+1}: {attachment_dict['filename']} ({attachment_dict['size']} bytes)")
                    except Exception as e:
                        print(f"Error processing attachment {i+1}: {e}")
                        continue
                firebase_data['has_attachments'] = True
                firebase_data['attachment_count'] = len(email_data.attachments)
                print(f"Total attachments processed: {len(firebase_data['attachments'])}")
            else:
                firebase_data['has_attachments'] = False
                firebase_data['attachment_count'] = 0
                print("No attachments to process")
            
            # Check data size before storing
            total_size = len(str(firebase_data))
            print(f"Total email data size: {total_size} bytes")
            
            if total_size > 1000000:  # 1MB limit
                print(f"Warning: Email data size ({total_size} bytes) exceeds 1MB limit")
                # For large emails, remove attachment data and store references only
                if firebase_data.get('attachments'):
                    print("Large email with attachments detected - storing attachment metadata only")
                    # Store only metadata, not the actual data
                    for att in firebase_data['attachments']:
                        att['data'] = f"[LARGE_FILE_{att['size']}_BYTES]"
                    print("Replaced attachment data with size indicators")
            
            # Store in Firebase
            email_ref.set(firebase_data)
            print(f"Successfully stored email {email_id} in Firebase")
            
            return email_id
            
        except Exception as e:
            raise Exception(f"Error storing email data: {str(e)}")
    
    async def get_emails(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[EmailFilterSchema] = None
    ) -> Dict[str, Any]:
        """
        Retrieve emails from Firebase with optional filtering
        
        Args:
            limit: Number of emails to retrieve
            offset: Number of emails to skip
            filters: Optional filters to apply
            
        Returns:
            Dict containing emails and metadata
        """
        try:
            query = self.db.collection(self.collection_name)
            
            # Apply filters
            if filters:
                if filters.owner_user_id:
                    query = query.where('owner_user_id', '==', filters.owner_user_id)
                if filters.mailbox_email:
                    query = query.where('mailbox_email', '==', filters.mailbox_email)
                if filters.user_token:
                    query = query.where('user_token', '==', filters.user_token)
                if filters.from_email:
                    query = query.where('from_email', '==', filters.from_email)
                if filters.has_attachments is not None:
                    query = query.where('has_attachments', '==', filters.has_attachments)
                if filters.processed is not None:
                    query = query.where('processed', '==', filters.processed)
                if filters.date_from:
                    query = query.where('received_at', '>=', filters.date_from)
                if filters.date_to:
                    query = query.where('received_at', '<=', filters.date_to)
            
            # Order by creation date (newest first)
            query = query.order_by('created_at', direction=Query.DESCENDING)
            
            # Apply pagination
            if offset > 0:
                # Get documents for offset
                offset_query = query.limit(offset)
                offset_docs = list(offset_query.stream())
                if len(offset_docs) < offset:
                    return {
                        'emails': [],
                        'total': 0,
                        'limit': limit,
                        'offset': offset
                    }
                # Start after the last offset document
                last_doc = offset_docs[-1]
                query = query.start_after(last_doc)
            
            # Get the requested number of documents
            docs = list(query.limit(limit).stream())
            
            emails = []
            for doc in docs:
                email_data = doc.to_dict()
                email_data['id'] = doc.id
                emails.append(email_data)
            
            # Get total count (this is expensive, consider caching)
            total_query = self.db.collection(self.collection_name)
            if filters:
                if filters.owner_user_id:
                    total_query = total_query.where('owner_user_id', '==', filters.owner_user_id)
                if filters.mailbox_email:
                    total_query = total_query.where('mailbox_email', '==', filters.mailbox_email)
                if filters.user_token:
                    total_query = total_query.where('user_token', '==', filters.user_token)
                if filters.from_email:
                    total_query = total_query.where('from_email', '==', filters.from_email)
                if filters.has_attachments is not None:
                    total_query = total_query.where('has_attachments', '==', filters.has_attachments)
                if filters.processed is not None:
                    total_query = total_query.where('processed', '==', filters.processed)
                if filters.date_from:
                    total_query = total_query.where('received_at', '>=', filters.date_from)
                if filters.date_to:
                    total_query = total_query.where('received_at', '<=', filters.date_to)
            
            total_docs = list(total_query.stream())
            total_count = len(total_docs)
            
            return {
                'emails': emails,
                'total': total_count,
                'limit': limit,
                'offset': offset
            }
            
        except Exception as e:
            raise Exception(f"Error retrieving emails: {str(e)}")
    
    async def get_email_by_id(self, email_id: str) -> Dict[str, Any]:
        """
        Retrieve a specific email by ID
        
        Args:
            email_id: Document ID
            
        Returns:
            Dict containing email data
        """
        try:
            doc = self.db.collection(self.collection_name).document(email_id).get()
            
            if not doc.exists:
                raise Exception("Email not found")
            
            email_data = doc.to_dict()
            email_data['id'] = doc.id
            
            return email_data
            
        except Exception as e:
            raise Exception(f"Error retrieving email: {str(e)}")
    
    async def update_email_status(
        self, 
        email_id: str, 
        status_data: Dict[str, Any]
    ) -> bool:
        """
        Update email processing status
        
        Args:
            email_id: Document ID
            status_data: Status data to update
            
        Returns:
            bool: Success status
        """
        try:
            status_data['updated_at'] = datetime.now(timezone.utc)
            
            self.db.collection(self.collection_name).document(email_id).update(status_data)
            
            return True
            
        except Exception as e:
            print(f"Error updating email status: {str(e)}")
            return False
    
    async def delete_email(self, email_id: str) -> bool:
        """
        Delete an email document
        
        Args:
            email_id: Document ID
            
        Returns:
            bool: Success status
        """
        try:
            self.db.collection(self.collection_name).document(email_id).delete()
            return True
            
        except Exception as e:
            print(f"Error deleting email: {str(e)}")
            return False
    
    async def search_emails(
        self, 
        search_term: str, 
        search_fields: List[str] = None,
        limit: int = 10,
        owner_user_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Search emails by text content
        
        Args:
            search_term: Text to search for
            search_fields: Fields to search in (default: subject, body)
            limit: Maximum number of results
            
        Returns:
            Dict containing search results
        """
        try:
            if search_fields is None:
                search_fields = ['subject', 'body']
            
            # Note: Firestore doesn't support full-text search natively
            # This is a basic implementation that searches in specific fields
            # For production, consider using Algolia or Elasticsearch
            
            query = self.db.collection(self.collection_name)
            if owner_user_id:
                query = query.where('owner_user_id', '==', owner_user_id)
            docs = list(query.limit(limit * 5).stream())
            
            results = []
            search_term_lower = search_term.lower()
            
            for doc in docs:
                email_data = doc.to_dict()
                email_data['id'] = doc.id
                
                # Check if search term is in any of the specified fields
                found = False
                for field in search_fields:
                    if field in email_data and email_data[field]:
                        if search_term_lower in str(email_data[field]).lower():
                            found = True
                            break
                
                if found:
                    results.append(email_data)
                    if len(results) >= limit:
                        break
            
            return {
                'emails': results,
                'total': len(results),
                'search_term': search_term,
                'search_fields': search_fields
            }
            
        except Exception as e:
            raise Exception(f"Error searching emails: {str(e)}")
