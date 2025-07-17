import json
import re
import os
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
from collections import defaultdict

# Compile regex patterns
KANJI_PATTERN = re.compile(r'[\u4e00-\u9fff]')
JAPANESE_PATTERN = re.compile(r'[\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]')
RUBY_PATTERN = re.compile(r'<ruby>.*?</ruby>', re.DOTALL)
CHOICE_PATTERN = re.compile(r'^[アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン]\.', re.MULTILINE)

# Set để lưu các kanji không tìm thấy
missing_kanji = set()

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
    """Kiểm tra xem text có chứa ký tự Kanji không"""
    return bool(KANJI_PATTERN.search(text))

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
    # Kiểm tra ký tự trước pos có phải là ký tự lựa chọn không
    char_before = text[pos-1]
    if char_before in 'アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン':
        # Kiểm tra ký tự tại pos có phải là dấu chấm không
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
    
    # Tìm từ dài trước (ưu tiên từ ghép)
    for length in range(min(10, text_len), 0, -1):
        for i in range(text_len - length + 1):
            if any(covered[i:i+length]):
                continue
            
            # Kiểm tra không phải là ký tự lựa chọn
            if is_choice_marker(text, i):
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
        if not covered[i] and has_kanji(text[i]) and not is_choice_marker(text, i):
            missing_kanji.add(text[i])
    
    matches.sort(key=lambda x: x[0])
    return matches

def clean_kanji_word(word):
    """Làm sạch từ Kanji bằng cách loại bỏ ký tự không phải tiếng Nhật"""
    cleaned = re.sub(r'[^\u3040-\u309f\u30a0-\u30ff\u4e00-\u9fff]', '', word)
    return cleaned

def add_ruby_to_text(text, dictionary):
    """Thêm ruby annotations vào text, tránh xử lý ký tự lựa chọn"""
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

def process_cdata_content(content, dictionary):
    """Xử lý nội dung trong CDATA section"""
    if not content or not has_japanese(content) or has_ruby_tags(content):
        return content
    
    # Xử lý từng phần text không nằm trong HTML tags
    def process_text_segment(text_segment):
        # Tránh xử lý nếu đã có ruby tags
        if has_ruby_tags(text_segment):
            return text_segment
        return add_ruby_to_text(text_segment, dictionary)
    
    # Tìm và xử lý text nằm giữa các HTML tags
    # Pattern để tìm text nằm ngoài tags
    pattern = r'>([^<]*)<'
    
    def replace_text(match):
        text_content = match.group(1)
        processed = process_text_segment(text_content)
        return f'>{processed}<'
    
    processed_content = re.sub(pattern, replace_text, content)
    
    # Xử lý text ở đầu và cuối không nằm trong tags
    if not content.startswith('<'):
        first_tag_pos = content.find('<')
        if first_tag_pos > 0:
            first_part = content[:first_tag_pos]
            rest_part = content[first_tag_pos:]
            processed_first = process_text_segment(first_part)
            processed_content = processed_first + rest_part
    
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
        # Đọc file XML
        with open(input_file, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        
        print("Đang xử lý CDATA sections...")
        processed_cdata_count = 0
        
        # Xử lý CDATA sections
        def process_cdata_match(match):
            nonlocal processed_cdata_count
            cdata_content = match.group(1)
            if has_japanese(cdata_content) and not has_ruby_tags(cdata_content):
                processed_content = process_cdata_content(cdata_content, dictionary)
                processed_cdata_count += 1
                return f'<![CDATA[{processed_content}]]>'
            return match.group(0)
        
        cdata_pattern = re.compile(r'<!\[CDATA\[(.*?)\]\]>', re.DOTALL)
        xml_content = cdata_pattern.sub(process_cdata_match, xml_content)
        
        print("Đang xử lý text elements...")
        processed_text_count = 0
        
        # Xử lý text elements không có CDATA
        def process_text_match(match):
            nonlocal processed_text_count
            text_content = match.group(1)
            if has_japanese(text_content) and not has_ruby_tags(text_content):
                processed_content = add_ruby_to_text(text_content, dictionary)
                processed_text_count += 1
                return f'<text>{processed_content}</text>'
            return match.group(0)
        
        # Pattern để tìm <text>content</text> không có CDATA
        text_pattern = re.compile(r'<text>([^<]*(?:(?!<text>|</text>)[^<]*)*)</text>', re.DOTALL)
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
        
        # Lưu danh sách kanji thiếu
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
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC.xml"
    output_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_improved.xml"
    dictionary_file = "dictionary_full_jmdict.json"
    
    # Kiểm tra file tồn tại
    if not os.path.exists(input_file):
        print(f"Không tìm thấy file input: {input_file}")
        return
    
    if not os.path.exists(dictionary_file):
        print(f"Không tìm thấy dictionary: {dictionary_file}")
        return
    
    print("=== Chương trình thêm Ruby cho file XML (Improved) ===")
    print(f"Input file: {input_file}")
    print(f"Output file: {output_file}")
    print(f"Dictionary file: {dictionary_file}")
    print()
    
    process_xml_file(input_file, output_file, dictionary_file)

if __name__ == "__main__":
    main()
