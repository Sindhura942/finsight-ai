"""Expense API endpoints"""

from typing import List

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.services.expense_service import ExpenseService
from app.services import OCRService, LLMService
from app.core.logger import app_logger
from app.core.constants import ALLOWED_IMAGE_EXTENSIONS, MAX_UPLOAD_SIZE_MB

router = APIRouter()


@router.post("/upload", response_model=ExpenseResponse, summary="Upload and process receipt")
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload a receipt image and extract expense information
    
    - **file**: Receipt image file (JPG, PNG, etc.)
    
    Returns:
        ExpenseResponse with extracted expense data
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected",
            )
        
        # Check file extension
        file_ext = "." + file.filename.rsplit(".", 1)[-1].lower()
        if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {ALLOWED_IMAGE_EXTENSIONS}",
            )
        
        # Save uploaded file
        file_path = f"uploads/{file.filename}"
        with open(file_path, "wb") as f:
            content = await file.read()
            
            # Check file size
            file_size_mb = len(content) / (1024 * 1024)
            if file_size_mb > MAX_UPLOAD_SIZE_MB:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds {MAX_UPLOAD_SIZE_MB}MB",
                )
            
            f.write(content)
        
        # Process receipt
        expense_service = ExpenseService(db)
        expense = expense_service.process_receipt_image(file_path)
        
        return expense
    
    except HTTPException:
        raise
    except Exception as e:
        app_logger.error(f"Receipt upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process receipt",
        )


@router.post("/", response_model=ExpenseResponse, summary="Create expense")
async def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
):
    """Create a new expense manually
    
    Returns:
        Created ExpenseResponse
    """
    try:
        expense_service = ExpenseService(db)
        return expense_service.create_expense(expense)
    except Exception as e:
        app_logger.error(f"Failed to create expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create expense",
        )


@router.get("/{expense_id}", response_model=ExpenseResponse, summary="Get expense")
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific expense by ID
    
    Returns:
        ExpenseResponse
    """
    expense_service = ExpenseService(db)
    expense = expense_service.get_expense(expense_id)
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    
    return expense


@router.get("/", response_model=List[ExpenseResponse], summary="Get all expenses")
async def get_all_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """Get all expenses with pagination
    
    - **skip**: Number of records to skip
    - **limit**: Maximum number of records to return
    
    Returns:
        List of ExpenseResponse
    """
    expense_service = ExpenseService(db)
    return expense_service.get_all_expenses(skip, limit)


@router.put("/{expense_id}", response_model=ExpenseResponse, summary="Update expense")
async def update_expense(
    expense_id: int,
    expense_update: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing expense
    
    Returns:
        Updated ExpenseResponse
    """
    expense_service = ExpenseService(db)
    expense = expense_service.update_expense(expense_id, expense_update)
    
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    
    return expense


@router.delete("/{expense_id}", summary="Delete expense")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """Delete an expense
    
    Returns:
        Success message
    """
    expense_service = ExpenseService(db)
    success = expense_service.delete_expense(expense_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense not found",
        )
    
    return {"message": "Expense deleted successfully"}
