# Email Configuration Guide

This guide will help you configure your email webhook service to automatically receive and store emails in Firebase.

## Prerequisites

1. **Firebase Project**: You need a Firebase project with Firestore enabled
2. **Email Account**: Gmail, Outlook, Yahoo, or any IMAP-compatible email account
3. **App Password**: For Gmail, you'll need to generate an app password

## Step 1: Firebase Configuration

### Option A: Service Account Key (Recommended for Development)

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project
3. Go to Project Settings > Service Accounts
4. Click "Generate new private key"
5. Download the JSON file
6. Place it in your project directory
7. Set the environment variable:
    ```bash
    FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/your/firebase-service-account-key.json
    ```

### Option B: Environment Variables (Recommended for Production)

1. Go to Firebase Console > Project Settings > Service Accounts
2. Copy the configuration values
3. Set these environment variables:
    ```bash
    FIREBASE_PROJECT_ID=your-firebase-project-id
    FIREBASE_PRIVATE_KEY_ID=your-private-key-id
    FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
    FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
    FIREBASE_CLIENT_ID=your-client-id
    FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
    ```

## Step 2: Email Configuration

### Gmail Setup

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
    - Go to Google Account settings
    - Security > 2-Step Verification > App passwords
    - Generate a new app password for "Mail"
3. **Set Environment Variables**:
    ```bash
    EMAIL_HOST=imap.gmail.com
    EMAIL_PORT=993
    EMAIL_USERNAME=your-email@gmail.com
    EMAIL_PASSWORD=your-16-character-app-password
    EMAIL_USE_SSL=true
    ```

### Outlook Setup

1. **Enable IMAP** in your Outlook account settings
2. **Set Environment Variables**:
    ```bash
    EMAIL_HOST=outlook.office365.com
    EMAIL_PORT=993
    EMAIL_USERNAME=your-email@outlook.com
    EMAIL_PASSWORD=your-password
    EMAIL_USE_SSL=true
    ```

### Yahoo Setup

1. **Enable IMAP** in your Yahoo account settings
2. **Generate App Password**:
    - Go to Yahoo Account Security
    - Generate and manage app passwords
3. **Set Environment Variables**:
    ```bash
    EMAIL_HOST=imap.mail.yahoo.com
    EMAIL_PORT=993
    EMAIL_USERNAME=your-email@yahoo.com
    EMAIL_PASSWORD=your-app-password
    EMAIL_USE_SSL=true
    ```

## Step 3: Environment Variables

Create a `.env` file in your project root with the following variables:

```bash
# Firebase Configuration
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/your/firebase-service-account-key.json
# OR use environment variables
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com

# Email Configuration
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USERNAME=your-email@gmail.com
EMAIL_PASSWORD=your-app-password
EMAIL_USE_SSL=true

# Application Settings
DEBUG=true
LOG_LEVEL=INFO
CORS_ORIGINS=*

# Email Polling Settings
EMAIL_POLL_INTERVAL=60
EMAIL_POLL_ENABLED=true

# File Processing
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=pdf,jpg,jpeg,png,doc,docx
UPLOAD_DIRECTORY=Static

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run the Application

```bash
python -m email-webhook.main
```

The service will start and automatically begin polling for new emails.

## Step 6: Test the Configuration

### Check Health Status

```bash
curl http://localhost:8001/webhook/health
```

### Check Email Configuration

```bash
curl http://localhost:8001/webhook/email/config
```

### Manually Trigger Email Polling

```bash
curl -X POST http://localhost:8001/webhook/email/poll
```

### View Stored Emails

```bash
curl http://localhost:8001/webhook/emails
```

## API Endpoints

-   `GET /` - Service information
-   `POST /webhook/email` - Manual email webhook
-   `GET /webhook/emails` - List stored emails
-   `GET /webhook/emails/{email_id}` - Get specific email
-   `GET /webhook/emails/{email_id}/status` - Get processing status
-   `POST /webhook/emails/{email_id}/process` - Reprocess email
-   `DELETE /webhook/emails/{email_id}` - Delete email
-   `GET /webhook/search` - Search emails
-   `GET /webhook/health` - Health check
-   `POST /webhook/email/poll` - Trigger email polling
-   `GET /webhook/email/config` - Get email configuration

## Troubleshooting

### Common Issues

1. **Firebase Authentication Error**:

    - Check your service account key path
    - Verify Firebase project ID
    - Ensure Firestore is enabled

2. **Email Connection Error**:

    - Verify email credentials
    - Check if IMAP is enabled
    - For Gmail, ensure you're using an app password

3. **Permission Denied**:

    - Check file permissions for upload directory
    - Ensure Firebase has proper permissions

4. **Email Not Being Polled**:
    - Check if `EMAIL_POLL_ENABLED=true`
    - Verify email configuration
    - Check logs for errors

### Logs

The application logs important events. Check the console output for:

-   Firebase initialization status
-   Email polling status
-   Email processing results
-   Error messages

## Security Considerations

1. **Never commit** your `.env` file or service account keys
2. **Use app passwords** instead of regular passwords
3. **Restrict Firebase permissions** to only what's needed
4. **Use environment variables** in production
5. **Enable CORS** only for trusted origins

## Production Deployment

1. Set all environment variables in your deployment platform
2. Use a secure secret management system
3. Enable proper logging and monitoring
4. Set up health checks
5. Configure proper CORS origins
6. Use HTTPS for all communications

## Support

If you encounter issues:

1. Check the logs for error messages
2. Verify your configuration
3. Test with a simple email first
4. Check Firebase console for data
5. Use the health check endpoint to diagnose issues
