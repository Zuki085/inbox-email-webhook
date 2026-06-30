// Email and attachment types for Next.js integration

export interface EmailAttachment {
	index: number;
	filename: string;
	content_type: string;
	size: number;
	file_id: string;
	stored_at: string;
	download_url: string;
	view_url?: string;
}

export interface EmailData {
	id: string;
	subject: string;
	from_email: string;
	to_email: string;
	body: string;
	html_body?: string;
	received_at: string;
	message_id: string;
	user_token: string;
	created_at: string;
	processed: boolean;
	isDeleted: boolean;
	updated_at: string;
	has_attachments: boolean;
	attachment_count: number;
	attachments?: EmailAttachment[];
}

export interface AttachmentInfo {
	email_id: string;
	attachment_index: number;
	filename: string;
	content_type: string;
	size: number;
	file_id: string;
	stored_at: string;
	last_modified: string;
	exists: boolean;
	download_url: string;
}

export interface AttachmentUrls {
	email_id: string;
	attachment_urls: Array<{
		index: number;
		filename: string;
		content_type: string;
		size: number;
		url: string;
		view_url: string;
		download_url: string;
	}>;
	count: number;
}

export interface EmailListResponse {
	emails: EmailData[];
	total: number;
	limit: number;
	offset: number;
}

export interface AttachmentListResponse {
	attachments: EmailAttachment[];
	count: number;
	email_id: string;
	message?: string;
}
