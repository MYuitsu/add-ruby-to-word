#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import shutil
import os

def create_clean_copy():
    """Create a clean copy with simple filename"""
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_fixed.xml"
    output_file = "quiz_with_ruby.xml"
    
    try:
        # Read with UTF-8 and write without BOM
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Write without BOM
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created clean copy: {output_file}")
        
        # Check file size
        size = os.path.getsize(output_file)
        print(f"✓ File size: {size} bytes")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def create_version_without_ruby():
    """Create a version without ruby tags for testing"""
    input_file = "平成 25 年前期 - ĐỀ NĂM 25 KÌ TRƯỚC_ruby_fixed.xml"
    output_file = "quiz_no_ruby.xml"
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove ruby tags but keep the text
        import re
        # Remove <ruby>text<rt>reading</rt></ruby> -> text
        content = re.sub(r'<ruby>([^<]*)<rt>[^<]*</rt></ruby>', r'\1', content)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Created version without ruby: {output_file}")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print("Creating clean copies for testing...")
    
    # Create clean copy with simple name
    create_clean_copy()
    
    # Create version without ruby tags
    create_version_without_ruby()
    
    print("\nTry importing these files:")
    print("1. quiz_with_ruby.xml (with ruby tags)")
    print("2. quiz_no_ruby.xml (without ruby tags)")

if __name__ == "__main__":
    main()
