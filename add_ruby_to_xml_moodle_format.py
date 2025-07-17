#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import re
import os
import time
from collections import defaultdict

# Compile regex patterns
KANJI_PATTERN = re.compile(r'[\u4e00-\u9fff]')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uff10-\uff19]')  # Thêm full-width numbers
RUBY_PATTERN = re.compile(r'<ruby>.*?</ruby>', re.DOTALL)
CHOICE_PATTERN = re.compile(r'^[アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン]\.', re.MULTILINE)
FULLWIDTH_NUMBER_PATTERN = re.compile(r'[\uff10-\uff19]')  # Full-width numbers pattern

# Set để lưu các kanji không tìm thấy
missing_kanji = set()

# Full-width numbers mapping
fullwidth_numbers = {
    '０': 'ゼロ', '１': 'いち', '２': 'に', '３': 'さん', '４': 'よん',
    '５': 'ご', '６': 'ろく', '７': 'なな', '８': 'はち', '９': 'きゅう'
}

def load_dictionary(dictionary_path):
    """Đọc dictionary từ file JSON"""
    print("Đang load dictionary...")
    start_time = time.time()
    
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
        
        # Lọc và tối ưu dictionary
        optimized_dict = {}
        kanji_count = 0
        
        for kanji, hiragana in dictionary.items():
            if (has_kanji(kanji) and 
                len(kanji) <= 10 and 
                len(kanji) >= 1 and
                not re.search(r'[a-zA-Z0-9]', kanji)):
                optimized_dict[kanji] = hiragana
                kanji_count += 1
        
        # Thêm full-width numbers với hiragana readings
        for fw_num, hiragana in fullwidth_numbers.items():
            optimized_dict[fw_num] = hiragana
            kanji_count += 1
        
        # Sắp xếp theo độ dài giảm dần
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
    """Kiểm tra xem text có chứa ký tự Kanji hoặc full-width number không"""
    return bool(KANJI_PATTERN.search(text)) or bool(FULLWIDTH_NUMBER_PATTERN.search(text))

def has_japanese(text):
    """Kiểm tra xem text có chứa ký tự tiếng Nhật không"""
    return bool(JAPANESE_PATTERN.search(text))

def has_ruby_tags(text):
    """Kiểm tra xem text đã có ruby tags chưa"""
    return bool(RUBY_PATTERN.search(text))

def is_choice_marker(text, pos):
    """Kiểm tra xem vị trí có phải là ký tự lựa chọn + dấu chấm không"""
    if pos == 0:
        return False
    char_before = text[pos-1]
    if char_before in 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン':
        if pos < len(text) and text[pos] == '．':
            return True
    return False

def find_kanji_matches(text, dictionary):
    """Tìm tất cả matches của kanji trong text với dictionary"""
    if not text or not has_japanese(text):
        return []
    
    matches = []
    text_len = len(text)
    covered = [False] * text_len
    
    # Đánh dấu các vùng có ruby tags để bỏ qua
    ruby_matches = list(RUBY_PATTERN.finditer(text))
    for ruby_match in ruby_matches:
        start, end = ruby_match.span()
        for i in range(start, end):
            if i < text_len:
                covered[i] = True
    
    # Tìm từ dài trước (ưu tiên từ ghép)
    for length in range(min(10, text_len), 0, -1):
        for i in range(text_len - length + 1):
            if any(covered[i:i+length]):
                continue
            
            if is_choice_marker(text, i):
                continue
                
            substring = text[i:i+length]
            cleaned_substring = clean_kanji_word(substring)
            
            if (cleaned_substring and 
                has_kanji(cleaned_substring) and 
                cleaned_substring in dictionary):
                matches.append((i, i + length, cleaned_substring, dictionary[cleaned_substring]))
                for j in range(i, i + length):
                    covered[j] = True
    
    # Xử lý các full-width numbers đơn lẻ
    for i in range(text_len):
        if not covered[i] and FULLWIDTH_NUMBER_PATTERN.match(text[i]):
            matches.append((i, i + 1, text[i], fullwidth_numbers.get(text[i], text[i])))
            covered[i] = True
    
    # Ghi lại các Kanji không tìm thấy
    for i in range(text_len):
        if not covered[i] and has_kanji(text[i]) and not is_choice_marker(text, i):
            missing_kanji.add(text[i])
    
    matches.sort(key=lambda x: x[0])
    return matches

def clean_kanji_word(word):
    """Làm sạch từ Kanji bằng cách loại bỏ ký tự không phải tiếng Nhật"""
    cleaned = re.sub(r'[^\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff\uff10-\uff19]', '', word)
    return cleaned

