# Gmail Email Webhook Setup for zeework98@gmail.com

This guide will help you set up the email webhook system to automatically receive and store emails from `zeework98@gmail.com` in Firebase.

## Prerequisites

1. **Gmail Account**: Access to `zeework98@gmail.com`
2. **Firebase Project**: A Firebase project with Firestore enabled
3. **App Password**: Gmail app password (not your regular password)

## Step 1: Enable Gmail App Password

1. Go to your Google Account settings: https://myaccount.google.com/
2. Navigate to **Security** → **2-Step Verification** (enable if not already)
3. Go to **App passwords** (you may need to search for it)
4. Select **Mail** and **Other (custom name)**
5. Enter "Email Webhook Service" as the name
6. Copy the generated 16-character password (you'll need this for `EMAIL_PASSWORD`)

## Step 2: Firebase Setup

### Option A: Service Account Key (Recommended for Development)

1. Go to Firebase Console: https://console.firebase.google.com/
2. Select your project
3. Go to **Project Settings** → **Service Accounts**
4. Click **Generate New Private Key**
5. Download the JSON file and place it in your project directory
6. Set `FIREBASE_SERVICE_ACCOUNT_KEY_PATH` to the path of this file

### Option B: Environment Variables (Recommended for Production)

1. In Firebase Console, go to **Project Settings** → **Service Accounts**
2. Copy the following values from your service account:
    - `project_id`
    - `private_key_id`
    - `private_key`
    - `client_email`
    - `client_id`
    - `client_x509_cert_url`

## Step 3: Environment Configuration

Create a `.env` file in your project root with the following configuration:

```env
# Gmail Configuration for zeework98@gmail.com
EMAIL_USERNAME=zeework98@gmail.com
EMAIL_PASSWORD=your_16_character_app_password
EMAIL_HOST=imap.gmail.com
EMAIL_PORT=993
EMAIL_USE_SSL=true
EMAIL_POLL_ENABLED=true
EMAIL_POLL_INTERVAL=60

# Firebase Configuration (choose one option)
# Option 1: Service Account Key File
FIREBASE_SERVICE_ACCOUNT_KEY_PATH=path/to/your/service-account-key.json

# Option 2: Environment Variables
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com

# Application Settings
DEBUG=false
LOG_LEVEL=INFO
```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 5: Run the Email Webhook Service

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

## How It Works

1. **Email Polling**: The service polls Gmail every 60 seconds for new emails
2. **Email Processing**: When new emails are found, they are:
    - Parsed to extract subject, body, attachments, etc.
    - Stored in Firebase Firestore
    - Marked as read in Gmail
3. **Webhook Endpoints**: The service provides REST API endpoints to:
    - View stored emails
    - Search emails
    - Get email details
    - Process emails

## API Endpoints

-   `GET /` - Service status and available endpoints
-   `POST /webhook/email` - Manual email webhook (for testing)
-   `GET /webhook/emails` - List stored emails
-   `GET /webhook/emails/{id}` - Get specific email
-   `GET /webhook/health` - Health check
-   `POST /webhook/email/poll` - Manually trigger email polling

## Testing

1. **Send a test email** to `zeework98@gmail.com`
2. **Check the logs** to see if the email was processed
3. **Query the API** to see stored emails:
    ```bash
    curl http://localhost:8001/webhook/emails
    ```

## Troubleshooting

### Common Issues

1. **Authentication Error**: Make sure you're using an app password, not your regular Gmail password
2. **Firebase Connection Error**: Verify your Firebase credentials and project ID
3. **No Emails Found**: Check if emails are marked as unread in Gmail
4. **Permission Denied**: Ensure your Firebase service account has Firestore permissions

### Logs

The service logs all activities. Check the console output for:

-   ✅ Successful operations
-   ❌ Error messages
-   ℹ️ Information messages

## Security Notes

-   Never commit your `.env` file to version control
-   Use app passwords instead of regular passwords
-   Regularly rotate your app passwords
-   Ensure your Firebase service account has minimal required permissions


