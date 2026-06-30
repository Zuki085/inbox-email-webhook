# Email Attachment System

This document explains the new attachment handling system that solves the issues with storing large binary data directly in Firestore.

## Problem Solved

The previous system had several issues:

-   **Size limitations**: Firestore has a 1MB document size limit
-   **Performance**: Large binary data in Firestore slows down queries
-   **Cost**: Storing large binary data in Firestore is expensive
-   **Memory usage**: Loading emails with large attachments consumed too much memory

## New Architecture

### File Storage Service (`services/file_storage_service.py`)

The `FileStorageService` handles all file operations:

-   Stores attachment files on the local filesystem
-   Organizes files by year/month for better management
-   Generates unique filenames to avoid conflicts
-   Provides methods for retrieving, deleting, and getting file information

**Key Features:**

-   Files stored in `storage/attachments/YYYY/MM/` directory structure
-   Unique UUID-based filenames to prevent conflicts
-   Base64 decoding of attachment data
-   File metadata tracking

### Updated Firebase Service (`services/firebase_service.py`)

The `FirebaseService` now stores file references instead of raw data:

-   Stores file metadata and references in Firestore
-   Provides methods to retrieve and download attachments
-   Handles attachment deletion and updates

**Key Changes:**

-   `attachments` field now contains file references instead of raw data
-   New methods: `get_attachment()`, `get_attachment_info()`, `get_attachment_url()`, `delete_attachment()`
-   Automatic file cleanup when attachments are deleted

### API Endpoints (`routes/webhook.py`)

New REST endpoints for attachment management:

#### Get Email Attachments

```
GET /webhook/emails/{email_id}/attachments
```

Returns a list of all attachments for an email.

#### Download Attachment

```
GET /webhook/emails/{email_id}/attachments/{attachment_index}/download
```

Downloads a specific attachment file.

#### Get Attachment Info

```
GET /webhook/emails/{email_id}/attachments/{attachment_index}/info
```

Returns metadata about a specific attachment without downloading.

#### Delete Attachment

```
DELETE /webhook/emails/{email_id}/attachments/{attachment_index}
```

Deletes a specific attachment.

## Usage Examples

### 1. Storing an Email with Attachments

```python
from services.firebase_service import FirebaseService
from models.schemas import EmailDataSchema, EmailAttachmentSchema

firebase_service = FirebaseService()

# Create attachment
attachment = EmailAttachmentSchema(
    filename="document.pdf",
    content_type="application/pdf",
    size=1024000,
    data=base64_encoded_data
)

# Create email
email_data = EmailDataSchema(
    subject="Email with PDF",
    from_email="sender@example.com",
    to_email="recipient@example.com",
    body="Please see attached document.",
    attachments=[attachment],
    received_at=datetime.now(timezone.utc),
    message_id="unique-message-id",
    user_token="user-token"
)

# Store email
email_id = await firebase_service.store_email(email_data)
```

### 2. Retrieving Attachment Information

```python
# Get attachment info without downloading
attachment_info = await firebase_service.get_attachment_info(email_id, 0)
print(f"Filename: {attachment_info['original_filename']}")
print(f"Size: {attachment_info['size']} bytes")
print(f"Content type: {attachment_info['content_type']}")
```

### 3. Downloading an Attachment

```python
# Download attachment data
attachment_data = await firebase_service.get_attachment(email_id, 0)
if attachment_data:
    with open(attachment_data['filename'], 'wb') as f:
        f.write(attachment_data['data'])
```

### 4. Using API Endpoints

#### Get all attachments for an email:

```bash
curl -X GET "http://localhost:8000/webhook/emails/{email_id}/attachments"
```

#### Download a specific attachment:

```bash
curl -X GET "http://localhost:8000/webhook/emails/{email_id}/attachments/0/download" \
     -o "downloaded_file.pdf"
```

#### Get attachment metadata:

```bash
curl -X GET "http://localhost:8000/webhook/emails/{email_id}/attachments/0/info"
```

## File Organization

Files are stored in the following structure:

```
storage/
└── attachments/
    └── 2024/
        └── 01/
            ├── uuid1.pdf
            ├── uuid2.jpg
            └── uuid3.docx
    └── 2024/
        └── 02/
            ├── uuid4.pdf
            └── uuid5.xlsx
```

## Benefits

1. **No size limitations**: Files are stored on disk, not in Firestore
2. **Better performance**: Email queries are faster without large binary data
3. **Lower costs**: Only metadata stored in Firestore
4. **Better organization**: Files organized by date
5. **Efficient downloads**: Direct file serving without database overhead
6. **Easy cleanup**: Files can be easily managed and deleted

## Migration from Old System

If you have existing emails with attachments stored in the old format, you'll need to:

1. **Backup existing data**: Export emails with attachments
2. **Update storage**: Re-process emails to use new file storage
3. **Clean up**: Remove old attachment data from Firestore

## Configuration

The file storage path can be configured in the `FileStorageService` constructor:

```python
file_storage = FileStorageService(storage_path="custom/storage/path")
```

## Security Considerations

-   Files are stored with UUID names to prevent directory traversal
-   Original filenames are preserved in metadata
-   Consider implementing access controls for sensitive attachments
-   Regular cleanup of orphaned files is recommended

## Monitoring

Use the `get_storage_stats()` method to monitor storage usage:

```python
stats = file_storage.get_storage_stats()
print(f"Total files: {stats['total_files']}")
print(f"Total size: {stats['total_size_mb']} MB")
```
