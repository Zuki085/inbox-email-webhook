'use client';

import React, { useState, useEffect } from 'react';
import { EmailData, EmailListResponse } from '../types/email';
import { emailAPI } from '../lib/api';
import AttachmentViewer from './AttachmentViewer';

interface EmailListProps {
	userToken?: string;
	className?: string;
}

export default function EmailList({
	userToken,
	className = '',
}: EmailListProps) {
	const [emails, setEmails] = useState<EmailData[]>([]);
	const [loading, setLoading] = useState(true);
	const [error, setError] = useState<string | null>(null);
	const [selectedEmail, setSelectedEmail] = useState<EmailData | null>(null);
	const [pagination, setPagination] = useState({
		limit: 10,
		offset: 0,
		total: 0,
	});

	useEffect(() => {
		loadEmails();
	}, [userToken, pagination.offset]);

	const loadEmails = async () => {
		try {
			setLoading(true);
			setError(null);

			const response = await emailAPI.getEmails(
				pagination.limit,
				pagination.offset,
				userToken
			);

			setEmails(response.emails);
			setPagination(prev => ({
				...prev,
				total: response.total,
			}));
		} catch (err) {
			setError(
				err instanceof Error ? err.message : 'Failed to load emails'
			);
		} finally {
			setLoading(false);
		}
	};

	const handleEmailClick = (email: EmailData) => {
		setSelectedEmail(email);
	};

	const handleCloseEmail = () => {
		setSelectedEmail(null);
	};

	const handleNextPage = () => {
		if (pagination.offset + pagination.limit < pagination.total) {
			setPagination(prev => ({
				...prev,
				offset: prev.offset + prev.limit,
			}));
		}
	};

	const handlePrevPage = () => {
		if (pagination.offset > 0) {
			setPagination(prev => ({
				...prev,
				offset: Math.max(0, prev.offset - prev.limit),
			}));
		}
	};

	const formatDate = (dateString: string) => {
		return new Date(dateString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
			hour: '2-digit',
			minute: '2-digit',
		});
	};

	if (loading && emails.length === 0) {
		return (
			<div className={`email-list ${className}`}>
				<div className='flex items-center justify-center p-8'>
					<div className='animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600'></div>
					<span className='ml-2 text-gray-600'>
						Loading emails...
					</span>
				</div>
			</div>
		);
	}

	if (error) {
		return (
			<div className={`email-list ${className}`}>
				<div className='bg-red-50 border border-red-200 rounded-md p-4'>
					<p className='text-red-800'>Error: {error}</p>
					<button
						onClick={loadEmails}
						className='mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700'
					>
						Retry
					</button>
				</div>
			</div>
		);
	}

	return (
		<div className={`email-list ${className}`}>
			<div className='mb-6'>
				<h2 className='text-2xl font-bold text-gray-900 mb-2'>
					Email Inbox
				</h2>
				<p className='text-gray-600'>
					{pagination.total} total emails • Showing {emails.length}{' '}
					emails
				</p>
			</div>

			<div className='space-y-4'>
				{emails.map(email => (
					<EmailCard
						key={email.id}
						email={email}
						onClick={() => handleEmailClick(email)}
						formatDate={formatDate}
					/>
				))}
			</div>

			{/* Pagination */}
			<div className='mt-6 flex items-center justify-between'>
				<div className='text-sm text-gray-700'>
					Showing {pagination.offset + 1} to{' '}
					{Math.min(
						pagination.offset + pagination.limit,
						pagination.total
					)}{' '}
					of {pagination.total} emails
				</div>

				<div className='flex space-x-2'>
					<button
						onClick={handlePrevPage}
						disabled={pagination.offset === 0}
						className='px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300'
					>
						Previous
					</button>
					<button
						onClick={handleNextPage}
						disabled={
							pagination.offset + pagination.limit >=
							pagination.total
						}
						className='px-3 py-1 bg-gray-200 text-gray-700 rounded disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-300'
					>
						Next
					</button>
				</div>
			</div>

			{/* Email Detail Modal */}
			{selectedEmail && (
				<EmailDetailModal
					email={selectedEmail}
					onClose={handleCloseEmail}
					formatDate={formatDate}
				/>
			)}
		</div>
	);
}

