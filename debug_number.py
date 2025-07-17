#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Test patterns
FULLWIDTH_NUMBER_PATTERN = re.compile(r'[\uff10-\uff19]')

# Test text
test_text = "問題９ ロット生産に関する記述として最も適切なものは、次のうちどれか。"

print(f"Original text: {test_text}")

# Find "問題" position
pos = test_text.find("問題")
print(f"Position of 問題: {pos}")

# Check character after "問題"
if pos != -1:
    end_pos = pos + 2  # "問題" has 2 characters
    if end_pos < len(test_text):
        next_char = test_text[end_pos]
        print(f"Character after 問題: '{next_char}'")
        print(f"Is full-width number: {bool(FULLWIDTH_NUMBER_PATTERN.match(next_char))}")
        
        # Check Unicode value
        print(f"Unicode value: {ord(next_char)}")
        print(f"Expected full-width 9: {ord('９')}")
        
        # Test manual pattern
        is_fw_num = '\uff10' <= next_char <= '\uff19'
        print(f"Manual check: {is_fw_num}")
