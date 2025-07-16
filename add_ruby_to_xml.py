#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script để thêm Ruby annotations vào file XML chứa câu hỏi tiếng Nhật
Chỉ thêm Ruby cho những phần chưa có, tránh trùng lặp
"""

import json
import re
import xml.etree.ElementTree as ET
from xml.dom import minidom
import os
import time
from collections import defaultdict

# Compile regex patterns
KANJI_PATTERN = re.compile(r'[\u4e00-\u9fff]')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')
RUBY_PATTERN = re.compile(r'<ruby>.*?</ruby>', re.DOTALL)

# Set để lưu các kanji không tìm thấy
missing_kanji = set()

def load_dictionary(dictionary_path):
    """Đọc dictionary từ file JSON"""
    print("Đang load dictionary...")
    start_time = time.time()
    
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
        
        # Tối ưu dictionary - sắp xếp theo độ dài giảm dần
        optimized_dict = {}
        kanji_count = 0
        
        for kanji, hiragana in dictionary.items():
            # Lọc từ hợp lệ
            if (has_kanji(kanji) and 
                len(kanji) <= 10 and  
                len(kanji) >= 1 and   
                not re.search(r'[a-zA-Z0-9]', kanji)):
                optimized_dict[kanji] = hiragana
                kanji_count += 1
        
        # Sắp xếp theo độ dài giảm dần để ưu tiên từ dài trước
        sorted_dict = dict(sorted(optimized_dict.items(), key=lambda x: len(x[0]), reverse=True))
        
        load_time = time.time() - start_time
        print(f"Đã load {kanji_count} từ Kanji trong {load_time:.2f} giây")
        
        return sorted_dict
        
    except FileNotFoundError:
        print(f"Không tìm thấy file dictionary: {dictionary_path}")
        return {}
    except json.JSONDecodeError:
        print(f"Lỗi định dạng JSON trong file: {dictionary_path}")
        return {}

def has_kanji(text):
    """Kiểm tra xem text có chứa ký tự Kanji không"""
    return bool(KANJI_PATTERN.search(text))

def has_japanese(text):
    """Kiểm tra xem text có chứa ký tự tiếng Nhật không"""
    return bool(JAPANESE_PATTERN.search(text))

def has_ruby_tags(text):
    """Kiểm tra xem text đã có ruby tags chưa"""
    return bool(RUBY_PATTERN.search(text))

def clean_kanji_word(word):
    """Làm sạch từ Kanji bằng cách loại bỏ ký tự không phải tiếng Nhật"""
    cleaned = re.sub(r'[^\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', '', word)
    return cleaned

def find_kanji_matches(text, dictionary):
    """Tìm tất cả matches của kanji trong text với dictionary"""
    if not text or not has_japanese(text):
        return []
    
    matches = []
    text_len = len(text)
    covered = [False] * text_len
    
    # Tìm từ dài trước (ưu tiên từ ghép)
    for length in range(min(10, text_len), 0, -1):
        for i in range(text_len - length + 1):
            if any(covered[i:i+length]):
                continue
                
            substring = text[i:i+length]
            cleaned_substring = clean_kanji_word(substring)
            
            if (cleaned_substring and 
                has_kanji(cleaned_substring) and 
                cleaned_substring in dictionary):
                matches.append((i, i + length, cleaned_substring, dictionary[cleaned_substring]))
                # Đánh dấu vùng đã xử lý
                for j in range(i, i + length):
                    covered[j] = True
    
    # Ghi lại các Kanji không tìm thấy
    for i in range(text_len):
        if not covered[i] and has_kanji(text[i]):
            missing_kanji.add(text[i])
    
    # Sắp xếp matches theo vị trí
    matches.sort(key=lambda x: x[0])
    return matches

def add_ruby_to_text(text, dictionary):
    """Thêm ruby annotations vào text"""
    if not text or not has_japanese(text) or has_ruby_tags(text):
        return text
    
    matches = find_kanji_matches(text, dictionary)
    if not matches:
        return text
    
    # Xây dựng text mới với ruby tags
    result = ""
    last_end = 0
    
    for start, end, kanji, hiragana in matches:
        # Thêm text trước match
        result += text[last_end:start]
        # Thêm ruby tag
        result += f"<ruby>{kanji}<rt>{hiragana}</rt></ruby>"
        last_end = end
    
    # Thêm phần còn lại
    result += text[last_end:]
    
    return result

def process_text_element(element, dictionary):
    """Xử lý element chứa text, thêm ruby nếu cần"""
    if element.text and has_japanese(element.text) and not has_ruby_tags(element.text):
        original_text = element.text
        new_text = add_ruby_to_text(original_text, dictionary)
        if new_text != original_text:
            element.text = new_text
            return True
    return False

def find_cdata_sections(xml_string):
    """Tìm và xử lý các CDATA sections"""
    cdata_pattern = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
    return cdata_pattern.findall(xml_string)

def process_cdata_content(content, dictionary):
    """Xử lý nội dung trong CDATA section"""
    if not content or not has_japanese(content):
        return content
    
    # Parse HTML content trong CDATA
    # Tìm text nodes không nằm trong ruby tags
    def replace_japanese_text(match):
        text = match.group(0)
        if '<ruby>' in text or '</ruby>' in text or '<rt>' in text or '</rt>' in text:
            return text  # Đã có ruby, không xử lý
        return add_ruby_to_text(text, dictionary)
    
    # Tìm text nằm ngoài các HTML tags và ruby tags
    text_pattern = re.compile(r'>([^<]*[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff][^<]*)<', re.DOTALL)
    processed_content = text_pattern.sub(lambda m: f'>{add_ruby_to_text(m.group(1), dictionary)}<', content)
    
    return processed_content

def process_xml_file(input_file, output_file, dictionary_path):
    """Xử lý file XML và thêm ruby annotations"""
    global missing_kanji
    missing_kanji.clear()
    
    print(f"=== Xử lý file XML: {input_file} ===")
    start_time = time.time()
    
    # Load dictionary
    dictionary = load_dictionary(dictionary_path)
    if not dictionary:
        print("Dictionary trống hoặc không đọc được.")
        return
    
    try:
        # Đọc file XML as text để xử lý CDATA
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print("Đang xử lý CDATA sections...")
        
        # Xử lý CDATA sections
        def process_cdata_match(match):
            cdata_content = match.group(1)
            processed_content = process_cdata_content(cdata_content, dictionary)
            return f'<![CDATA[{processed_content}]]>'
        
        cdata_pattern = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
        xml_content = cdata_pattern.sub(process_cdata_match, xml_content)
        
        # Parse XML để xử lý các text elements khác
        print("Đang parse XML...")
        root = ET.fromstring(xml_content)
        
        # Đếm số elements được xử lý
        processed_elements = 0
        total_text_elements = 0
        
        # Xử lý tất cả elements có text
        for element in root.iter():
            if element.text and element.text.strip():
                total_text_elements += 1
                if process_text_element(element, dictionary):
                    processed_elements += 1
        
        # Tạo XML string với pretty format
        xml_str = ET.tostring(root, encoding='unicode')
        
        # Format XML đẹp
        dom = minidom.parseString(xml_str)
        pretty_xml = dom.toprettyxml(indent="  ", encoding=None)
        
        # Loại bỏ dòng XML declaration trùng lặp
        lines = pretty_xml.split('\n')
        if lines[0].startswith('<?xml') and len(lines) > 1:
            lines = lines[1:]  # Bỏ dòng đầu nếu trùng
        
        # Thêm XML declaration đúng
        final_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + '\n'.join(lines)
        
        # Lưu file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_xml)
        
        processing_time = time.time() - start_time
        
        print(f"\n=== THỐNG KÊ XỬ LÝ ===")
        print(f"File đầu vào: {input_file}")
        print(f"File đầu ra: {output_file}")
        print(f"Tổng elements có text: {total_text_elements}")
        print(f"Elements đã thêm ruby: {processed_elements}")
        print(f"Từ Kanji không tìm thấy: {len(missing_kanji)}")
        print(f"Thời gian xử lý: {processing_time:.2f} giây")
        
        # Lưu danh sách kanji thiếu
        if missing_kanji:
            save_missing_kanji_report(missing_kanji, f"{output_file}_missing_kanji.txt")
        
        print("Xử lý hoàn tất!")
        
    except ET.ParseError as e:
        print(f"Lỗi parse XML: {e}")
    except Exception as e:
        print(f"Lỗi xử lý file: {e}")

def save_missing_kanji_report(missing_kanji, report_file):
    """Lưu báo cáo các kanji không tìm thấy"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== KANJI KHÔNG TÌM THẤY TRONG DICTIONARY ===\n\n")
        for kanji in sorted(missing_kanji):
            f.write(f"{kanji}\n")
    
    print(f"Đã lưu báo cáo kanji thiếu: {report_file}")

def main():
    """Main function"""
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC.xml"
    output_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_with_ruby.xml"  # Đơn giản hóa tên file
    dictionary_file = "dictionary_full_jmdict.json"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(input_file):
        print("Khong tim thay file input")
        return
    
    if not os.path.exists(dictionary_file):
        print("Khong tim thay dictionary")
        return
    
    print("=== Chuong trinh them Ruby cho file XML ===")
    print("Input file: " + input_file)
    print("Output file: " + output_file)
    print("Dictionary file: " + dictionary_file)
    print()
    
    process_xml_file(input_file, output_file, dictionary_file)

if __name__ == "__main__":
    main()
