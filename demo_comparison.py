"""
Demo script để test và so sánh Gemini vs ChatGPT translator
"""

import os
import time
import json
from typing import Dict, List

def test_gemini_translator():
    """Test Gemini translator"""
    print("🧪 TESTING GEMINI TRANSLATOR")
    print("="*50)
    
    try:
        from japanese_translator_v2 import JapaneseToVietnameseTranslator
        from config import get_config
        
        config = get_config()
        if not config:
            print("❌ Gemini config không hợp lệ")
            return None
        
        translator = JapaneseToVietnameseTranslator(config['api_key'])
        
        # Test texts
        test_texts = [
            "こんにちは、元気ですか？",
            "今日は良い天気ですね。",
            "日本語を勉強しています。"
        ]
        
        results = {}
        start_time = time.time()
        
        for i, text in enumerate(test_texts):
            print(f"📝 Testing text {i+1}: {text}")
            translation = translator.translate_text(text)
            results[text] = translation
            print(f"✅ Result: {translation}")
            print()
        
        end_time = time.time()
        
        return {
            'translator': 'Gemini',
            'results': results,
            'time': end_time - start_time,
            'api_calls': translator.request_count,
            'daily_requests': translator.daily_request_count,
            'cache_size': len(translator.translation_cache)
        }
        
    except Exception as e:
        print(f"❌ Gemini test failed: {e}")
        return None

def test_chatgpt_translator():
    """Test ChatGPT translator"""
    print("🧪 TESTING CHATGPT TRANSLATOR")
    print("="*50)
    
    try:
        from japanese_translator_chatgpt import JapaneseToVietnameseTranslatorChatGPT
        from config_chatgpt import get_config
        
        config = get_config()
        if not config:
            print("❌ ChatGPT config không hợp lệ")
            return None
        
        translator = JapaneseToVietnameseTranslatorChatGPT(
            api_key=config['api_key'],
            model=config['model']
        )
        
        # Test texts
        test_texts = [
            "こんにちは、元気ですか？",
            "今日は良い天気ですね。",
            "日本語を勉強しています。",
            "私は学生です。毎日学校に行きます。",
            "東京は大きな都市です。"
        ]
        
        # Test batch processing
        paragraph_data = [(f"test_{i}", text) for i, text in enumerate(test_texts)]
        
        start_time = time.time()
        
        # Create batch and translate
        batches = translator.create_translation_batch(paragraph_data)
        print(f"📦 Created {len(batches)} batches")
        
        all_results = {}
        for batch_idx, batch in enumerate(batches):
            print(f"🔄 Processing batch {batch_idx + 1}")
            batch_results = translator.translate_batch(batch)
            all_results.update(batch_results)
        
        end_time = time.time()
        
        return {
            'translator': 'ChatGPT',
            'model': config['model'],
            'results': all_results,
            'time': end_time - start_time,
            'api_calls': translator.request_count,
            'tokens_used': translator.total_tokens_used,
            'estimated_cost': translator.estimated_cost,
            'cache_size': len(translator.translation_cache),
            'batches': len(batches)
        }
        
    except Exception as e:
        print(f"❌ ChatGPT test failed: {e}")
        return None

