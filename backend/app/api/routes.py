"""
FinSight AI - FastAPI Routes Module

This module contains all API endpoints for the FinSight AI application.
Endpoints are organized by functionality:
- Receipt Upload & Analysis
- Expense Management
- Spending Insights
- Monthly Analytics
"""

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.database.session import get_db
from app.models import ExpenseResponse, SpendingSummary
from app.services.expense_service import ExpenseService
from app.services.insight_service import InsightService
from app.core.logger import app_logger

# Create main router
router = APIRouter(prefix="/api", tags=["api"])

# ============================================================================
# 1. RECEIPT UPLOAD & ANALYSIS ENDPOINTS
# ============================================================================

@router.post("/upload-receipt", 
    response_model=dict,
    summary="Upload receipt image and run full analysis",
    status_code=201,
    tags=["receipts"])
async def upload_receipt(
    file: UploadFile = File(..., description="Receipt image file (JPG, PNG, etc.)"),
    db: Session = Depends(get_db)
):
    """
    Upload a receipt image and run complete analysis.
    
    This endpoint:
    1. Receives the receipt image file
    2. Performs OCR to extract text
    3. Uses LLM to parse expense details (merchant, category, amount, date)
    4. Stores the expense in the database
    5. Returns the extracted and stored expense
    
    **Request:**
    - file: Receipt image file (multipart/form-data)
    
    **Response (201 Created):**
    ```json
    {
        "success": true,
        "message": "Receipt analyzed and stored successfully",
        "expense": {
            "id": 1,
            "date": "2024-03-13",
            "merchant": "Starbucks",
            "category": "food & dining",
            "amount": 6.50,
            "description": "Coffee",
            "source": "receipt_upload",
            "created_at": "2024-03-13T10:30:00Z"
        },
        "confidence": 0.95,
        "extraction_details": {
            "merchant_confidence": 0.98,
            "amount_confidence": 0.99,
            "category_confidence": 0.90
        }
    }
    ```
    
    **Errors:**
    - 400: Invalid file format or no file provided
    - 413: File too large (max 10MB)
    - 422: Failed to process image
    - 500: Server error during processing
    
    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/upload-receipt" \\
        -H "Content-Type: multipart/form-data" \\
        -F "file=@receipt.jpg"
    ```
    """
    try:
        if not file.filename:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No file selected"
            )
        
        # Validate file extension
        allowed_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
        file_ext = "." + file.filename.rsplit(".", 1)[-1].lower()
        
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Read and process file
        contents = await file.read()
        
        if len(contents) > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large. Maximum size is 10MB"
            )
        
        # Process with expense service
        expense_service = ExpenseService(db)
        result = expense_service.process_receipt_image(contents, file.filename)
        
        app_logger.info(f"Receipt processed successfully: {file.filename}")
        
        return {
            "success": True,
            "message": "Receipt analyzed and stored successfully",
            "expense": result.get("expense"),
            "confidence": result.get("confidence", 0),
            "extraction_details": result.get("extraction_details", {})
        }
    
    except HTTPException as e:
        app_logger.error(f"HTTP Error in upload_receipt: {e.detail}")
        raise
    except Exception as e:
        app_logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process receipt image"
        )


# ============================================================================
# 2. EXPENSE MANAGEMENT ENDPOINTS
# ============================================================================

@router.post("/add-expense",
    response_model=dict,
    summary="Add expense via text input",
    status_code=201,
    tags=["expenses"])
