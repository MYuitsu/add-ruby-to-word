#!/usr/bin/env python3
"""
Script helper để test Gemini API rate limits và troubleshoot
"""

import google.generativeai as genai
import time
import json
from config import get_config

def test_api_connection():
    """Test kết nối API và rate limits"""
    print("🔍 TESTING GEMINI API CONNECTION & RATE LIMITS")
    print("=" * 50)
    
    config = get_config()
    if not config:
        return
    
    try:
        genai.configure(api_key=config['api_key'])
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        print("✅ API key configured successfully")
        print(f"🤖 Model: gemini-1.5-flash")
        print()
        
        # Test với requests đơn giản
        test_requests = [
            "こんにちは",
            "ありがとう", 
            "すみません",
            "おはよう",
            "こんばんは"
        ]
        
        successful_requests = 0
        failed_requests = 0
        start_time = time.time()
        
        for i, test_text in enumerate(test_requests, 1):
            try:
                print(f"📤 Request {i}/{len(test_requests)}: '{test_text}'")
                
                response = model.generate_content(
                    f"Translate this Japanese to Vietnamese: {test_text}",
                    generation_config={
                        'temperature': 0.3,
                        'max_output_tokens': 100,
                    }
                )
                
                if response.text:
                    print(f"✅ Response: {response.text.strip()}")
                    successful_requests += 1
                else:
                    print("❌ Empty response")
                    failed_requests += 1
                
                # Delay giữa requests
                if i < len(test_requests):
                    print("⏳ Waiting 6 seconds...")
                    time.sleep(6)
                
            except Exception as e:
                print(f"❌ Error: {e}")
                failed_requests += 1
                
                # Check nếu là rate limit error
                if "quota" in str(e).lower() or "rate" in str(e).lower():
                    print("🛑 Rate limit detected! Waiting 60 seconds...")
                    time.sleep(60)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 50)
        print("📊 TEST RESULTS")
        print("=" * 50)
        print(f"✅ Successful requests: {successful_requests}")
        print(f"❌ Failed requests: {failed_requests}")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        print(f"📈 Average time per request: {total_time/len(test_requests):.2f} seconds")
        
        if successful_requests > 0:
            print("\n🎉 API is working! You can proceed with translation.")
        else:
            print("\n💔 API test failed. Check your API key and internet connection.")
            
    except Exception as e:
        print(f"❌ API Configuration Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Check your API key in config.py")
        print("2. Make sure you have internet connection")
        print("3. Verify API key at: https://makersuite.google.com/app/apikey")

def check_rate_limits():
    """Hiển thị thông tin về rate limits"""
    print("\n📋 GEMINI API RATE LIMITS (Free Tier)")
    print("=" * 40)
    print("🔹 gemini-1.5-flash:")
    print("   • 15 requests per minute")
    print("   • 1 million tokens per minute")
    print("   • 1,500 requests per day")
    print()
    print("🔹 gemini-1.5-pro:")
    print("   • 2 requests per minute")
    print("   • 32,000 tokens per minute") 
    print("   • 50 requests per day")
    print()
    print("💡 Recommendations:")
    print("   • Use delays of 5-6 seconds between requests")
    print("   • Use batch processing when possible")
    print("   • Cache translations to avoid re-requests")
    print("   • Monitor your quota at: https://aistudio.google.com/app/apikey")

def estimate_translation_time(japanese_paragraphs: int):
    """Ước tính thời gian dịch dựa trên rate limits"""
    print(f"\n⏱️  TRANSLATION TIME ESTIMATION")
    print("=" * 40)
    print(f"📄 Japanese paragraphs to translate: {japanese_paragraphs}")
    
    # Với rate limit 12 requests/minute để an toàn
    requests_per_minute = 12
    minutes_needed = japanese_paragraphs / requests_per_minute
    hours_needed = minutes_needed / 60
    
    print(f"⏰ Estimated time: {minutes_needed:.1f} minutes ({hours_needed:.1f} hours)")
    
    if minutes_needed > 60:
        print("⚠️  This will take a long time. Consider:")
        print("   • Processing in smaller batches")
        print("   • Using batch translation function")
        print("   • Processing over multiple sessions")

if __name__ == "__main__":
    print("🧪 GEMINI API TROUBLESHOOTER")
    print("=" * 50)
    
    # Test API connection
    test_api_connection()
    
    # Show rate limits info
    check_rate_limits()
    
    # Estimate time cho file hiện tại
    try:
        # Đọc file và đếm paragraphs tiếng Nhật (rough estimate)
        from docx import Document
        from config import get_config
        
        config = get_config()
        if config and config['input_file']:
            try:
                doc = Document(config['input_file'])
                japanese_count = 0
                
                # Rough count - paragraphs có ký tự tiếng Nhật
                import re
                japanese_pattern = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]+')
                
                for paragraph in doc.paragraphs:
                    if japanese_pattern.search(paragraph.text):
                        japanese_count += 1
                
                if japanese_count > 0:
                    estimate_translation_time(japanese_count)
                    
            except Exception as e:
                print(f"⚠️  Could not analyze input file: {e}")
                
    except ImportError:
        print("⚠️  Could not estimate translation time (missing dependencies)")
    
    print("\n🎯 Ready to translate? Run: python japanese_translator_v2.py")