def compare_results(gemini_result: Dict, chatgpt_result: Dict):
    """So sánh kết quả giữa 2 translator"""
    print("\n" + "="*60)
    print("📊 SO SÁNH KẾT QUẢ")
    print("="*60)
    
    if gemini_result:
        print(f"🔥 GEMINI RESULTS:")
        print(f"   ⏱️  Thời gian: {gemini_result['time']:.2f}s")
        print(f"   🔄 API calls: {gemini_result['api_calls']}")
        print(f"   📊 Daily requests: {gemini_result['daily_requests']}")
        print(f"   💾 Cache size: {gemini_result['cache_size']}")
        print(f"   💰 Chi phí: FREE (trong hạn mức)")
        print()
    
    if chatgpt_result:
        print(f"🤖 CHATGPT RESULTS:")
        print(f"   🧠 Model: {chatgpt_result['model']}")
        print(f"   ⏱️  Thời gian: {chatgpt_result['time']:.2f}s")
        print(f"   🔄 API calls: {chatgpt_result['api_calls']}")
        print(f"   📦 Batches: {chatgpt_result['batches']}")
        print(f"   🎯 Tokens: {chatgpt_result['tokens_used']:,}")
        print(f"   💰 Chi phí: ${chatgpt_result['estimated_cost']:.4f}")
        print(f"   💾 Cache size: {chatgpt_result['cache_size']}")
        print()
    
    # So sánh hiệu suất
    if gemini_result and chatgpt_result:
        print("⚡ PERFORMANCE COMPARISON:")
        
        # Speed
        speed_ratio = gemini_result['time'] / chatgpt_result['time']
        if speed_ratio > 1:
            print(f"   🏃 ChatGPT nhanh hơn {speed_ratio:.1f}x")
        else:
            print(f"   🏃 Gemini nhanh hơn {1/speed_ratio:.1f}x")
        
        # API efficiency
        gemini_efficiency = len(gemini_result['results']) / gemini_result['api_calls']
        chatgpt_efficiency = len(chatgpt_result['results']) / chatgpt_result['api_calls']
        
        print(f"   📈 Gemini efficiency: {gemini_efficiency:.1f} translations/call")
        print(f"   📈 ChatGPT efficiency: {chatgpt_efficiency:.1f} translations/call")
        
        efficiency_ratio = chatgpt_efficiency / gemini_efficiency
        print(f"   🎯 ChatGPT hiệu quả hơn {efficiency_ratio:.1f}x về API calls")
        
        print()
    
    # So sánh chất lượng dịch
    common_texts = []
    if gemini_result and chatgpt_result:
        gemini_texts = set(gemini_result['results'].keys())
        chatgpt_texts = set(chatgpt_result['results'].keys())
        common_texts = gemini_texts.intersection(chatgpt_texts)
        
        if common_texts:
            print("🔍 TRANSLATION QUALITY COMPARISON:")
            for text in list(common_texts)[:3]:  # Show first 3
                print(f"   📝 Original: {text}")
                print(f"   🔥 Gemini: {gemini_result['results'][text]}")
                print(f"   🤖 ChatGPT: {chatgpt_result['results'][text]}")
                print()
    
    print("="*60)

def main():
    """Main demo function"""
    print("🚀 TRANSLATOR COMPARISON DEMO")
    print("="*60)
    
    # Kiểm tra file cấu hình
    configs_ok = True
    
    try:
        from config import get_config as get_gemini_config
        gemini_config = get_gemini_config()
        if not gemini_config:
            print("❌ Gemini config not available")
            configs_ok = False
    except:
        print("❌ Gemini config file missing")
        configs_ok = False
    
    try:
        from config_chatgpt import get_config as get_chatgpt_config  
        chatgpt_config = get_chatgpt_config()
        if not chatgpt_config:
            print("❌ ChatGPT config not available")
            configs_ok = False
    except:
        print("❌ ChatGPT config file missing")
        configs_ok = False
    
    if not configs_ok:
        print("\n💡 Hướng dẫn setup:")
        print("1. Tạo config.py với Gemini API key")
        print("2. Tạo config_chatgpt.py với OpenAI API key")  
        print("3. Chạy lại demo")
        return
    
    print("✅ Configs available, starting tests...\n")
    
    # Test Gemini (nếu có config)
    gemini_result = None
    if gemini_config:
        gemini_result = test_gemini_translator()
        time.sleep(2)  # Delay between tests
    
    # Test ChatGPT (nếu có config)
    chatgpt_result = None
    if chatgpt_config:
        chatgpt_result = test_chatgpt_translator()
    
    # So sánh kết quả
    compare_results(gemini_result, chatgpt_result)
    
    # Lưu kết quả để tham khảo
    demo_results = {
        'timestamp': time.time(),
        'gemini': gemini_result,
        'chatgpt': chatgpt_result
    }
    
    with open('demo_results.json', 'w', encoding='utf-8') as f:
        json.dump(demo_results, f, ensure_ascii=False, indent=2, default=str)
    
    print("💾 Kết quả đã lưu vào demo_results.json")
    print("🎉 Demo completed!")

if __name__ == "__main__":
    main()
