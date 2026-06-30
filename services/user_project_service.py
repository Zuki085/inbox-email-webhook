"""
User and Project Lookup Service

Handles user lookup by email and project assignment lookup for emails.
"""

from typing import Dict, Any, Optional
import logging
from firebase_admin import firestore
from config.firebase_config import get_firestore_client

logger = logging.getLogger(__name__)

class UserProjectService:
    """Service for user and project lookups"""
    
    def __init__(self):
        self.db = get_firestore_client()
    
    async def lookup_user_by_email(self, email: str) -> Dict[str, Any]:
        """
        Check sender email in users collection.
        If found → return firstName.
        If not found → return "unknown".
        
        Args:
            email: Sender email address
            
        Returns:
            Dict containing user information
        """
        try:
            # Query users collection by email
            users_ref = self.db.collection('users')
            query = users_ref.where('email', '==', email).limit(1)
            docs = list(query.stream())
            
            if docs:
                user_doc = docs[0]
                user_data = user_doc.to_dict()
                
                # Return user information
                return {
                    'found': True,
                    'username': user_data.get('firstName', user_data.get('username', user_data.get('name', 'unknown'))),
                    'user_id': user_doc.id,
                    'user_data': user_data
                }
            else:
                logger.info(f"User not found for email: {email}")
                return {
                    'found': False,
                    'username': 'unknown',
                    'user_id': None,
                    'user_data': None
                }
                
        except Exception as e:
            logger.error(f"Error looking up user by email {email}: {str(e)}")
            return {
                'found': False,
                'username': 'unknown',
                'user_id': None,
                'user_data': None,
                'error': str(e)
            }
    
    async def lookup_user_project(self, user_id: str) -> Dict[str, Any]:
        """
        Check assigned projects in assignProjects collection:
        Match userId (from user doc).
        If found, get the first projectId.
        Fetch corresponding project from projects collection.
        Return project object.
        
        Args:
            user_id: User document ID
            
        Returns:
            Dict containing project information
        """
        try:
            if not user_id:
                return {
                    'found': False,
                    'project': None,
                    'error': 'No user ID provided'
                }
            
            # Query assignProjects collection by userId
            assign_projects_ref = self.db.collection('assignProjects')
            query = assign_projects_ref.where('userId', '==', user_id).limit(1)
            docs = list(query.stream())
            
            if not docs:
                logger.info(f"No assigned projects found for user: {user_id}")
                return {
                    'found': False,
                    'project': None,
                    'message': 'No assigned projects found'
                }
            
            # Get the first assigned project
            assign_doc = docs[0]
            assign_data = assign_doc.to_dict()
            project_id = assign_data.get('projectId')
            
            if not project_id:
                logger.warning(f"No projectId found in assignment for user: {user_id}")
                return {
                    'found': False,
                    'project': None,
                    'error': 'No projectId in assignment'
                }
            
            # Fetch the project from projects collection
            project_ref = self.db.collection('projects').document(project_id)
            project_doc = project_ref.get()
            
            if not project_doc.exists:
                logger.warning(f"Project not found: {project_id}")
                return {
                    'found': False,
                    'project': None,
                    'error': f'Project {project_id} not found'
                }
            
            project_data = project_doc.to_dict()
            project_data['id'] = project_doc.id
            
            return {
                'found': True,
                'project': project_data,
                'project_id': project_id,
                'assignment_data': assign_data
            }
            
        except Exception as e:
            logger.error(f"Error looking up project for user {user_id}: {str(e)}")
            return {
                'found': False,
                'project': None,
                'error': str(e)
            }
    
    async def get_user_and_project_data(self, email: str) -> Dict[str, Any]:
        """
        Combined lookup for user and project data based on email
        
        Args:
            email: Sender email address
            
        Returns:
            Dict containing both user and project information
        """
        try:
            # First, lookup user by email
            user_result = await self.lookup_user_by_email(email)
            
            result = {
                'user': user_result,
                'project': {'found': False, 'project': None}
            }
            
            # If user found, lookup their assigned project
            if user_result['found'] and user_result['user_id']:
                project_result = await self.lookup_user_project(user_result['user_id'])
                result['project'] = project_result
            
            return result
            
        except Exception as e:
            logger.error(f"Error in combined lookup for email {email}: {str(e)}")
            return {
                'user': {
                    'found': False,
                    'username': 'unknown',
                    'user_id': None,
                    'error': str(e)
                },
                'project': {
                    'found': False,
                    'project': None,
                    'error': str(e)
                }
            }
