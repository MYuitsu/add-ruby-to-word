#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Test full-width numbers
FULLWIDTH_NUMBER_PATTERN = re.compile(r'[\uff10-\uff19]')

# Test string with full-width number
test_string = "問題９ロット生産に関する記述として最も適切なものは次のうちどれか。"

# Find all full-width numbers
matches = FULLWIDTH_NUMBER_PATTERN.findall(test_string)
print(f"Full-width numbers found: {matches}")

# Check if string contains full-width numbers
has_fullwidth = bool(FULLWIDTH_NUMBER_PATTERN.search(test_string))
print(f"Contains full-width numbers: {has_fullwidth}")

# Test individual character
char_nine = "９"
print(f"Character '９' is full-width number: {bool(FULLWIDTH_NUMBER_PATTERN.search(char_nine))}")

# Test dictionary mapping
fullwidth_numbers = {
    '０': 'ゼロ', '１': 'いち', '２': 'に', '３': 'さん', '４': 'よん',
    '５': 'ご', '６': 'ろく', '７': 'なな', '８': 'はち', '９': 'きゅう'
}

print(f"Mapping for '９': {fullwidth_numbers.get('９', 'NOT FOUND')}")
