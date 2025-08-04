#!/usr/bin/env python3
"""
Test script for Gemini 2.5 Flash integration.
This script tests the LLM service with Gemini API.
"""

import asyncio
import os
from app.services.llm_service import LLMService

async def test_gemini_integration():
    """Test Gemini integration."""
    print("🧪 Testing Gemini 2.5 Flash Integration...")
    
    # Check if API key is set
    if not os.getenv('GOOGLE_API_KEY'):
        print("⚠️  GOOGLE_API_KEY not set. Please set it in your .env file.")
        print("   You can get one from: https://makersuite.google.com/app/apikey")
        return False
    
    try:
        # Initialize LLM service
        llm_service = LLMService()
        print(f"✅ LLM Service initialized with model: {llm_service.model}")
        
        # Test simple query parsing
        test_query = "What is the grace period for premium payment?"
        print(f"\n🔍 Testing query: {test_query}")
        
        # Test query parsing
        query_analysis = await llm_service.parse_query(test_query)
        print(f"✅ Query analysis: {query_analysis}")
        
        # Test answer generation
        context_chunks = [
            "The grace period for premium payments is 30 days from the due date.",
            "Premium payments are due on the 1st of each month.",
            "Late payments may result in policy cancellation."
        ]
        
        print(f"\n📝 Testing answer generation with context...")
        answer_data = await llm_service.generate_answer(test_query, context_chunks)
        print(f"✅ Answer: {answer_data.get('answer', 'No answer generated')}")
        print(f"✅ Confidence: {answer_data.get('confidence', 0.0)}")
        
        # Test reasoning explanation
        print(f"\n🧠 Testing reasoning explanation...")
        explanation = await llm_service.explain_reasoning(
            test_query, 
            answer_data.get('answer', ''), 
            [{'content': context_chunks[0]}]
        )
        print(f"✅ Explanation: {explanation[:100]}...")
        
        print("\n🎉 Gemini integration test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Gemini integration test failed: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("🚀 Testing HackRx 6.0 with Gemini 2.5 Flash")
    print("=" * 50)
    
    success = await test_gemini_integration()
    
    if success:
        print("\n✅ All tests passed! Gemini integration is working correctly.")
    else:
        print("\n❌ Tests failed. Please check your configuration.")

if __name__ == "__main__":
    asyncio.run(main()) 