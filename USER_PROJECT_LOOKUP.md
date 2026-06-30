# User and Project Lookup System

This document explains the enhanced email webhook system that automatically looks up user information and project assignments when processing emails.

## Overview

The email webhook now automatically performs two key lookups when storing email data:

1. **User Lookup**: Checks sender email against the `users` collection
2. **Project Lookup**: Finds assigned projects for the user in `assignProjects` collection

## Features

### 1. User Lookup by Email

When an email is received, the system:

-   Queries the `users` collection by sender email address
-   If found: Returns firstName and user ID
-   If not found: Returns "unknown" as firstName

### 2. Project Assignment Lookup

If a user is found, the system:

-   Queries `assignProjects` collection by user ID
-   Gets the first assigned project ID
-   Fetches the complete project object from `projects` collection
-   Returns the project data

## Firebase Collections Structure

### Users Collection (`users`)

```json
{
	"email": "john.doe@example.com",
	"firstName": "John",
	"lastName": "Doe",
	"username": "john_doe",
	"name": "John Doe",
	"created_at": "2023-01-15T10:30:00Z"
	// other user fields...
}
```

### Assign Projects Collection (`assignProjects`)

```json
{
	"userId": "user_doc_id_123",
	"projectId": "project_doc_id_456",
	"assigned_at": "2023-02-01T14:20:00Z",
	"role": "developer"
	// other assignment fields...
}
```

### Projects Collection (`projects`)

```json
{
	"name": "Website Redesign",
	"description": "Complete redesign of company website",
	"status": "active",
	"created_at": "2023-01-10T09:00:00Z"
	// other project fields...
}
```

## Enhanced Email Document Structure

When emails are stored, they now include additional fields:

```json
{
	"subject": "Project Update",
	"from_email": "john.doe@example.com",
	"to_email": "webhook@company.com",
	"body": "Email content...",
	"received_at": "2023-03-15T16:45:00Z",

	// User lookup results
	"sender_username": "John",
	"sender_user_id": "user_doc_id_123",
	"sender_found": true,

	// Project lookup results
	"assigned_project": {
		"id": "project_doc_id_456",
		"name": "Website Redesign",
		"description": "Complete redesign of company website",
		"status": "active"
	},
	"project_found": true,

	// Standard email fields...
	"created_at": "2023-03-15T16:45:00Z",
	"processed": false,
	"isDeleted": false
}
```

## API Usage

### Storing Emails with Lookup

When you send an email to the webhook endpoint, the lookup happens automatically:

```bash
curl -X POST "http://localhost:8001/webhook/email" \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Test Email",
    "from_email": "john.doe@example.com",
    "to_email": "webhook@company.com",
    "body": "This is a test email",
    "received_at": "2023-03-15T16:45:00Z",
    "message_id": "test-123"
  }'
```

### Retrieving Emails with User/Project Data

```bash
# Get all emails with user and project data
curl "http://localhost:8001/webhook/emails"

# Get specific email with all lookup data
curl "http://localhost:8001/webhook/emails/{email_id}"
```

## Service Classes

### UserProjectService

Located in `services/user_project_service.py`, this service handles:

-   `lookup_user_by_email(email)`: Find user by email address and return firstName
-   `lookup_user_project(user_id)`: Find assigned project for user
-   `get_user_and_project_data(email)`: Combined lookup

### Enhanced FirebaseService

The `FirebaseService` in `services/firebase_service.py` now:

-   Automatically performs user/project lookup during email storage
-   Includes lookup results in the stored email document
-   Logs lookup results for debugging

## Error Handling

The system gracefully handles various scenarios:

1. **User not found**: Sets `sender_username` to "unknown"
2. **No assigned projects**: Sets `assigned_project` to null
3. **Project not found**: Sets `assigned_project` to null
4. **Database errors**: Logs errors and continues with default values

## Logging

The system provides detailed logging:

```
INFO - Looking up user and project data for email: john.doe@example.com
INFO - User lookup result: firstName='John', found=True
INFO - Project lookup result: found=True, project_name='Website Redesign'
```

## Testing

Use the test script to verify functionality:

```bash
python test_user_project_lookup.py
```

This will show:

-   How user lookup works
-   How project lookup works
-   What data gets stored in emails

## Configuration

No additional configuration is required. The system uses your existing Firebase connection and automatically queries the required collections.

## Benefits

1. **Automatic User Identification**: No need to manually lookup senders
2. **Project Context**: Emails are automatically associated with projects
3. **Enhanced Filtering**: Filter emails by username or project
4. **Audit Trail**: Track which users are sending emails
5. **Project Management**: See all emails related to specific projects

## Migration

Existing emails will not have the new fields. Only new emails processed after this update will include user and project lookup data.

## Performance Considerations

-   User lookup: Single query by email (indexed field recommended)
-   Project lookup: Two queries (assignProjects + projects)
-   Results are cached within the same request
-   Consider adding database indexes on frequently queried fields

## Troubleshooting

### Common Issues

1. **User not found**: Verify email exists in `users` collection
2. **Project not found**: Check `assignProjects` and `projects` collections
3. **Slow lookups**: Add database indexes on `email`, `userId`, and `projectId` fields

### Debug Logging

Enable debug logging to see detailed lookup information:

```python
import logging
logging.getLogger('services.user_project_service').setLevel(logging.DEBUG)
logging.getLogger('services.firebase_service').setLevel(logging.DEBUG)
```
