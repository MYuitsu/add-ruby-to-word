import os
from typing import Dict, Optional

def get_config() -> Optional[Dict[str, str]]:
    """Lấy cấu hình cho ChatGPT translator"""
    
    # Đọc API key từ environment variable hoặc set trực tiếp
    api_key = os.getenv('OPENAI_API_KEY', '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')
    
    if api_key == 'your_openai_api_key_here':
        print("❌ Vui lòng cập nhật OpenAI API key!")
        print("   Cách 1: Sửa trực tiếp trong config_chatgpt.py")
        print("   Cách 2: Set environment variable: OPENAI_API_KEY")
        print("   Cách 3: Tạo file .env với OPENAI_API_KEY=your_key")
        return None
    
    # Cấu hình files
    input_file = "kienthucchungfinal_no_vietnamese.docx"
    output_file = "kienthucchungfinal_with_vietnamese_chatgpt.docx"
    cache_file = "translation_cache_chatgpt.json"
    
    # Model ChatGPT (có thể thay đổi)
    # GPT-4.1-mini: Context length 1M tokens, tốt nhất cho dịch thuật (cân bằng giá/chất lượng)
    model = "gpt-4.1-mini"  # Mới nhất 2025, 1M context, $0.40/$1.60 per 1M tokens
    
    config = {
        'api_key': api_key,
        'model': model,
        'input_file': input_file,
        'output_file': output_file,
        'cache_file': cache_file
    }
    
    return config

def print_config():
    """In thông tin cấu hình"""
    config = get_config()
    if config is None:
        return
    
    print("🔧 CHATGPT TRANSLATOR CONFIG")
    print("-" * 40)
    print(f"🤖 Model: {config['model']}")
    print(f"📥 Input: {config['input_file']}")
    print(f"📤 Output: {config['output_file']}")
    print(f"💾 Cache: {config['cache_file']}")
    print(f"🔑 API Key: {'✅ Configured' if config['api_key'] != 'your_openai_api_key_here' else '❌ Not set'}")
    
    # Pricing info (cập nhật tháng 7/2025)
    pricing_info = {
        "gpt-3.5-turbo": "$0.50/$1.50 per 1M tokens",
        "gpt-4": "$30.00/$60.00 per 1M tokens", 
        "gpt-4-turbo": "$10.00/$30.00 per 1M tokens",
        "gpt-4o": "$5.00/$15.00 per 1M tokens",
        "gpt-4o-mini": "$0.15/$0.60 per 1M tokens",  # Model hiện tại được recommend
        "gpt-4.1": "$2.00/$8.00 per 1M tokens",
        "gpt-4.1-mini": "$0.40/$1.60 per 1M tokens", 
        "gpt-4.1-nano": "$0.10/$0.40 per 1M tokens",
        "o3": "$2.00/$8.00 per 1M tokens",
        "o4-mini": "$1.10/$4.40 per 1M tokens"
    }
    
    if config['model'] in pricing_info:
        print(f"💰 Pricing: {pricing_info[config['model']]}")
    
    print("-" * 40)

# Để test nhanh
if __name__ == "__main__":
    print_config()
