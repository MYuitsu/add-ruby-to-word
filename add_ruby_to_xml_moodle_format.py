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
            # Giữ lại mọi từ Kanji, kể cả từ đơn lẻ, miễn là có ký tự Kanji hoặc số full-width
            if has_kanji(kanji) and not re.search(r'[a-zA-Z0-9]', kanji):
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
    
    # Tìm các chuỗi Kanji hoặc số full-width liên tiếp, ưu tiên vùng dài nhất
    i = 0
    while i < text_len:
        if covered[i] or is_choice_marker(text, i):
            i += 1
            continue
        # Ưu tiên nhận diện chuỗi dài nhất có trong dictionary
        found = False
        for length in range(min(10, text_len - i), 0, -1):
            substring = text[i:i+length]
            if substring in dictionary and not any(covered[i:i+length]):
                matches.append((i, i+length, substring, dictionary[substring]))
                for j in range(i, i+length):
                    covered[j] = True
                i += length
                found = True
                break
        if found:
            continue
        # Nếu không có từ ghép, kiểm tra số full-width liên tiếp
        if FULLWIDTH_NUMBER_PATTERN.match(text[i]):
            start = i
            while i < text_len and not covered[i] and FULLWIDTH_NUMBER_PATTERN.match(text[i]):
                i += 1
            end = i
            num_str = text[start:end]
            num_reading = ''.join([fullwidth_numbers.get(ch, ch) for ch in num_str])
            matches.append((start, end, num_str, num_reading))
            for j in range(start, end):
                covered[j] = True
            continue
        i += 1
    
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
    
    # Xử lý trước các pattern đặc biệt như "問題[chuỗi số full-width]"
    pattern = r'問題([\uff10-\uff19]+)'
    def replace_problem_number(match):
        number = match.group(1)
        number_reading = ''.join([fullwidth_numbers.get(ch, ch) for ch in number])
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

        print("Đang xử lý các tag format=\"html\"...")
        processed_html_count = 0
        # Xử lý các tag có format="html" (name, questiontext, answer, feedback, ...)
        def process_html_tag(match):
            tag = match.group(1)
            attrs = match.group(2)
            content = match.group(3)
            # Chỉ xử lý nếu có tiếng Nhật và chưa có ruby
            if has_japanese(content) and not has_ruby_tags(content):
                processed = add_ruby_to_text(content, dictionary)
                nonlocal processed_html_count
                processed_html_count += 1
                return f'<{tag}{attrs}>{processed}</{tag}>'
            return match.group(0)

        # Regex cho các tag có format="html"
        html_tag_pattern = re.compile(r'<(name|questiontext|answer|feedback|generalfeedback|correctfeedback|partiallycorrectfeedback|incorrectfeedback)([^>]*)format="html"[^>]*>(.*?)</\1>', re.DOTALL)
        xml_content = html_tag_pattern.sub(process_html_tag, xml_content)

        # Đảm bảo mọi <text> đều được bọc CDATA sau khi xử lý ruby
        def wrap_text_cdata(match):
            content = match.group(1)
            # Nếu đã có CDATA thì giữ nguyên
            if content.strip().startswith('<![CDATA['):
                return f'<text>{content}</text>'
            # Nếu chưa có, bọc lại bằng CDATA
            return f'<text><![CDATA[{content}]]></text>'

        text_pattern = re.compile(r'<text>(.*?)</text>', re.DOTALL)
        xml_content = text_pattern.sub(wrap_text_cdata, xml_content)

        # Lưu file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(xml_content)

        processing_time = time.time() - start_time

        print(f"\n=== THỐNG KÊ XỬ LÝ ===")
        print(f"File đầu vào: {input_file}")
        print(f"File đầu ra: {output_file}")
        print(f"Tag format=\"html\" đã xử lý: {processed_html_count}")
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
