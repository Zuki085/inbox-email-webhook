'use client';

import React, { useState, useEffect } from 'react';
import { emailAPI } from '../lib/api';

interface PDFPreviewProps {
	emailId: string;
	attachmentIndex: number;
	filename: string;
}

export default function PDFPreview({
	emailId,
	attachmentIndex,
	filename,
}: PDFPreviewProps) {
	const [pdfUrl, setPdfUrl] = useState<string | null>(null);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);

	useEffect(() => {
		loadPDF();
	}, [emailId, attachmentIndex]);

	const loadPDF = async () => {
		try {
			setLoading(true);
			setError(null);

			const viewUrl = emailAPI.getAttachmentViewUrl(
				emailId,
				attachmentIndex
			);
			setPdfUrl(viewUrl);
		} catch (err) {
			setError(err instanceof Error ? err.message : 'Failed to load PDF');
		} finally {
			setLoading(false);
		}
	};

	if (loading) {
		return (
			<div className='flex items-center justify-center h-64'>
				<div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600'></div>
				<span className='ml-2 text-gray-600'>Loading PDF...</span>
			</div>
		);
	}

	if (error) {
		return (
			<div className='bg-red-50 border border-red-200 rounded-md p-4'>
				<p className='text-red-800'>Error: {error}</p>
				<button
					onClick={loadPDF}
					className='mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700'
				>
					Retry
				</button>
			</div>
		);
	}

	return (
		<div className='pdf-preview'>
			<div className='text-center mb-4'>
				<h4 className='text-lg font-medium text-gray-900'>
					{filename}
				</h4>
				<p className='text-sm text-gray-600'>PDF Document</p>
			</div>

			<div className='border rounded-lg overflow-hidden'>
				<iframe
					src={pdfUrl || ''}
					className='w-full h-96'
					title={filename}
					onError={() => setError('Failed to load PDF')}
				/>
			</div>

			<div className='mt-4 flex justify-center space-x-4'>
				<a
					href={emailAPI.getAttachmentDownloadUrl(
						emailId,
						attachmentIndex
					)}
					download={filename}
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
					Download PDF
				</a>

				<a
					href={pdfUrl || ''}
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
			</div>
		</div>
	);
}
