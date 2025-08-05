
"""
Simple test to verify only answers are returned.
"""

import asyncio
import json
from app.services.simple_query_processor import SimpleQueryProcessor

async def test_simple_answers():
    """Test that only answers are returned."""
    
    print("🚀 Testing Simplified Answers Only")
    print("=" * 40)
    
    # Test data
    test_url = "https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=2023-01-03&st=2025-07-04T09%3A11%3A24Z&se=2027-07-05T09%3A11%3A00Z&sr=b&sp=r&sig=N4a9OU0w0QXO6AOIBiu4bpl7AXvEZogeT%2FjUHNO7HzQ%3D"
    
    test_questions = [
        "What is the grace period for premium payment?",
        "Does this policy cover maternity expenses?"
    ]
    
    try:
        # Initialize processor
        processor = SimpleQueryProcessor()
        
        print(f"📄 Processing PDF from: {test_url}")
        print(f"❓ Questions: {len(test_questions)}")
        
        # Process queries
        results = await processor.process_queries(
            documents=test_url,
            questions=test_questions
        )
        
        print("\n✅ Processing completed!")
        print(f"📊 Results:")
        print(f"   - Status: {results['status']}")
        print(f"   - Total questions: {results['total_questions']}")
        print(f"   - Successful questions: {results['successful_questions']}")
        
        print("\n📝 Answers Only:")
        for i, (question, answer) in enumerate(zip(test_questions, results['answers']), 1):
            print(f"\n--- Question {i} ---")
            print(f"Q: {question}")
            print(f"A: {answer}")
        
        # Save results
        with open('simple_answers_test.json', 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to simple_answers_test.json")
        
        # Verify no extra fields
        print(f"\n🔍 Response Structure:")
        for key in results.keys():
            print(f"   - {key}: {type(results[key])}")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_simple_answers()) 