interface EmailCardProps {
	email: EmailData;
	onClick: () => void;
	formatDate: (dateString: string) => string;
}

function EmailCard({ email, onClick, formatDate }: EmailCardProps) {
	return (
		<div
			onClick={onClick}
			className='border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer'
		>
			<div className='flex items-start justify-between'>
				<div className='flex-1 min-w-0'>
					<h3 className='text-lg font-medium text-gray-900 truncate'>
						{email.subject}
					</h3>
					<p className='text-sm text-gray-600 mt-1'>
						From: {email.from_email}
					</p>
					<p className='text-sm text-gray-500 mt-1 line-clamp-2'>
						{email.body}
					</p>
					<div className='flex items-center mt-2 space-x-4 text-xs text-gray-500'>
						<span>{formatDate(email.received_at)}</span>
						{email.has_attachments && (
							<span className='flex items-center'>
								📎 {email.attachment_count} attachment
								{email.attachment_count !== 1 ? 's' : ''}
							</span>
						)}
					</div>
				</div>
				<div className='ml-4 flex-shrink-0'>
					<svg
						className='w-5 h-5 text-gray-400'
						fill='none'
						stroke='currentColor'
						viewBox='0 0 24 24'
					>
						<path
							strokeLinecap='round'
							strokeLinejoin='round'
							strokeWidth={2}
							d='M9 5l7 7-7 7'
						/>
					</svg>
				</div>
			</div>
		</div>
	);
}

interface EmailDetailModalProps {
	email: EmailData;
	onClose: () => void;
	formatDate: (dateString: string) => string;
}

function EmailDetailModal({
	email,
	onClose,
	formatDate,
}: EmailDetailModalProps) {
	return (
		<div className='fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50'>
			<div className='bg-white rounded-lg max-w-4xl max-h-[90vh] w-full mx-4 overflow-hidden'>
				<div className='flex items-center justify-between p-4 border-b'>
					<h2 className='text-xl font-semibold'>{email.subject}</h2>
					<button
						onClick={onClose}
						className='text-gray-400 hover:text-gray-600 text-2xl'
					>
						×
					</button>
				</div>

				<div className='p-6 overflow-auto max-h-[calc(90vh-80px)]'>
					<div className='mb-6'>
						<div className='grid grid-cols-1 md:grid-cols-2 gap-4 text-sm'>
							<div>
								<span className='font-medium text-gray-700'>
									From:
								</span>
								<span className='ml-2 text-gray-900'>
									{email.from_email}
								</span>
							</div>
							<div>
								<span className='font-medium text-gray-700'>
									To:
								</span>
								<span className='ml-2 text-gray-900'>
									{email.to_email}
								</span>
							</div>
							<div>
								<span className='font-medium text-gray-700'>
									Date:
								</span>
								<span className='ml-2 text-gray-900'>
									{formatDate(email.received_at)}
								</span>
							</div>
							<div>
								<span className='font-medium text-gray-700'>
									Message ID:
								</span>
								<span className='ml-2 text-gray-900 font-mono text-xs'>
									{email.message_id}
								</span>
							</div>
						</div>
					</div>

					<div className='mb-6'>
						<h3 className='text-lg font-medium text-gray-900 mb-2'>
							Message
						</h3>
						<div className='bg-gray-50 rounded-lg p-4'>
							{email.html_body ? (
								<div
									dangerouslySetInnerHTML={{
										__html: email.html_body,
									}}
									className='prose max-w-none'
								/>
							) : (
								<pre className='whitespace-pre-wrap text-sm text-gray-800'>
									{email.body}
								</pre>
							)}
						</div>
					</div>

					{email.has_attachments && (
						<div>
							<h3 className='text-lg font-medium text-gray-900 mb-4'>
								Attachments
							</h3>
							<AttachmentViewer emailId={email.id} />
						</div>
					)}
				</div>
			</div>
		</div>
	);
}
