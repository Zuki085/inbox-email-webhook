#!/usr/bin/env python3
"""
Examples of storing and accessing direct URLs for attachments in Firebase

This script demonstrates multiple approaches to store URLs that can be opened directly in browsers.
"""

import asyncio
import base64
from services.firebase_service import FirebaseService

async def example_direct_urls():
    """Example showing how to work with direct URLs"""
    
    firebase_service = FirebaseService()
    
    # Example email ID (replace with actual)
    email_id = "your-email-document-id-here"
    
    try:
        print("=== Direct URL Examples ===\n")
        
        # Method 1: Get all attachment URLs for an email
        print("1. Get all attachment URLs:")
        attachment_urls = await firebase_service.get_attachment_urls(email_id)
        
        for i, url_info in enumerate(attachment_urls):
            print(f"   Attachment {i}:")
            print(f"     Filename: {url_info['filename']}")
            print(f"     Download URL: {url_info['url']}")
            print(f"     View URL: {url_info['view_url']}")
            print(f"     Content Type: {url_info['content_type']}")
            print(f"     Size: {url_info['size']} bytes")
            print()
        
        # Method 2: Get specific attachment URL
        if attachment_urls:
            print("2. Get specific attachment URL:")
            specific_url = await firebase_service.get_attachment_url(email_id, 0)
            print(f"   First attachment URL: {specific_url}")
            print()
        
        # Method 3: Show how URLs work in different contexts
        print("3. URL Usage Examples:")
        if attachment_urls:
            url_info = attachment_urls[0]
            
            print("   HTML Link (download):")
            print(f'   <a href="{url_info["url"]}" download="{url_info["filename"]}">Download {url_info["filename"]}</a>')
            print()
            
            print("   HTML Image (inline view):")
            if url_info['content_type'].startswith('image/'):
                print(f'   <img src="{url_info["view_url"]}" alt="{url_info["filename"]}" />')
            print()
            
            print("   HTML iframe (for PDFs):")
            if url_info['content_type'] == 'application/pdf':
                print(f'   <iframe src="{url_info["view_url"]}" width="100%" height="600px"></iframe>')
            print()
            
            print("   JavaScript fetch:")
            print(f'   fetch("{url_info["url"]}")')
            print()
        
    except Exception as e:
        print(f"Error: {e}")

