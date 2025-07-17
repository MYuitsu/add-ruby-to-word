#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os

def convert_ruby_for_moodle(text):
    """Convert ruby tags to Moodle-friendly format"""
    
    # Chuyển <ruby>kanji<rt>hiragana</rt></ruby> thành kanji(hiragana)
    def ruby_to_parentheses(match):
        kanji = match.group(1)
        hiragana = match.group(2)
        return f"{kanji}({hiragana})"

    ruby_pattern = r'<ruby>([^<]*)<rt>([^<]*)</rt></ruby>'
    converted = re.sub(ruby_pattern, ruby_to_parentheses, text)

    # Đảm bảo các trường <text> chỉ chứa chuỗi, không bị tách thành mảng
    # Gộp các đoạn CDATA lại thành một đoạn duy nhất nếu cần
    # Xử lý: Nếu có nhiều <![CDATA[...]]> trong một <text>, hãy nối lại thành một chuỗi
    def merge_cdata(text):
        # Tìm tất cả CDATA sections trong <text>
        cdata_pattern = r'<text>(?:\s*<!\[CDATA\[(.*?)\]\]>\s*)+</text>'
        def cdata_replacer(match):
            all_cdata = re.findall(r'<!\[CDATA\[(.*?)\]\]>', match.group(0), re.DOTALL)
            merged = ''.join(all_cdata)
            return f'<text><![CDATA[{merged}]]></text>'
        return re.sub(cdata_pattern, cdata_replacer, text, flags=re.DOTALL)

    converted = merge_cdata(converted)
    return converted

def create_moodle_compatible_file(input_file, output_file):
    """Create a Moodle-compatible version of the XML file"""
    
    print(f"Converting {input_file} to Moodle-compatible format...")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Convert ruby tags
        converted_content = convert_ruby_for_moodle(content)
        
        # Count conversions
        ruby_count = len(re.findall(r'<ruby>[^<]*<rt>[^<]*</rt></ruby>', content))
        
        # Write converted content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(converted_content)
        
        print(f"✓ Converted {ruby_count} ruby tags")
        print(f"✓ Created Moodle-compatible file: {output_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_multiple_formats():
    """Create multiple format versions for testing"""
    
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_fixed.xml"

    # Format 1: Parentheses format, đảm bảo <text> là chuỗi duy nhất
    print("Creating Format 1: Parentheses format kanji(hiragana)")
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    def ruby_to_parentheses(match):
        kanji = match.group(1)
        hiragana = match.group(2)
        return f"{kanji}({hiragana})"

    content1 = re.sub(r'<ruby>([^<]*)<rt>([^<]*)</rt></ruby>', ruby_to_parentheses, content)
    # Gộp các đoạn CDATA lại thành một đoạn duy nhất nếu cần
    def merge_cdata(text):
        cdata_pattern = r'<text>(?:\s*<!\[CDATA\[(.*?)\]\]>\s*)+</text>'
        def cdata_replacer(match):
            all_cdata = re.findall(r'<!\[CDATA\[(.*?)\]\]>', match.group(0), re.DOTALL)
            merged = ''.join(all_cdata)
            return f'<text><![CDATA[{merged}]]></text>'
        return re.sub(cdata_pattern, cdata_replacer, text, flags=re.DOTALL)
    content1 = merge_cdata(content1)
    with open("quiz_ruby_parentheses.xml", 'w', encoding='utf-8') as f:
        f.write(content1)

    # Format 2: HTML spans with styling
    print("Creating Format 2: HTML spans with styling")
    def ruby_to_html(match):
        kanji = match.group(1)
        hiragana = match.group(2)
        return f'<span style="border-top: 1px solid #666; font-size: 0.8em; position: relative;" title="{hiragana}">{kanji}</span>'

    content2 = re.sub(r'<ruby>([^<]*)<rt>([^<]*)</rt></ruby>', ruby_to_html, content)
    content2 = merge_cdata(content2)
    with open("quiz_ruby_html.xml", 'w', encoding='utf-8') as f:
        f.write(content2)

    # Format 3: Square brackets
    print("Creating Format 3: Square brackets kanji[hiragana]")
    def ruby_to_brackets(match):
        kanji = match.group(1)
        hiragana = match.group(2)
        return f"{kanji}[{hiragana}]"

    content3 = re.sub(r'<ruby>([^<]*)<rt>([^<]*)</rt></ruby>', ruby_to_brackets, content)
    content3 = merge_cdata(content3)
    with open("quiz_ruby_brackets.xml", 'w', encoding='utf-8') as f:
        f.write(content3)

    print("\nCreated 3 formats for testing:")
    print("1. quiz_ruby_parentheses.xml - 問題(もんだい)")
    print("2. quiz_ruby_html.xml - With HTML styling")
    print("3. quiz_ruby_brackets.xml - 問題[もんだい]")

def main():
    create_multiple_formats()

if __name__ == "__main__":
    main()
