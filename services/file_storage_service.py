"""
File Storage Service

Handles file storage for email attachments using local filesystem or cloud storage.
This service manages attachment files separately from Firestore to avoid size limitations.
"""

import os
import base64
import uuid
from typing import Optional, Dict, Any, BinaryIO
from datetime import datetime, timezone
from pathlib import Path
import mimetypes
import shutil

class FileStorageService:
    """Service for managing file storage for email attachments"""
    
    def __init__(self, storage_path: str = "storage/attachments"):
        """
        Initialize file storage service
        
        Args:
            storage_path: Base directory for storing files
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories by year/month for organization
        current_date = datetime.now()
        self.current_year = current_date.year
        self.current_month = current_date.month
        
    def _get_storage_directory(self, year: int = None, month: int = None) -> Path:
        """Get storage directory for a specific year/month"""
        if year is None:
            year = self.current_year
        if month is None:
            month = self.current_month
            
        dir_path = self.storage_path / str(year) / f"{month:02d}"
        dir_path.mkdir(parents=True, exist_ok=True)
        return dir_path
    
    async def store_attachment(
        self, 
        filename: str, 
        content_type: str, 
        data: str, 
        email_id: str,
        year: int = None,
        month: int = None
    ) -> Dict[str, Any]:
        """
        Store attachment file and return file reference
        
        Args:
            filename: Original filename
            content_type: MIME type
            data: Base64 encoded file data
            email_id: Associated email ID
            year: Year for directory organization (defaults to current)
            month: Month for directory organization (defaults to current)
            
        Returns:
            Dict containing file reference information
        """
        try:
            # Decode base64 data
            file_data = base64.b64decode(data)
            
            # Generate unique filename to avoid conflicts
            file_extension = Path(filename).suffix
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            
            # Get storage directory
            storage_dir = self._get_storage_directory(year, month)
            
            # Full file path
            file_path = storage_dir / unique_filename
            
            # Write file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Create file reference
            file_reference = {
                'file_id': str(uuid.uuid4()),
                'original_filename': filename,
                'stored_filename': unique_filename,
                'file_path': str(file_path),
                'relative_path': f"{year}/{month:02d}/{unique_filename}",
                'content_type': content_type,
                'size': len(file_data),
                'email_id': email_id,
                'stored_at': datetime.now(timezone.utc),
                'year': year or self.current_year,
                'month': month or self.current_month
            }
            
            return file_reference
            
        except Exception as e:
            raise Exception(f"Error storing attachment: {str(e)}")
    
    async def get_attachment(self, file_reference: Dict[str, Any]) -> Optional[bytes]:
        """
        Retrieve attachment file data
        
        Args:
            file_reference: File reference from database
            
        Returns:
            File data as bytes, or None if not found
        """
        try:
            file_path = Path(file_reference['file_path'])
            
            if not file_path.exists():
                return None
            
            with open(file_path, 'rb') as f:
                return f.read()
                
        except Exception as e:
            print(f"Error retrieving attachment: {str(e)}")
            return None
    
    async def get_attachment_info(self, file_reference: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Get attachment file information without loading the file
        
        Args:
            file_reference: File reference from database
            
        Returns:
            File information dict, or None if not found
        """
        try:
            file_path = Path(file_reference['file_path'])
            
            if not file_path.exists():
                return None
            
            stat = file_path.stat()
            
            return {
                'file_id': file_reference['file_id'],
                'original_filename': file_reference['original_filename'],
                'stored_filename': file_reference['stored_filename'],
                'content_type': file_reference['content_type'],
                'size': file_reference['size'],
                'actual_size': stat.st_size,
                'stored_at': file_reference['stored_at'],
                'last_modified': datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                'exists': True
            }
            
        except Exception as e:
            print(f"Error getting attachment info: {str(e)}")
            return None
    
    async def delete_attachment(self, file_reference: Dict[str, Any]) -> bool:
        """
        Delete attachment file
        
        Args:
            file_reference: File reference from database
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            file_path = Path(file_reference['file_path'])
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
            
        except Exception as e:
            print(f"Error deleting attachment: {str(e)}")
            return False
    
    async def get_attachment_url(self, file_reference: Dict[str, Any], base_url: str = "") -> str:
        """
        Generate URL for accessing attachment
        
        Args:
            file_reference: File reference from database
            base_url: Base URL for the application
            
        Returns:
            URL for accessing the attachment
        """
        file_id = file_reference['file_id']
        return f"{base_url}/attachments/{file_id}/download"
    
    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics
        
        Returns:
            Dict containing storage statistics
        """
        try:
            total_files = 0
            total_size = 0
            
            for file_path in self.storage_path.rglob('*'):
                if file_path.is_file():
                    total_files += 1
                    total_size += file_path.stat().st_size
            
            return {
                'total_files': total_files,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2),
                'storage_path': str(self.storage_path)
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'total_files': 0,
                'total_size_bytes': 0,
                'total_size_mb': 0
            }
