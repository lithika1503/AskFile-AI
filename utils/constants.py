"""Constants used across AskFile AI."""

# Activity Types
ACTIVITY_UPLOAD = "UPLOAD"
ACTIVITY_PROCESS = "PROCESS"
ACTIVITY_DELETE = "DELETE"
ACTIVITY_CHAT = "CHAT"
ACTIVITY_SEARCH = "SEARCH"
ACTIVITY_SUMMARIZE = "SUMMARIZE"
ACTIVITY_EXTRACT = "EXTRACT"
ACTIVITY_COMPARE = "COMPARE"

# Processing Statuses
STATUS_PENDING = "pending"
STATUS_PROCESSING = "processing"
STATUS_COMPLETED = "completed"
STATUS_FAILED = "failed"

# Message Roles
ROLE_USER = "user"
ROLE_ASSISTANT = "assistant"
ROLE_SYSTEM = "system"

# File types
TYPE_PDF = "pdf"
TYPE_DOCX = "docx"
TYPE_TXT = "txt"

# Standard Error Messages
ERR_FILE_TOO_LARGE = "File exceeds the maximum allowed size of {max_size} MB."
ERR_UNSUPPORTED_TYPE = "Unsupported file type: {ext}. Supported types: PDF, DOCX, TXT."
ERR_DUPLICATE_FILE = "This document has already been uploaded ({filename})."
ERR_EMPTY_FILE = "The uploaded file contains no text or is unreadable."
ERR_SCANNED_PDF = "This PDF appears to be a scanned image with no selectable text. OCR is required."
ERR_NO_DOCUMENTS_SELECTED = "Please select at least one document to proceed."