def add_ruby_to_text(text, dictionary):
    """Thêm ruby annotations vào text với format đúng cho Moodle"""
    if not text or not has_japanese(text) or has_ruby_tags(text):
        return text
    
    # Xử lý trước các pattern đặc biệt như "問題[số]"
    pattern = r'問題([\uff10-\uff19])'
    def replace_problem_number(match):
        number = match.group(1)
        number_reading = fullwidth_numbers.get(number, number)
        return f'<ruby>問題<rt>もんだい</rt></ruby><ruby>{number}<rt>{number_reading}</rt></ruby>'
    
    processed_text = re.sub(pattern, replace_problem_number, text)
    
    # Xử lý các từ còn lại
    matches = find_kanji_matches(processed_text, dictionary)
    if not matches:
        return processed_text
    
    # Xây dựng text mới với ruby tags
    result = ""
    last_end = 0
    
    for start, end, kanji, hiragana in matches:
        result += processed_text[last_end:start]
        result += f"<ruby>{kanji}<rt>{hiragana}</rt></ruby>"
        last_end = end
    
    result += processed_text[last_end:]
    return result

def process_cdata_content(content, dictionary):
    """Xử lý nội dung trong CDATA section với format đúng"""
    if not content or not has_japanese(content) or has_ruby_tags(content):
        return content
    
    # Kiểm tra nếu content đã có <p> tags
    if '<p>' in content:
        # Xử lý text trong <p> tags
        def process_p_content(match):
            p_content = match.group(1)
            processed = add_ruby_to_text(p_content, dictionary)
            return f'<p>{processed}</p>'
        
        # Pattern để tìm nội dung trong <p> tags
        p_pattern = r'<p>(.*?)</p>'
        processed_content = re.sub(p_pattern, process_p_content, content, flags=re.DOTALL)
        return processed_content
    else:
        # Nếu không có <p> tags, wrap với <p> và xử lý
        processed = add_ruby_to_text(content, dictionary)
        return f'<p>{processed}</p>'

def process_xml_file(input_file, output_file, dictionary_path):
    """Xử lý file XML và thêm ruby annotations với format đúng"""
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
        # Đọc file XML
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print("Đang xử lý CDATA sections...")
        processed_cdata_count = 0
        
        # Xử lý tất cả <text> để đảm bảo bọc CDATA duy nhất
        processed_text_count = 0
        def process_text_match(match):
            text_content = match.group(1)
            # Nếu đã có CDATA thì giữ nguyên, nếu chưa thì thêm vào
            if text_content.strip().startswith('<![CDATA['):
                return f'<text>{text_content.strip()}</text>'
            # Nếu có tiếng Nhật và chưa có ruby thì thêm ruby rồi bọc CDATA
            if has_japanese(text_content) and not has_ruby_tags(text_content):
                processed_content = add_ruby_to_text(text_content, dictionary)
                nonlocal processed_text_count
                processed_text_count += 1
                return f'<text><![CDATA[{processed_content}]]></text>'
            # Nếu không thì vẫn bọc CDATA
            return f'<text><![CDATA[{text_content.strip()}]]></text>'

        text_pattern = re.compile(r'<text>(.*?)</text>', re.DOTALL)
        xml_content = text_pattern.sub(process_text_match, xml_content)
        
        # Lưu file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        
        processing_time = time.time() - start_time
        
        print(f"\n=== THỐNG KÊ XỬ LÝ ===")
        print(f"File đầu vào: {input_file}")
        print(f"File đầu ra: {output_file}")
        print(f"CDATA sections đã xử lý: {processed_cdata_count}")
        print(f"Text elements đã xử lý: {processed_text_count}")
        print(f"Từ Kanji không tìm thấy: {len(missing_kanji)}")
        print(f"Thời gian xử lý: {processing_time:.2f} giây")
        
        if missing_kanji:
            save_missing_kanji_report(missing_kanji, f"{output_file}_missing_kanji.txt")
        
        print("Xử lý hoàn tất!")
        
    except Exception as e:
        print(f"Lỗi xử lý file: {e}")
        import traceback
        traceback.print_exc()

def save_missing_kanji_report(missing_kanji, report_file):
    """Lưu báo cáo các kanji không tìm thấy"""
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("=== KANJI KHÔNG TÌM THẤY TRONG DICTIONARY ===\n\n")
        for kanji in sorted(missing_kanji):
            f.write(f"{kanji}\n")
    
    print(f"Đã lưu báo cáo kanji thiếu: {report_file}")

def main():
    """Main function"""
    dictionary_file = "dictionary_full_jmdict.json"
    input_folder = "2025.7.14"
    if not os.path.exists(dictionary_file):
        print(f"Không tìm thấy dictionary: {dictionary_file}")
        return

    if not os.path.exists(input_folder):
        print(f"Không tìm thấy thư mục: {input_folder}")
        return

    print("=== Chương trình thêm Ruby cho tất cả file XML trong thư mục 2025.7.14 (Moodle Format) ===")
    print(f"Dictionary file: {dictionary_file}")
    print()

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.xml'):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(input_folder, filename.replace('.xml', '_ruby_moodle_format.xml'))
            print(f"\n--- Đang xử lý: {input_file} ---")
            process_xml_file(input_file, output_file, dictionary_file)

if __name__ == "__main__":
    main()
