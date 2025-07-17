#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import re
import sys

def validate_xml_file(file_path):
    """Validate XML file and report issues"""
    print(f"Validating XML file: {file_path}")
    
    try:
        # Try to parse the XML
        tree = ET.parse(file_path)
        root = tree.getroot()
        print("✓ XML is well-formed")
        
        # Check for common issues
        issues = []
        
        # Read file content to check for issues
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for nested ruby tags
        nested_ruby_pattern = r'<ruby>[^<]*<ruby>'
        if re.search(nested_ruby_pattern, content):
            issues.append("Found nested ruby tags")
        
        # Check for malformed ruby tags
        malformed_ruby_pattern = r'<ruby>[^<]*</ruby>[^<]*</ruby>'
        if re.search(malformed_ruby_pattern, content):
            issues.append("Found malformed ruby tags")
        
        # Check for unclosed tags
        ruby_open = content.count('<ruby>')
        ruby_close = content.count('</ruby>')
        rt_open = content.count('<rt>')
        rt_close = content.count('</rt>')
        
        if ruby_open != ruby_close:
            issues.append(f"Mismatched ruby tags: {ruby_open} open, {ruby_close} close")
        
        if rt_open != rt_close:
            issues.append(f"Mismatched rt tags: {rt_open} open, {rt_close} close")
        
        # Check for empty text elements
        empty_text_pattern = r'<text>\s*</text>'
        empty_count = len(re.findall(empty_text_pattern, content))
        if empty_count > 0:
            print(f"Found {empty_count} empty text elements (this is normal)")
        
        if issues:
            print("\n⚠️  Issues found:")
            for issue in issues:
                print(f"  - {issue}")
        else:
            print("✓ No issues found")
        
        return len(issues) == 0
        
    except ET.ParseError as e:
        print(f"✗ XML Parse Error: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def fix_xml_file(input_file, output_file):
    """Fix common XML issues"""
    print(f"Fixing XML file: {input_file} -> {output_file}")
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Fix nested ruby tags
        # Pattern: <ruby>text<ruby>text<rt>reading</rt></ruby><rt>reading</rt></ruby>
        def fix_nested_ruby(match):
            # This is a complex fix - for now, just report
            return match.group(0)
        
        # Fix malformed ruby tags like: <ruby>text</ruby>text</ruby>
        malformed_pattern = r'(<ruby>[^<]*</ruby>[^<]*)</ruby>'
        content = re.sub(malformed_pattern, r'\1', content)
        
        # Fix double rt tags like: t>reading</rt></ruby><ruby><ruby>text<rt>reading</rt></ruby>
        double_rt_pattern = r't>([^<]*)</rt></ruby><ruby><ruby>([^<]*)<rt>([^<]*)</rt></ruby>'
        content = re.sub(double_rt_pattern, r't>\1</rt></ruby> <ruby>\2<rt>\3</rt></ruby>', content)
        
        # Save fixed content
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✓ XML file fixed")
        return True
        
    except Exception as e:
        print(f"✗ Error fixing file: {e}")
        return False

def main():
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_fixed.xml"
    output_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_clean.xml"
    
    # Validate original file
    if validate_xml_file(input_file):
        print("\nOriginal file is valid!")
    else:
        print("\nAttempting to fix issues...")
        if fix_xml_file(input_file, output_file):
            print(f"\nValidating fixed file: {output_file}")
            validate_xml_file(output_file)

if __name__ == "__main__":
    main()
