"""
FinSight AI LangGraph Workflow

Main workflow orchestrating the complete expense processing pipeline:
1. OCR Extraction - Extract text from images or accept text input
2. Expense Extraction - Parse text into structured expense items
3. Categorization - Assign categories to expenses
4. Database Storage - Store results persistently
5. Financial Analysis - Analyze spending patterns
6. Recommendations - Generate cost-saving recommendations
"""

import logging
import time
import sqlite3
import json
from typing import Dict, Any, Optional
from datetime import datetime

from langgraph.graph import StateGraph, END

from src.ocr.processor import OCRExtractor
from src.ocr.receipt_parser import ReceiptParser
from src.agents import ExpenseCategorizer, FinancialAnalyzer
from src.workflows.state import (
    WorkflowState,
    ExpenseItem,
    Recommendation,
    AnalysisResult,
    CategoryBreakdown
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FinSightWorkflow:
    """
    LangGraph-based workflow for FinSight AI.
    
    Orchestrates the complete pipeline from receipt input to recommendations.
    """
    
    def __init__(self, use_llm: bool = False, db_path: str = "finsight.db"):
        """
        Initialize the workflow.
        
        Args:
            use_llm: Whether to use LLM for categorization and analysis
            db_path: Path to SQLite database file
        """
        self.use_llm = use_llm
        self.db_path = db_path
        
        # Initialize modules
        self.ocr = OCRExtractor()
        self.parser = ReceiptParser(use_llm=use_llm)
        self.categorizer = ExpenseCategorizer(use_llm=use_llm)
        self.analyzer = FinancialAnalyzer(use_llm=use_llm)
        
        # Initialize database
        self._init_database()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _init_database(self):
        """Initialize SQLite database tables."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Receipts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS receipts (
                    id TEXT PRIMARY KEY,
                    created_at TIMESTAMP,
                    raw_text TEXT,
                    input_type TEXT
                )
            """)
            
            # Expenses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS expenses (
                    id TEXT PRIMARY KEY,
                    receipt_id TEXT,
                    merchant TEXT,
                    amount REAL,
                    category TEXT,
                    confidence REAL,
                    created_at TIMESTAMP,
                    FOREIGN KEY (receipt_id) REFERENCES receipts(id)
                )
            """)
            
            # Analysis table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analyses (
                    id TEXT PRIMARY KEY,
                    receipt_id TEXT,
                    analysis_json TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (receipt_id) REFERENCES receipts(id)
                )
            """)
            
            conn.commit()
            conn.close()
            logger.info(f"Database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow graph."""
        graph = StateGraph(WorkflowState)
        
        # Add nodes
        graph.add_node("ocr", self._ocr_node)
        graph.add_node("extraction", self._extraction_node)
        graph.add_node("categorization", self._categorization_node)
        graph.add_node("storage", self._storage_node)
        graph.add_node("analysis", self._analysis_node)
        graph.add_node("recommendations", self._recommendations_node)
        
        # Add edges (sequential flow)
        graph.add_edge("ocr", "extraction")
        graph.add_edge("extraction", "categorization")
        graph.add_edge("categorization", "storage")
        graph.add_edge("storage", "analysis")
        graph.add_edge("analysis", "recommendations")
        graph.add_edge("recommendations", END)
        
        # Set entry point
        graph.set_entry_point("ocr")
        
        logger.info("LangGraph workflow built successfully")
        return graph.compile()
    
    def _ocr_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 1: OCR Extraction
        
        Extracts text from image or uses provided text.
        
        Input: input_type, input_content
        Output: extracted_text, ocr_confidence, ocr_error
        """
        logger.info(f"OCR Node: Processing {state.input_type} input")
        
        try:
            start_time = time.time()
            
            if state.input_type == "image":
                # Extract text from image file
                logger.info(f"Extracting text from image: {state.input_content}")
                state.extracted_text = self.ocr.extract(state.input_content)
                state.ocr_confidence = 0.85  # OCR confidence estimate
                
            elif state.input_type == "text":
                # Use provided text directly
                logger.info("Using provided text input")
                state.extracted_text = state.input_content
                state.ocr_confidence = 1.0  # Perfect confidence for text input
                
            else:
                raise ValueError(f"Unknown input type: {state.input_type}")
            
            if not state.extracted_text or not state.extracted_text.strip():
                state.ocr_error = "No text extracted from input"
                logger.warning("OCR produced empty output")
            else:
                logger.info(f"OCR extracted {len(state.extracted_text)} characters")
        
        except Exception as e:
            state.ocr_error = str(e)
            logger.error(f"OCR Error: {e}")
        
        return state
    
    def _extraction_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 2: Expense Extraction
        
        Parses extracted text into structured expense items.
        
        Input: extracted_text
        Output: raw_items, extraction_error
        """
        logger.info("Extraction Node: Parsing expenses from text")
        
        try:
            if not state.extracted_text:
                state.extraction_error = "No text to extract expenses from"
                return state
            
            # Parse the text
            logger.info(f"Parsing receipt text ({len(state.extracted_text)} chars)")
            parsed_items = self.parser.parse(state.extracted_text)
            
            # Convert to WorkflowState ExpenseItem objects
            state.raw_items = [
                ExpenseItem(
                    merchant=item.get("merchant", "Unknown"),
                    amount=float(item.get("amount", 0.0)),
                    description=item.get("description"),
                    confidence=item.get("confidence", 0.0)
                )
                for item in parsed_items
            ]
            
            logger.info(f"Extracted {len(state.raw_items)} expense items")
        
        except Exception as e:
            state.extraction_error = str(e)
            logger.error(f"Extraction Error: {e}")
        
        return state
    
    def _categorization_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 3: Categorization
        
        Assigns categories to expense items using AI or keywords.
        
        Input: raw_items
        Output: categorized_expenses, categorization_error
        """
        logger.info("Categorization Node: Assigning categories to expenses")
        
        try:
            if not state.raw_items:
                state.categorization_error = "No items to categorize"
                return state
            
            # Prepare items for categorization
            items_for_categorization = [item.to_dict() for item in state.raw_items]
            
            logger.info(f"Categorizing {len(items_for_categorization)} items")
            
            # Categorize using the categorizer agent
            categorized = self.categorizer.categorize(items_for_categorization)
            
            # Update raw items with categories
            state.categorized_expenses = []
            for i, expense in enumerate(categorized):
                item = state.raw_items[i] if i < len(state.raw_items) else None
                if item:
                    item.category = expense.get("category", "other")
                    item.confidence = expense.get("confidence", 0.0)
                    state.categorized_expenses.append(item)
            
            logger.info(f"Categorized {len(state.categorized_expenses)} expenses")
        
        except Exception as e:
            state.categorization_error = str(e)
            logger.error(f"Categorization Error: {e}")
        
        return state
    
    def _storage_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 4: Database Storage
        
        Stores receipt and expense data in SQLite database.
        
        Input: extracted_text, categorized_expenses
        Output: storage_id, storage_error
        """
        logger.info("Storage Node: Saving to database")
        
        try:
            if not state.categorized_expenses:
                logger.warning("No expenses to store")
                return state
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Generate IDs
            workflow_id = state.workflow_id
            receipt_id = f"receipt_{workflow_id}"
            
            # Insert receipt
            cursor.execute(
                """INSERT INTO receipts (id, created_at, raw_text, input_type)
                   VALUES (?, ?, ?, ?)""",
                (receipt_id, datetime.now(), state.extracted_text, state.input_type)
            )
            logger.info(f"Stored receipt: {receipt_id}")
            
            # Insert expenses
            for i, expense in enumerate(state.categorized_expenses):
                expense_id = f"expense_{workflow_id}_{i}"
                cursor.execute(
                    """INSERT INTO expenses (id, receipt_id, merchant, amount, category, confidence, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (expense_id, receipt_id, expense.merchant, expense.amount, 
                     expense.category, expense.confidence, datetime.now())
                )
            
            conn.commit()
            logger.info(f"Stored {len(state.categorized_expenses)} expenses")
            
            state.storage_id = receipt_id
            conn.close()
        
        except Exception as e:
            state.storage_error = str(e)
            logger.error(f"Storage Error: {e}")
        
        return state
    
    def _analysis_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 5: Financial Analysis
        
        Analyzes spending patterns and generates statistics.
        
        Input: categorized_expenses
        Output: analysis, analysis_error
        """
        logger.info("Analysis Node: Analyzing spending patterns")
        
        try:
            if not state.categorized_expenses:
                state.analysis_error = "No expenses to analyze"
                return state
            
            # Convert to format expected by analyzer
            expenses_dict = [item.to_dict() for item in state.categorized_expenses]
            
            logger.info(f"Analyzing {len(expenses_dict)} expenses")
            
            # Run analysis
            analysis_result = self.analyzer.analyze(
                expenses_dict,
                budget_limits=state.budget_limits
            )
            
            # Convert to WorkflowState AnalysisResult
            state.analysis = AnalysisResult(
                total_spending=analysis_result.total_spending,
                currency=analysis_result.currency,
                category_breakdown=[
                    CategoryBreakdown(
                        category=cat.category,
                        amount=cat.amount,
                        count=cat.count,
                        average=cat.average,
                        percentage=cat.percentage
                    )
                    for cat in analysis_result.category_breakdown
                ],
                highest_spending_category=analysis_result.highest_spending_category,
                highest_spending_amount=analysis_result.highest_spending_amount,
                expense_count=analysis_result.expense_count,
                summary=analysis_result.summary
            )
            
            logger.info(f"Analysis complete: ${state.analysis.total_spending:.2f} total")
        
        except Exception as e:
            state.analysis_error = str(e)
            logger.error(f"Analysis Error: {e}")
        
        return state
    
    def _recommendations_node(self, state: WorkflowState) -> WorkflowState:
        """
        Node 6: Recommendations
        
        Generates cost-saving recommendations based on analysis.
        
        Input: analysis
        Output: recommendations, recommendation_error
        """
        logger.info("Recommendations Node: Generating recommendations")
        
        try:
            if not state.analysis:
                state.recommendation_error = "No analysis available for recommendations"
                return state
            
            # Extract recommendations from analysis
            state.recommendations = [
                Recommendation(
                    title=rec.title,
                    description=rec.description,
                    category=rec.category,
                    potential_savings=rec.potential_savings,
                    priority=rec.priority,
                    actionable_steps=rec.actionable_steps,
                    confidence=rec.confidence
                )
                for rec in state.analysis.recommendations
            ]
            
            # Store analysis in database
            if state.storage_id:
                try:
                    conn = sqlite3.connect(self.db_path)
                    cursor = conn.cursor()
                    
                    analysis_id = f"analysis_{state.workflow_id}"
                    analysis_json = json.dumps(state.analysis.to_dict())
                    
                    cursor.execute(
                        """INSERT INTO analyses (id, receipt_id, analysis_json, created_at)
                           VALUES (?, ?, ?, ?)""",
                        (analysis_id, state.storage_id, analysis_json, datetime.now())
                    )
                    
                    conn.commit()
                    conn.close()
                    logger.info(f"Stored analysis: {analysis_id}")
                except Exception as e:
                    logger.warning(f"Could not store analysis in database: {e}")
            
            logger.info(f"Generated {len(state.recommendations)} recommendations")
            
            # Mark workflow as complete
            state.completed_at = datetime.now().isoformat()
        
        except Exception as e:
            state.recommendation_error = str(e)
            logger.error(f"Recommendation Error: {e}")
        
        return state
    
    def run(
        self,
        input_type: str,
        input_content: str,
        budget_limits: Optional[Dict[str, float]] = None
    ) -> WorkflowState:
        """
        Run the complete workflow pipeline.
        
        Args:
            input_type: "image" or "text"
            input_content: File path (for image) or text content
            budget_limits: Optional per-category budget limits
        
        Returns:
            WorkflowState with all results
        """
        logger.info(f"Starting workflow: {input_type} input")
        
        start_time = time.time()
        
        # Create initial state
        state = WorkflowState(
            input_type=input_type,
            input_content=input_content,
            use_llm=self.use_llm,
            budget_limits=budget_limits or {}
        )
        
        try:
            # Run the graph
            final_state = self.graph.invoke(state)
            
            # Calculate processing time
            final_state.processing_time_ms = (time.time() - start_time) * 1000
            
            if final_state.has_error():
                logger.warning(f"Workflow completed with errors: {final_state.get_errors()}")
            else:
                logger.info(f"Workflow completed successfully in {final_state.processing_time_ms:.2f}ms")
            
            return final_state
        
        except Exception as e:
            state.workflow_error = str(e)
            state.processing_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Workflow failed: {e}")
            return state
