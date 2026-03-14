"""Expense API endpoints"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session

from src.database import get_db
from src.services import ExpenseService, ReceiptService
from src.schemas import ExpenseResponse, ExpenseCreate, ExpenseUpdate
from src.utils import get_logger

logger = get_logger("expenses_api")

router = APIRouter(
    prefix="/api/expenses",
    tags=["expenses"],
)


@router.post("/", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    db: Session = Depends(get_db),
):
    """Create a new expense"""
    try:
        service = ExpenseService(db)
        return service.create(expense)
    except Exception as e:
        logger.error(f"Failed to create expense: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """Get expense by ID"""
    try:
        service = ExpenseService(db)
        expense = service.get(expense_id)
        if not expense:
            raise HTTPException(status_code=404, detail="Expense not found")
        return expense
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get expense: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=List[ExpenseResponse])
async def list_expenses(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List all expenses"""
    try:
        service = ExpenseService(db)
        return service.get_all(skip, limit)
    except Exception as e:
        logger.error(f"Failed to list expenses: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: int,
    expense: ExpenseUpdate,
    db: Session = Depends(get_db),
):
    """Update expense"""
    try:
        service = ExpenseService(db)
        updated = service.update(expense_id, expense)
        if not updated:
            raise HTTPException(status_code=404, detail="Expense not found")
        return updated
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update expense: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
):
    """Delete expense"""
    try:
        service = ExpenseService(db)
        success = service.delete(expense_id)
        if not success:
            raise HTTPException(status_code=404, detail="Expense not found")
        return {"message": "Expense deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete expense: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/upload-receipt/")
async def upload_receipt(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload and process receipt"""
    try:
        # Save file
        import tempfile
        from pathlib import Path
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            contents = await file.read()
            tmp.write(contents)
            tmp_path = tmp.name
        
        # Process receipt
        receipt_service = ReceiptService(db)
        expense_service = ExpenseService(db)
        
        result = receipt_service.process_receipt(tmp_path)
        
        if not result.success:
            return {"success": False, "error": result.error}
        
        # Create expense
        expense_data = receipt_service.create_expense_from_receipt(
            tmp_path,
            result.data,
            result.confidence,
        )
        
        expense = expense_service.create(expense_data)
        
        # Cleanup
        Path(tmp_path).unlink()
        
        return {
            "success": True,
            "expense": expense,
            "confidence": result.confidence,
        }
    
    except Exception as e:
        logger.error(f"Failed to process receipt: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