async def add_expense(
    date: str = Query(..., description="Expense date (YYYY-MM-DD format)"),
    merchant: str = Query(..., description="Vendor/store name"),
    category: str = Query(..., description="Expense category (e.g., 'food', 'transportation')"),
    amount: float = Query(..., gt=0, description="Amount spent (must be > 0)"),
    description: Optional[str] = Query(None, description="Optional expense description/notes"),
    db: Session = Depends(get_db)
):
    """
    Add a new expense via text input (manual entry).
    
    This endpoint allows users to manually enter expense details without uploading a receipt.
    
    **Query Parameters:**
    - date: Date of expense in YYYY-MM-DD format (required)
    - merchant: Name of the vendor/store (required)
    - category: Expense category like 'food', 'transportation', 'shopping' (required)
    - amount: Amount spent, must be positive number (required)
    - description: Optional notes or description (optional)
    
    **Response (201 Created):**
    ```json
    {
        "success": true,
        "message": "Expense added successfully",
        "expense": {
            "id": 1,
            "date": "2024-03-13",
            "merchant": "Starbucks",
            "category": "food & dining",
            "amount": 6.50,
            "description": "Morning coffee",
            "source": "manual_entry",
            "created_at": "2024-03-13T10:30:00Z"
        }
    }
    ```
    
    **Errors:**
    - 400: Invalid data (invalid date format, negative amount, etc.)
    - 422: Validation error
    - 500: Server error
    
    **Examples:**
    ```bash
    # Basic expense
    curl -X POST "http://localhost:8000/api/add-expense" \\
        -H "Content-Type: application/x-www-form-urlencoded" \\
        -d "date=2024-03-13&merchant=Starbucks&category=food&amount=6.50"
    
    # With description
    curl -X POST "http://localhost:8000/api/add-expense" \\
        -d "date=2024-03-13&merchant=Whole Foods&category=groceries&amount=75.50&description=Weekly groceries"
    ```
    """
    try:
        # Validate date format
        try:
            expense_date = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use YYYY-MM-DD (e.g., 2024-03-13)"
            )
        
        # Validate amount
        if amount <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Amount must be greater than 0"
            )
        
        # Validate required fields
        if not merchant or not merchant.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Merchant name is required"
            )
        
        if not category or not category.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category is required"
            )
        
        # Add expense to database
        expense_service = ExpenseService(db)
        expense = expense_service.create_expense(
            date=expense_date,
            merchant=merchant.strip(),
            category=category.strip(),
            amount=amount,
            description=description.strip() if description else None,
            source="manual_entry"
        )
        
        app_logger.info(f"Expense added: {merchant} - ${amount} on {date}")
        
        return {
            "success": True,
            "message": "Expense added successfully",
            "expense": {
                "id": expense.id,
                "date": expense.date.isoformat(),
                "merchant": expense.merchant,
                "category": expense.category,
                "amount": expense.amount,
                "description": expense.description,
                "source": "manual_entry",
                "created_at": expense.created_at.isoformat()
            }
        }
    
    except HTTPException as e:
        raise
    except Exception as e:
        app_logger.error(f"Error adding expense: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to add expense"
        )


@router.get("/expenses",
    response_model=dict,
    summary="Get all expenses",
    tags=["expenses"])
