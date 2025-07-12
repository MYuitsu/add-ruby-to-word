#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from remove_vietnamese import is_vietnamese_text, remove_vietnamese_chars_from_word, should_keep_paragraph

def test_vietnamese_detection():
    """Test các trường hợp phát hiện tiếng Việt"""
    print("=== TEST PHÁT HIỆN TIẾNG VIỆT ===")
    
    test_cases = [
        ("phng", True),  # Từ tiếng Việt bị thiếu ký tự
        ("phương", True),  # Từ tiếng Việt đầy đủ
        ("品質管理", False),  # Tiếng Nhật
        ("quality", False),  # Tiếng Anh
        ("management", False),  # Tiếng Anh
        ("Kit", False),  # Từ không phải tiếng Việt
        ("lng", True),  # Từ tiếng Việt bị thiếu ký tự
        ("lượng", True),  # Từ tiếng Việt đầy đủ
        ("hthng", False),  # Không phải tiếng Việt
        ("hệ thống", True),  # Tiếng Việt có khoảng trắng
    ]
    
    for text, expected in test_cases:
        result = is_vietnamese_text(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (expected: {expected})")

def test_remove_vietnamese_chars():
    """Test loại bỏ ký tự tiếng Việt"""
    print("\n=== TEST LOẠI BỎ KÝ TỰ TIẾNG VIỆT ===")
    
    test_cases = [
        ("phương", "phng"),  # Bỏ ký tự có dấu
        ("lượng", "lng"),   # Bỏ ký tự có dấu
        ("chất", "cht"),    # Bỏ ký tự có dấu
        ("quality", "quality"),  # Giữ nguyên tiếng Anh
        ("管理", "管理"),    # Giữ nguyên tiếng Nhật
        ("thông", "thng"),  # Bỏ ký tự có dấu
        ("để", ""),         # Bỏ hết vì toàn ký tự có dấu
    ]
    
    for text, expected in test_cases:
        result = remove_vietnamese_chars_from_word(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> '{result}' (expected: '{expected}')")

def test_paragraph_decision():
    """Test quyết định giữ lại paragraph"""
    print("\n=== TEST QUYẾT ĐỊNH GIỮ LẠI PARAGRAPH ===")
    
    test_cases = [
        ("第１節品質管理の考え方", True),  # Chủ yếu tiếng Nhật
        ("Kim cht lng mt hthng", False),  # Chủ yếu tiếng Việt
        ("Quality management system", True),  # Tiếng Anh
        ("品質管理は、顧客ニーズに合った品質", True),  # Tiếng Nhật
        ("Cht lng là một hệ thống", False),  # Tiếng Việt
        ("API reference guide", True),  # Tiếng Anh với viết tắt
        ("HTML5 và CSS3", True),  # Có viết tắt
        ("管理とは、経営目的", True),  # Tiếng Nhật
    ]
    
    for text, expected in test_cases:
        result = should_keep_paragraph(text)
        status = "✓" if result == expected else "✗"
        print(f"{status} '{text}' -> {result} (expected: {expected})")

if __name__ == "__main__":
    test_vietnamese_detection()
    test_remove_vietnamese_chars()
    test_paragraph_decision()
