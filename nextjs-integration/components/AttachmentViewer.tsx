'use client';

import React, { useState, useEffect } from 'react';
import { EmailAttachment } from '../types/email';
import { emailAPI } from '../lib/api';
import ImagePreview from './ImagePreview';
import PDFPreview from './PDFPreview';
import DocumentPreview from './DocumentPreview';

interface AttachmentViewerProps {
	emailId: string;
	className?: string;
}

export default function AttachmentViewer({
	emailId,
	className = '',
}: AttachmentViewerProps) {
	const [attachments, setAttachments] = useState<EmailAttachment[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [selectedAttachment, setSelectedAttachment] =
		useState<EmailAttachment | null>(null);

	useEffect(() => {
		loadAttachments();
	}, [emailId]);

	const loadAttachments = async () => {
		try {
			setLoading(true);
			setError(null);
			const response = await emailAPI.getEmailAttachments(emailId);
			setAttachments(response.attachments);
		} catch (err) {
			setError(
				err instanceof Error
					? err.message
					: 'Failed to load attachments'
			);
		} finally {
			setLoading(false);
		}
	};

	const handleAttachmentClick = (attachment: EmailAttachment) => {
		setSelectedAttachment(attachment);
	};

	const handleClosePreview = () => {
		setSelectedAttachment(null);
	};

	const handleDownload = async (attachment: EmailAttachment) => {
		try {
			const url = emailAPI.getAttachmentDownloadUrl(
				emailId,
				attachment.index
			);
			const response = await fetch(url);

			if (!response.ok) {
				throw new Error('Download failed');
			}

			const blob = await response.blob();
			const downloadUrl = window.URL.createObjectURL(blob);
			const link = document.createElement('a');
			link.href = downloadUrl;
			link.download = attachment.filename;
			document.body.appendChild(link);
			link.click();
			document.body.removeChild(link);
			window.URL.revokeObjectURL(downloadUrl);
		} catch (err) {
			console.error('Download error:', err);
			alert('Failed to download file');
		}
	};

	if (loading) {
		return (
			<div className={`attachment-viewer ${className}`}>
				<div className='flex items-center justify-center p-4'>
					<div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600'></div>
					<span className='ml-2 text-gray-600'>
						Loading attachments...
					</span>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className={`attachment-viewer ${className}`}>
				<div className='bg-red-50 border border-red-200 rounded-md p-4'>
					<p className='text-red-800'>Error: {error}</p>
					<button
						onClick={loadAttachments}
						className='mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700'
					>
						Retry
					</button>
				</div>
			</div>
		);
	}

	if (attachments.length === 0) {
		return (
			<div className={`attachment-viewer ${className}`}>
				<div className='text-center text-gray-500 py-8'>
					<p>No attachments found for this email.</p>
				</div>
			</div>
		);
	}

	return (
		<div className={`attachment-viewer ${className}`}>
			<div className='mb-4'>
				<h3 className='text-lg font-semibold text-gray-900 mb-2'>
					Attachments ({attachments.length})
				</h3>
			</div>

			<div className='grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4'>
				{attachments.map(attachment => (
					<AttachmentCard
						key={attachment.index}
						attachment={attachment}
						onPreview={handleAttachmentClick}
						onDownload={handleDownload}
					/>
				))}
			</div>

			{selectedAttachment && (
				<AttachmentModal
					attachment={selectedAttachment}
					emailId={emailId}
					onClose={handleClosePreview}
				/>
			)}
		</div>
	);
}

interface AttachmentCardProps {
	attachment: EmailAttachment;
	onPreview: (attachment: EmailAttachment) => void;
	onDownload: (attachment: EmailAttachment) => void;
}

function AttachmentCard({
	attachment,
	onPreview,
	onDownload,
}: AttachmentCardProps) {
	const fileIcon = emailAPI.getFileIcon(attachment.content_type);
	const fileSize = emailAPI.formatFileSize(attachment.size);
	const isPreviewable = emailAPI.isPreviewable(attachment.content_type);

	return (
		<div className='border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow'>
			<div className='flex items-start space-x-3'>
				<div className='text-2xl'>{fileIcon}</div>
				<div className='flex-1 min-w-0'>
					<h4 className='text-sm font-medium text-gray-900 truncate'>
						{attachment.filename}
					</h4>
					<p className='text-xs text-gray-500 mt-1'>
						{fileSize} • {attachment.content_type}
					</p>
					<div className='flex space-x-2 mt-3'>
						{isPreviewable && (
							<button
								onClick={() => onPreview(attachment)}
								className='text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded hover:bg-blue-200'
							>
								Preview
							</button>
						)}
						<button
							onClick={() => onDownload(attachment)}
							className='text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded hover:bg-gray-200'
						>
							Download
						</button>
					</div>
				</div>
			</div>
		</div>
	);
}

interface AttachmentModalProps {
	attachment: EmailAttachment;
	emailId: string;
	onClose: () => void;
}

function AttachmentModal({
	attachment,
	emailId,
	onClose,
}: AttachmentModalProps) {
	const isImage = attachment.content_type.startsWith('image/');
	const isPDF = attachment.content_type === 'application/pdf';

	return (
		<div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
			<div className='bg-white rounded-lg max-w-4xl max-h-[90vh] w-full mx-4 overflow-hidden'>
				<div className='flex items-center justify-between p-4 border-b'>
					<h3 className='text-lg font-semibold truncate'>
						{attachment.filename}
					</h3>
					<button
						onClick={onClose}
						className='text-gray-400 hover:text-gray-600 text-2xl'
					>
						×
					</button>
				</div>

				<div className='p-4 overflow-auto max-h-[calc(90vh-80px)]'>
					{isImage && (
						<ImagePreview
							emailId={emailId}
							attachmentIndex={attachment.index}
							filename={attachment.filename}
						/>
					)}
					{isPDF && (
						<PDFPreview
							emailId={emailId}
							attachmentIndex={attachment.index}
							filename={attachment.filename}
						/>
					)}
					{!isImage && !isPDF && (
						<DocumentPreview
							emailId={emailId}
							attachmentIndex={attachment.index}
							attachment={attachment}
						/>
					)}
				</div>
			</div>
		</div>
	);
}