async def get_expenses(
    days: int = Query(30, ge=1, le=365, description="Number of days to retrieve (1-365)"),
    category: Optional[str] = Query(None, description="Filter by category (optional)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve all expenses for the specified period.
    
    Optionally filter by category.
    
    **Query Parameters:**
    - days: Number of recent days to include (default: 30)
    - category: Optional category filter (e.g., 'food', 'transportation')
    
    **Response:**
    ```json
    {
        "success": true,
        "count": 15,
        "total_amount": 250.50,
        "period": {
            "from": "2024-02-13",
            "to": "2024-03-13"
        },
        "expenses": [
            {
                "id": 1,
                "date": "2024-03-13",
                "merchant": "Starbucks",
                "category": "food & dining",
                "amount": 6.50,
                "description": "Coffee",
                "source": "receipt_upload"
            }
        ]
    }
    ```
    
    **Examples:**
    ```bash
    # Last 30 days (default)
    curl "http://localhost:8000/api/expenses"
    
    # Last 90 days
    curl "http://localhost:8000/api/expenses?days=90"
    
    # Filter by category
    curl "http://localhost:8000/api/expenses?days=30&category=food"
    ```
    """
    try:
        expense_service = ExpenseService(db)
        expenses = expense_service.get_expenses(days=days, category=category)
        
        total_amount = sum(e.amount for e in expenses) if expenses else 0
        start_date = (datetime.now() - timedelta(days=days)).date()
        end_date = datetime.now().date()
        
        return {
            "success": True,
            "count": len(expenses),
            "total_amount": round(total_amount, 2),
            "period": {
                "from": start_date.isoformat(),
                "to": end_date.isoformat()
            },
            "expenses": [
                {
                    "id": e.id,
                    "date": e.date.isoformat(),
                    "merchant": e.merchant,
                    "category": e.category,
                    "amount": e.amount,
                    "description": e.description,
                    "source": e.source
                } for e in expenses
            ]
        }
    
    except Exception as e:
        app_logger.error(f"Error retrieving expenses: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve expenses"
        )


# ============================================================================
# 3. SPENDING SUMMARY ENDPOINTS
# ============================================================================

@router.get("/spending-summary",
    response_model=dict,
    summary="Return categorized expenses and insights",
    tags=["insights"])
async def get_spending_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive spending summary with categorized breakdown and insights.
    
    This endpoint provides:
    - Total spending amount
    - Breakdown by category with amounts and percentages
    - Average daily spending
    - Highest spending category
    - Spending trends
    
    **Query Parameters:**
    - days: Number of recent days to analyze (1-365, default: 30)
    
    **Response:**
    ```json
    {
        "success": true,
        "period_days": 30,
        "summary": {
            "total_spending": 250.50,
            "average_daily_spending": 8.35,
            "transaction_count": 15,
            "highest_category": "food & dining",
            "date_range": {
                "from": "2024-02-13",
                "to": "2024-03-13"
            }
        },
        "by_category": [
            {
                "category": "food & dining",
                "total": 150.00,
                "percentage": 59.8,
                "transaction_count": 10,
                "average_per_transaction": 15.00,
                "last_transaction": "2024-03-13"
            },
            {
                "category": "transportation",
                "total": 50.00,
                "percentage": 20.0,
                "transaction_count": 2,
                "average_per_transaction": 25.00,
                "last_transaction": "2024-03-12"
            }
        ],
        "insights": [
            "Food & dining is your top spending category (59.8%)",
            "You spent an average of $8.35 per day",
            "Transportation spending increased 20% vs previous period"
        ]
    }
    ```
    
    **Examples:**
    ```bash
    # Last 30 days summary
    curl "http://localhost:8000/api/spending-summary"
    
    # 90-day analysis
    curl "http://localhost:8000/api/spending-summary?days=90"
    
    # Full year analysis
    curl "http://localhost:8000/api/spending-summary?days=365"
    ```
    """
    try:
        insight_service = InsightService(db)
        summary = insight_service.get_spending_summary(days=days)
        
        # Handle both SpendingSummary object and dict returns
        if hasattr(summary, 'total_spending'):
            # It's a SpendingSummary object
            return {
                "success": True,
                "period_days": days,
                "data": {
                    "summary": {
                        "total_spending": summary.total_spending,
                        "average_daily_spending": summary.total_spending / days if days > 0 else 0,
                        "transaction_count": summary.transaction_count,
                        "highest_category": summary.highest_category,
                        "period": summary.period
                    },
                    "by_category": [
                        {
                            "category": cat.category,
                            "total": cat.total_amount,
                            "percentage": cat.percentage_of_total,
                            "transaction_count": cat.transaction_count
                        } for cat in (summary.categories or [])
                    ],
                    "insights": []
                }
            }
        else:
            # It's a dict
            return {
                "success": True,
                "period_days": days,
                "data": {
                    "summary": summary.get("total_summary", {}),
                    "by_category": summary.get("by_category", []),
                    "insights": summary.get("insights", [])
                }
            }
    
    except Exception as e:
        app_logger.error(f"Error getting spending summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate spending summary"
        )


@router.get("/category-breakdown",
    response_model=dict,
    summary="Get detailed breakdown by category",
    tags=["insights"])
async def get_category_breakdown(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed spending breakdown by category with transaction details.
    
    **Query Parameters:**
    - days: Number of recent days to analyze (1-365, default: 30)
    
    **Response:**
    ```json
    {
        "success": true,
        "period_days": 30,
        "categories": [
            {
                "category": "food & dining",
                "total": 150.00,
                "percentage": 59.8,
                "transaction_count": 10,
                "average_per_transaction": 15.00,
                "min_transaction": 5.50,
                "max_transaction": 45.00,
                "last_transaction": "2024-03-13",
                "transactions": [
                    {
                        "date": "2024-03-13",
                        "merchant": "Starbucks",
                        "amount": 6.50
                    }
                ]
            }
        ]
    }
    ```
    
    **Examples:**
    ```bash
    curl "http://localhost:8000/api/category-breakdown?days=30"
    ```
    """
    try:
        insight_service = InsightService(db)
        breakdown = insight_service.get_category_breakdown(days=days)
        
        return {
            "success": True,
            "period_days": days,
            "categories": breakdown.get("categories", [])
        }
    
    except Exception as e:
        app_logger.error(f"Error getting category breakdown: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate category breakdown"
        )


# ============================================================================
# 4. MONTHLY INSIGHTS ENDPOINTS
# ============================================================================

@router.get("/monthly-insights",
    response_model=dict,
    summary="Return spending trends and recommendations",
    tags=["insights"])
async def get_monthly_insights(
    months: int = Query(3, ge=1, le=12, description="Number of months to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed monthly spending trends and AI-powered recommendations.
    
    This endpoint provides:
    - Monthly spending data over time
    - Spending trends and patterns
    - Month-over-month comparisons
    - AI-generated cost-saving recommendations
    - Budget alerts and warnings
    
    **Query Parameters:**
    - months: Number of recent months to analyze (1-12, default: 3)
    
    **Response:**
    ```json
    {
        "success": true,
        "analysis_period": "3 months",
        "monthly_data": [
            {
                "month": "2024-01",
                "total_spending": 850.00,
                "transaction_count": 35,
                "average_daily": 27.42,
                "vs_previous_month": {
                    "change_amount": 50.00,
                    "change_percentage": 6.3,
                    "direction": "up"
                },
                "top_categories": [
                    {
                        "category": "food & dining",
                        "amount": 350.00,
                        "percentage": 41.2
                    }
                ]
            }
        ],
        "trends": {
            "overall_trend": "increasing",
            "trend_description": "Your spending is increasing. Last month was 6.3% higher than the previous month.",
            "fastest_growing_category": "transportation",
            "most_consistent_category": "food & dining",
            "spending_stability": 0.85
        },
        "recommendations": [
            {
                "priority": "high",
                "category": "food & dining",
                "suggestion": "Consider meal planning to reduce food spending. You spent $350 in the past month.",
                "potential_savings": 50.00,
                "savings_percentage": 14.3
            },
            {
                "priority": "medium",
                "category": "transportation",
                "suggestion": "Your transportation costs increased significantly. Explore carpooling or public transit options.",
                "potential_savings": 25.00,
                "savings_percentage": 12.5
            }
        ],
        "budget_alerts": [
            {
                "category": "food & dining",
                "suggested_budget": 300.00,
                "current_spending": 350.00,
                "status": "over_budget",
                "excess_amount": 50.00
            }
        ]
    }
    ```
    
    **Examples:**
    ```bash
    # Last 3 months (default)
    curl "http://localhost:8000/api/monthly-insights"
    
    # Last 6 months
    curl "http://localhost:8000/api/monthly-insights?months=6"
    
    # Full year analysis
    curl "http://localhost:8000/api/monthly-insights?months=12"
    ```
    """
    try:
        insight_service = InsightService(db)
        insights = insight_service.get_monthly_insights(months=months)
        
        return {
            "success": True,
            "analysis_period": f"{months} month{'s' if months > 1 else ''}",
            "monthly_data": insights.get("monthly_data", []),
            "trends": insights.get("trends", {}),
            "recommendations": insights.get("recommendations", []),
            "budget_alerts": insights.get("budget_alerts", [])
        }
    
    except Exception as e:
        app_logger.error(f"Error getting monthly insights: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate monthly insights"
        )


@router.get("/spending-trends",
    response_model=dict,
    summary="Get detailed spending trends",
    tags=["insights"])
async def get_spending_trends(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    db: Session = Depends(get_db)
):
    """
    Get detailed daily/weekly spending trends over time.
    
    **Query Parameters:**
    - days: Number of recent days to analyze (1-365, default: 30)
    
    **Response:**
    ```json
    {
        "success": true,
        "period_days": 30,
        "daily_trends": [
            {
                "date": "2024-03-13",
                "total": 25.50,
                "transaction_count": 3,
                "categories": {
                    "food & dining": 15.50,
                    "transportation": 10.00
                }
            }
        ],
        "weekly_summary": [
            {
                "week": "2024-W11",
                "total": 180.00,
                "average_daily": 25.71,
                "transaction_count": 20
            }
        ]
    }
    ```
    
    **Examples:**
    ```bash
    curl "http://localhost:8000/api/spending-trends?days=30"
    ```
    """
    try:
        insight_service = InsightService(db)
        trends = insight_service.get_spending_trends(days=days)
        
        return {
            "success": True,
            "period_days": days,
            "daily_trends": trends.get("daily_trends", []),
            "weekly_summary": trends.get("weekly_summary", [])
        }
    
    except Exception as e:
        app_logger.error(f"Error getting spending trends: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate spending trends"
        )


@router.get("/recommendations",
    response_model=dict,
    summary="Get cost-saving recommendations",
    tags=["insights"])
async def get_recommendations(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    category: Optional[str] = Query(None, description="Specific category (optional)"),
    db: Session = Depends(get_db)
):
    """
    Get AI-powered cost-saving recommendations based on spending patterns.
    
    **Query Parameters:**
    - days: Number of recent days to analyze (1-365, default: 30)
    - category: Optional category filter (optional)
    
    **Response:**
    ```json
    {
        "success": true,
        "period_days": 30,
        "recommendations": [
            {
                "id": "rec_001",
                "priority": "high",
                "category": "food & dining",
                "current_spending": 150.00,
                "suggested_budget": 120.00,
                "potential_savings": 30.00,
                "savings_percentage": 20.0,
                "suggestion": "You're spending more on food than average. Consider meal planning and cooking at home.",
                "actions": [
                    "Set a weekly food budget",
                    "Plan meals for the week",
                    "Cook at home instead of eating out"
                ]
            }
        ],
        "summary": {
            "total_potential_savings": 105.00,
            "high_priority_count": 2,
            "medium_priority_count": 1,
            "low_priority_count": 0
        }
    }
    ```
    
    **Examples:**
    ```bash
    curl "http://localhost:8000/api/recommendations"
    curl "http://localhost:8000/api/recommendations?days=90&category=food"
    ```
    """
    try:
        insight_service = InsightService(db)
        recommendations = insight_service.get_recommendations(days=days, category=category)
        
        return {
            "success": True,
            "period_days": days,
            "recommendations": recommendations.get("recommendations", []),
            "summary": recommendations.get("summary", {})
        }
    
    except Exception as e:
        app_logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate recommendations"
        )


# ============================================================================
# 5. HEALTH & STATUS ENDPOINTS
# ============================================================================

@router.get("/health",
    response_model=dict,
    summary="Health check endpoint",
    tags=["system"])
async def health_check():
    """
    Check if the API is running and healthy.
    
    **Response:**
    ```json
    {
        "status": "healthy",
        "timestamp": "2024-03-13T10:30:00Z",
        "version": "1.0.0"
    }
    ```
    
    **Examples:**
    ```bash
    curl "http://localhost:8000/api/health"
    ```
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/stats",
    response_model=dict,
    summary="Get system statistics",
    tags=["system"])
async def get_stats(db: Session = Depends(get_db)):
    """
    Get overall system statistics.
    
    **Response:**
    ```json
    {
        "success": true,
        "stats": {
            "total_expenses": 150,
            "total_amount": 2500.50,
            "categories_tracked": 8,
            "data_since": "2024-01-01",
            "last_update": "2024-03-13T10:30:00Z"
        }
    }
    ```
    """
    try:
        expense_service = ExpenseService(db)
        stats = expense_service.get_stats()
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        app_logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve statistics"
        )
