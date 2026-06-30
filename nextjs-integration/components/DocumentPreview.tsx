'use client';

import React, { useState, useEffect } from 'react';
import { EmailAttachment } from '../types/email';
import { emailAPI } from '../lib/api';

interface DocumentPreviewProps {
	emailId: string;
	attachmentIndex: number;
	attachment: EmailAttachment;
}

export default function DocumentPreview({
	emailId,
	attachmentIndex,
	attachment,
}: DocumentPreviewProps) {
	const [content, setContent] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		loadContent();
	}, [emailId, attachmentIndex]);

	const loadContent = async () => {
		try {
			setLoading(true);
			setError(null);

			// For text files, try to fetch and display content
			if (attachment.content_type.startsWith('text/')) {
				const viewUrl = emailAPI.getAttachmentViewUrl(
					emailId,
					attachmentIndex
				);
				const response = await fetch(viewUrl);

				if (!response.ok) {
					throw new Error('Failed to load content');
				}

				const text = await response.text();
				setContent(text);
			}
		} catch (err) {
			setError(
				err instanceof Error ? err.message : 'Failed to load document'
			);
		} finally {
			setLoading(false);
		}
	};

	const isTextFile = attachment.content_type.startsWith('text/');
	const fileIcon = emailAPI.getFileIcon(attachment.content_type);
	const fileSize = emailAPI.formatFileSize(attachment.size);

	if (loading) {
		return (
			<div className='flex items-center justify-center h-64'>
				<div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600'></div>
				<span className='ml-2 text-gray-600'>Loading document...</span>
			</div>
		);
	}

	if (error) {
		return (
			<div className='bg-red-50 border border-red-200 rounded-md p-4'>
				<p className='text-red-800'>Error: {error}</p>
				<button
					onClick={loadContent}
					className='mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700'
				>
					Retry
				</button>
			</div>
		);
	}

	return (
		<div className='document-preview'>
			<div className='text-center mb-6'>
				<div className='text-4xl mb-2'>{fileIcon}</div>
				<h4 className='text-lg font-medium text-gray-900'>
					{attachment.filename}
				</h4>
				<p className='text-sm text-gray-600'>
					{attachment.content_type} • {fileSize}
				</p>
			</div>

			{isTextFile && content ? (
				<div className='bg-gray-50 border rounded-lg p-4 max-h-96 overflow-auto'>
					<pre className='text-sm text-gray-800 whitespace-pre-wrap font-mono'>
						{content}
					</pre>
				</div>
			) : (
				<div className='text-center py-8'>
					<div className='text-6xl mb-4'>{fileIcon}</div>
					<p className='text-gray-600 mb-4'>
						This file type cannot be previewed inline.
					</p>
					<p className='text-sm text-gray-500'>
						Click download to view the file with an appropriate
						application.
					</p>
				</div>
			)}

			<div className='mt-6 flex justify-center space-x-4'>
				<a
					href={emailAPI.getAttachmentDownloadUrl(
						emailId,
						attachmentIndex
					)}
					download={attachment.filename}
					className='inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700'
				>
					<svg
						className='w-4 h-4 mr-2'
						fill='none'
						stroke='currentColor'
						viewBox='0 0 24 24'
					>
						<path
							strokeLinecap='round'
							strokeLinejoin='round'
							strokeWidth={2}
							d='M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z'
						/>
					</svg>
					Download File
				</a>

				{isTextFile && (
					<a
						href={emailAPI.getAttachmentViewUrl(
							emailId,
							attachmentIndex
						)}
						target='_blank'
						rel='noopener noreferrer'
						className='inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700'
					>
						<svg
							className='w-4 h-4 mr-2'
							fill='none'
							stroke='currentColor'
							viewBox='0 0 24 24'
						>
							<path
								strokeLinecap='round'
								strokeLinejoin='round'
								strokeWidth={2}
								d='M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14'
							/>
						</svg>
						Open in New Tab
					</a>
				)}
			</div>
		</div>
	);
}
