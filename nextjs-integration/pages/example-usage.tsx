// Example usage page for Next.js integration
// This shows how to use the email attachment preview components

import React from 'react';
import EmailList from '../components/EmailList';
import AttachmentViewer from '../components/AttachmentViewer';

export default function ExampleUsage() {
	return (
		<div className='min-h-screen bg-gray-50'>
			<div className='max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8'>
				<div className='mb-8'>
					<h1 className='text-3xl font-bold text-gray-900'>
						Email Attachment Preview System
					</h1>
					<p className='mt-2 text-gray-600'>
						This example demonstrates how to integrate email
						attachment previewing with your webhook system.
					</p>
				</div>

				{/* Example 1: Full Email List with Attachments */}
				<div className='mb-12'>
					<h2 className='text-2xl font-semibold text-gray-900 mb-4'>
						Example 1: Email List with Attachment Preview
					</h2>
					<div className='bg-white rounded-lg shadow'>
						<EmailList userToken='your-user-token' />
					</div>
				</div>

				{/* Example 2: Standalone Attachment Viewer */}
				<div className='mb-12'>
					<h2 className='text-2xl font-semibold text-gray-900 mb-4'>
						Example 2: Standalone Attachment Viewer
					</h2>
					<div className='bg-white rounded-lg shadow p-6'>
						<p className='text-gray-600 mb-4'>
							Replace 'your-email-id' with an actual email ID from
							your system:
						</p>
						<AttachmentViewer emailId='your-email-id' />
					</div>
				</div>

				{/* Configuration Instructions */}
				<div className='bg-blue-50 border border-blue-200 rounded-lg p-6'>
					<h3 className='text-lg font-semibold text-blue-900 mb-2'>
						Configuration Required
					</h3>
					<div className='text-blue-800 space-y-2'>
						<p>
							1. Set your webhook base URL in environment
							variables:
						</p>
						<code className='block bg-blue-100 p-2 rounded text-sm'>
							NEXT_PUBLIC_WEBHOOK_BASE_URL=http://localhost:8000
						</code>

						<p className='mt-4'>
							2. Make sure your webhook server is running and
							accessible.
						</p>

						<p className='mt-4'>
							3. Replace placeholder values with actual data:
						</p>
						<ul className='list-disc list-inside ml-4 space-y-1'>
							<li>
								Replace 'your-user-token' with actual user
								tokens
							</li>
							<li>
								Replace 'your-email-id' with actual email IDs
							</li>
						</ul>
					</div>
				</div>

				{/* API Endpoints Reference */}
				<div className='mt-8 bg-gray-50 rounded-lg p-6'>
					<h3 className='text-lg font-semibold text-gray-900 mb-4'>
						Available API Endpoints
					</h3>
					<div className='space-y-3 text-sm'>
						<div>
							<code className='bg-gray-200 px-2 py-1 rounded'>
								GET /webhook/emails
							</code>
							<span className='ml-2 text-gray-600'>
								- List emails with pagination
							</span>
						</div>
						<div>
							<code className='bg-gray-200 px-2 py-1 rounded'>
								GET /webhook/emails/{`{id}`}/attachments
							</code>
							<span className='ml-2 text-gray-600'>
								- List email attachments
							</span>
						</div>
						<div>
							<code className='bg-gray-200 px-2 py-1 rounded'>
								GET /webhook/emails/{`{id}`}/attachments/
								{`{index}`}/view
							</code>
							<span className='ml-2 text-gray-600'>
								- View attachment inline
							</span>
						</div>
						<div>
							<code className='bg-gray-200 px-2 py-1 rounded'>
								GET /webhook/emails/{`{id}`}/attachments/
								{`{index}`}/download
							</code>
							<span className='ml-2 text-gray-600'>
								- Download attachment
							</span>
						</div>
						<div>
							<code className='bg-gray-200 px-2 py-1 rounded'>
								GET /webhook/emails/{`{id}`}/attachments/
								{`{index}`}/info
							</code>
							<span className='ml-2 text-gray-600'>
								- Get attachment metadata
							</span>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
