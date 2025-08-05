
"""
Test script for PDF upload functionality using Gemini File API.
"""

import asyncio
import json
from app.services.simple_llm_service import SimpleLLMService
from app.config import settings

async def test_pdf_upload():
    """Test PDF upload and processing."""
    
    print("🚀 Testing PDF Upload with Gemini File API")
    print("=" * 50)
    
    # Test data
    test_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    test_questions = [
        "What is the grace period for premium payment under the National Parivar Mediclaim Plus Policy?",
        "Does this policy cover maternity expenses?"
    ]
    
    try:
        # Initialize the LLM service
        llm_service = SimpleLLMService(api_key=settings.GOOGLE_API_KEY)
        
        print(f"📄 Processing PDF from: {test_url}")
        print(f"❓ Questions: {len(test_questions)}")
        
        # Process the questions
        results = await llm_service.process_pdf_with_gemini(
            pdf_url=test_url,
            questions=test_questions
        )
        
        print("\n✅ Processing completed!")
        print(f"📊 Results:")
        
        for i, result in enumerate(results, 1):
            print(f"\n--- Question {i} ---")
            print(f"Q: {result['question']}")
            print(f"A: {result['answer']}")
        
        # Save results
        with open('pdf_upload_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to pdf_upload_test_results.json")
        
    except Exception as e:
        print(f"❌ Error during testing: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_upload()) 