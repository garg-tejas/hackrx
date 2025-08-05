from typing import List, Dict, Any, Optional
from app.models.schemas import QueryRequest, QueryResponse, DocumentChunk
from app.services.document_processor import DocumentProcessor
from app.services.retrieval_service import RetrievalService
from app.services.llm_service import LLMService
import logging
import asyncio

logger = logging.getLogger(__name__)

class QueryProcessor:
    """Main orchestrator for processing document queries."""
    
    def __init__(self):
        self.doc_processor = DocumentProcessor()
        self.retrieval_service = RetrievalService()
        self.llm_service = LLMService()
        self.current_chunks = []
    
    async def process_document_queries(self, document_url: str, questions: List[str]) -> QueryResponse:
        """Main method to process document queries through the complete pipeline."""
        try:
            logger.info(f"Starting document processing for URL: {document_url}")
            
            # Step 1: Download and parse document
            chunks = await self.doc_processor.process_document(document_url)
            self.current_chunks = chunks
            
            # Step 2: Build search index
            await self.retrieval_service.build_document_index(chunks)
            
            # Step 3: Process each question
            answers = []
            explanations = []
            
            for i, question in enumerate(questions):
                logger.info(f"Processing question {i+1}/{len(questions)}: {question}")
                
                try:
                    # Parse query intent
                    query_analysis = await self.llm_service.parse_query(question)
                    
                    # Get relevant context chunks
                    context_chunks = await self.retrieval_service.get_context_for_query(question, max_chunks=5)
                    
                    if not context_chunks:
                        # No relevant chunks found
                        answer_data = {
                            "answer": "The information is not available in the provided document.",
                        }
                    else:
                        # Generate answer using LLM
                        answer_data = await self.llm_service.generate_answer(question, context_chunks)
                    
                    # Get source citations
                    search_results = await self.retrieval_service.search_relevant_chunks(question, top_k=3)
                    citations = await self.retrieval_service.get_source_citations(search_results)
                    
                    # Store results
                    answers.append(answer_data.get("answer", "Unable to generate answer"))
                    
                    # Generate explanation if confidence is low
                    if answer_data.get("confidence", 0.0) < 0.7:
                        explanation = await self.llm_service.explain_reasoning(
                            question, 
                            answer_data.get("answer", ""), 
                            citations
                        )
                        explanations.append(explanation)
                    else:
                        explanations.append(answer_data.get("reasoning", ""))
                    
                except Exception as e:
                    error_msg = str(e)
                    logger.error(f"Failed to process question {i+1}: {error_msg}")
                    
                    # Handle rate limiting specifically
                    if "Rate limit" in error_msg or "429" in error_msg:
                        answers.append("Rate limit exceeded. Please try again in a few minutes.")
                        explanations.append("API rate limit reached. The system is processing too many requests.")
                    else:
                        answers.append(f"Error processing question: {error_msg}")
                        explanations.append("Processing error occurred")
            
            # Step 4: Return structured response
            response = QueryResponse(
                answers=answers,
                explanations=explanations
            )
            
            logger.info(f"Successfully processed {len(questions)} questions")
            return response
            
        except Exception as e:
            logger.error(f"Failed to process document queries: {str(e)}")
            # Return error response
            error_answers = [f"Processing failed: {str(e)}"] * len(questions)
            return QueryResponse(
                answers=error_answers,
                explanations=["System error occurred"] * len(questions),
            )
    
    async def process_single_query(self, document_url: str, question: str) -> Dict[str, Any]:
        """Process a single query for testing purposes."""
        try:
            # Process document if not already processed
            if not self.current_chunks:
                chunks = await self.doc_processor.process_document(document_url)
                self.current_chunks = chunks
                await self.retrieval_service.build_document_index(chunks)
            
            # Get context and generate answer
            context_chunks = await self.retrieval_service.get_context_for_query(question)
            answer_data = await self.llm_service.generate_answer(question, context_chunks)
            
            search_results = await self.retrieval_service.search_relevant_chunks(question)
            
            return {
                "question": question,
                "answer": answer_data.get("answer"),
            }
            
        except Exception as e:
            logger.error(f"Failed to process single query: {str(e)}")
            return {
                "question": question,
                "answer": f"Error: {str(e)}",
            }
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get statistics about the current processing session."""
        return {
            "total_chunks": len(self.current_chunks),
            "index_stats": self.retrieval_service.get_index_stats(),
            "llm_info": self.llm_service.get_model_info()
        }
    
    def clear_session(self) -> None:
        """Clear current processing session."""
        self.current_chunks = []
        self.retrieval_service.clear_index()
        logger.info("Cleared processing session") 