"""Application constants"""

# Expense categories
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Shopping",
    "Entertainment",
    "Utilities",
    "Healthcare",
    "Personal Care",
    "Education",
    "Travel",
    "Subscriptions",
    "Other",
]

# Confidence thresholds
OCR_CONFIDENCE_THRESHOLD = 0.7
CATEGORIZATION_CONFIDENCE_THRESHOLD = 0.6

# File upload limits
MAX_UPLOAD_SIZE_MB = 10
ALLOWED_IMAGE_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".bmp"]

# API response messages
MESSAGES = {
    "expense_created": "Expense successfully created",
    "expense_deleted": "Expense successfully deleted",
    "expense_not_found": "Expense not found",
    "invalid_image": "Invalid image format or file",
    "ocr_failed": "Failed to extract text from image",
    "categorization_failed": "Failed to categorize expense",
    "database_error": "Database error occurred",
}