def create_html_viewer_with_urls(email_id: str):
    """Create an HTML viewer that uses direct URLs"""
    
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Email Attachment Viewer with Direct URLs</title>
    <style>
        body {{ 
            font-family: Arial, sans-serif; 
            margin: 20px; 
            background: #f5f5f5;
        }}
        .container {{ 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .attachment {{ 
            border: 1px solid #ddd; 
            padding: 20px; 
            margin: 20px 0; 
            border-radius: 5px;
            background: #fafafa;
        }}
        .btn {{ 
            background: #007bff; 
            color: white; 
            padding: 10px 20px; 
            text-decoration: none; 
            border-radius: 5px; 
            display: inline-block;
            margin: 5px;
            border: none;
            cursor: pointer;
        }}
        .btn:hover {{ background: #0056b3; }}
        .btn-success {{ background: #28a745; }}
        .btn-info {{ background: #17a2b8; }}
        .attachment-preview {{
            margin: 10px 0;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background: white;
        }}
        .url-display {{
            background: #f8f9fa;
            padding: 10px;
            border-radius: 3px;
            font-family: monospace;
            word-break: break-all;
            margin: 10px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📎 Email Attachment Viewer</h1>
        <p><strong>Email ID:</strong> {email_id}</p>
        
        <div class="attachment">
            <h3>🔗 Direct URL Access</h3>
            <p>These URLs can be opened directly in any browser:</p>
            
            <h4>API Endpoints:</h4>
            <ul>
                <li><strong>Get all attachment URLs:</strong> <code>GET /webhook/emails/{email_id}/attachments/urls</code></li>
                <li><strong>Download attachment:</strong> <code>GET /webhook/emails/{email_id}/attachments/0/download</code></li>
                <li><strong>View inline:</strong> <code>GET /webhook/emails/{email_id}/attachments/0/view</code></li>
            </ul>
            
            <h4>Example URLs:</h4>
            <div class="url-display">
                Download: http://localhost:8000/webhook/emails/{email_id}/attachments/0/download<br>
                View: http://localhost:8000/webhook/emails/{email_id}/attachments/0/view
            </div>
            
            <h4>Actions:</h4>
            <button class="btn" onclick="loadAttachments()">Load Attachments</button>
            <button class="btn btn-success" onclick="openAllUrls()">Open All URLs</button>
            <button class="btn btn-info" onclick="copyUrls()">Copy URLs</button>
        </div>
        
        <div id="attachments-container">
            <!-- Attachments will be loaded here -->
        </div>
    </div>

    <script>
        let attachmentUrls = [];
        
        async function loadAttachments() {{
            try {{
                const response = await fetch(`/webhook/emails/{email_id}/attachments/urls`);
                const data = await response.json();
                
                if (data.attachment_urls) {{
                    attachmentUrls = data.attachment_urls;
                    displayAttachments(data.attachment_urls);
                }} else {{
                    document.getElementById('attachments-container').innerHTML = 
                        '<div class="attachment"><p>No attachments found or error loading data.</p></div>';
                }}
            }} catch (error) {{
                console.error('Error loading attachments:', error);
                document.getElementById('attachments-container').innerHTML = 
                    '<div class="attachment"><p>Error loading attachments: ' + error.message + '</p></div>';
            }}
        }}
        
        function displayAttachments(attachments) {{
            const container = document.getElementById('attachments-container');
            container.innerHTML = '';
            
            if (attachments.length === 0) {{
                container.innerHTML = '<div class="attachment"><p>No attachments found.</p></div>';
                return;
            }}
            
            attachments.forEach((attachment, index) => {{
                const attachmentDiv = document.createElement('div');
                attachmentDiv.className = 'attachment';
                
                const isImage = attachment.content_type.startsWith('image/');
                const isPdf = attachment.content_type === 'application/pdf';
                
                attachmentDiv.innerHTML = `
                    <h4>📄 ${{attachment.filename}}</h4>
                    <p><strong>Type:</strong> ${{attachment.content_type}} | <strong>Size:</strong> ${{attachment.size}} bytes</p>
                    
                    <div class="url-display">
                        <strong>Download URL:</strong><br>
                        <a href="${{attachment.url}}" target="_blank">${{attachment.url}}</a>
                    </div>
                    
                    <div class="url-display">
                        <strong>View URL:</strong><br>
                        <a href="${{attachment.view_url}}" target="_blank">${{attachment.view_url}}</a>
                    </div>
                    
                    <div style="margin: 10px 0;">
                        <a href="${{attachment.url}}" class="btn" download="${{attachment.filename}}">⬇️ Download</a>
                        <a href="${{attachment.view_url}}" class="btn btn-success" target="_blank">👁️ View Inline</a>
                        <button class="btn btn-info" onclick="copyToClipboard('${{attachment.url}}')">📋 Copy URL</button>
                    </div>
                    
                    ${{isImage ? `
                        <div class="attachment-preview">
                            <h5>Preview:</h5>
                            <img src="${{attachment.view_url}}" alt="${{attachment.filename}}" style="max-width: 100%; height: auto;" />
                        </div>
                    ` : ''}}
                    
                    ${{isPdf ? `
                        <div class="attachment-preview">
                            <h5>PDF Preview:</h5>
                            <iframe src="${{attachment.view_url}}" width="100%" height="400px" style="border: 1px solid #ccc;"></iframe>
                        </div>
                    ` : ''}}
                `;
                
                container.appendChild(attachmentDiv);
            }});
        }}
        
        function openAllUrls() {{
            attachmentUrls.forEach(attachment => {{
                window.open(attachment.view_url, '_blank');
            }});
        }}
        
        function copyUrls() {{
            const urls = attachmentUrls.map(att => att.url).join('\\n');
            copyToClipboard(urls);
        }}
        
        function copyToClipboard(text) {{
            navigator.clipboard.writeText(text).then(() => {{
                alert('URL copied to clipboard!');
            }}).catch(err => {{
                console.error('Failed to copy: ', err);
            }});
        }}
        
        // Auto-load attachments when page loads
        window.onload = loadAttachments;
    </script>
</body>
</html>
    """
    
    with open("attachment_viewer_with_urls.html", "w") as f:
        f.write(html_content)
    
    print("HTML viewer with direct URLs created: attachment_viewer_with_urls.html")
    print("Open this file in your browser to see the interface with direct URLs")

def create_data_url_example():
    """Example of creating data URLs for direct browser viewing"""
    
    example_data_url = """
# Data URL Examples for Direct Browser Viewing

## Method 1: Data URLs (for small files)
Data URLs embed the file content directly in the URL:

```html
<!-- For images -->
<img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==" />

<!-- For PDFs -->
<iframe src="data:application/pdf;base64,JVBERi0xLjQKJcfsj6IKNSAwIG9iago8PAovVHlwZSAvQ2F0YWxvZwovUGFnZXMgMiAwIFI+PgplbmRvYmoKMiAwIG9iago8PAovVHlwZSAvUGFnZXMKL0tpZHMgWzMgMCBSXQovQ291bnQgMQo+PgplbmRvYmoKMyAwIG9iago8PAovVHlwZSAvUGFnZQovUGFyZW50IDIgMCBSCi9SZXNvdXJjZXMgPDwKL0ZvbnQgPDwKL0YxIDQgMCBSCj4+Cj4+Ci9NZWRpYUJveCBbMCAwIDU5NSA4NDJdCi9Db250ZW50cyA1IDAgUgo+PgplbmRvYmoKNCAwIG9iago8PAovVHlwZSAvRm9udAovU3VidHlwZSAvVHlwZTEKL0Jhc2VGb250IC9IZWx2ZXRpY2EKPj4KZW5kb2JqCjUgMCBvYmoKPDwKL0xlbmd0aCA0NAo+PgpzdHJlYW0KQlQKL0YxIDEyIFRmCjAgMCAwIHJnCjcyIDcyMCAgVGQKKFRlc3QgUERGKSBUagoKRVQKZW5kc3RyZWFtCmVuZG9iagp4cmVmCjAgNgowMDAwMDAwMDAwIDY1NTM1IGYKMDAwMDAwMDAwOSAwMDAwMCBuCjAwMDAwMDAwNzQgMDAwMDAgbgowMDAwMDAwMTIwIDAwMDAwIG4KMDAwMDAwMDE3NSAwMDAwMCBuCjAwMDAwMDAyNDAgMDAwMDAgbgp0cmFpbGVyCjw8Ci9TaXplIDYKL1Jvb3QgMSAwIFIKPj4Kc3RhcnR4cmVmCjMzNQolJUVPRgo=" />

<!-- For any file type -->
<a href="data:text/plain;base64,SGVsbG8gV29ybGQ=" download="hello.txt">Download Text File</a>
```

## Method 2: Direct Server URLs (Recommended)
Store URLs in Firebase that point to your server endpoints:

```json
{{
  "attachment_urls": [
    {{
      "filename": "document.pdf",
      "url": "http://localhost:8000/webhook/emails/abc123/attachments/0/download",
      "view_url": "http://localhost:8000/webhook/emails/abc123/attachments/0/view",
      "content_type": "application/pdf",
      "size": 1024000
    }}
  ]
}}
```

## Method 3: Cloud Storage URLs
Store files in cloud storage (AWS S3, Google Cloud Storage, etc.) and store the public URLs:

```json
{{
  "attachment_urls": [
    {{
      "filename": "document.pdf",
      "url": "https://storage.googleapis.com/your-bucket/attachments/abc123/document.pdf",
      "content_type": "application/pdf",
      "size": 1024000
    }}
  ]
}}
```

## Method 4: CDN URLs
Use a Content Delivery Network for better performance:

```json
{{
  "attachment_urls": [
    {{
      "filename": "document.pdf",
      "url": "https://cdn.yoursite.com/attachments/abc123/document.pdf",
      "content_type": "application/pdf",
      "size": 1024000
    }}
  ]
}}
```
    """
    
    with open("data_url_examples.md", "w") as f:
        f.write(example_data_url)
    
    print("Data URL examples created: data_url_examples.md")

if __name__ == "__main__":
    print("Direct URL Storage Examples")
    print("=" * 50)
    
    # Example 1: Show how to work with direct URLs
    print("1. Working with direct URLs:")
    print("   - Run: asyncio.run(example_direct_urls())")
    
    # Example 2: Create HTML viewer
    print("\n2. Create HTML viewer with direct URLs:")
    print("   - Run: create_html_viewer_with_urls('your-email-id')")
    
    # Example 3: Show data URL examples
    print("\n3. Create data URL examples:")
    print("   - Run: create_data_url_example()")
    
    print("\n" + "=" * 50)
    print("Available URL Types:")
    print("✅ Direct server URLs (recommended)")
    print("✅ Data URLs (for small files)")
    print("✅ Cloud storage URLs")
    print("✅ CDN URLs")
    print("✅ Inline viewing URLs")
    
    # Create the examples
    create_html_viewer_with_urls("example-email-id")
    create_data_url_example()
