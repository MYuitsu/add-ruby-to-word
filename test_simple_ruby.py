#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

# Full-width numbers mapping
fullwidth_numbers = {
    '０': 'ゼロ', '１': 'いち', '２': 'に', '３': 'さん', '４': 'よん',
    '５': 'ご', '６': 'ろく', '７': 'なな', '８': 'はち', '９': 'きゅう'
}

FULLWIDTH_NUMBER_PATTERN = re.compile(r'[\uff10-\uff19]')

def add_ruby_to_text_simple(text):
    """Simplified version to test number processing"""
    # Simple replacement for testing
    if "問題９" in text:
        text = text.replace("問題９", "<ruby>問題<rt>もんだい</rt></ruby><ruby>９<rt>きゅう</rt></ruby>")
    elif "問題" in text:
        text = text.replace("問題", "<ruby>問題<rt>もんだい</rt></ruby>")
    return text

# Test
test_text = "問題９ ロット生産に関する記述として最も適切なものは、次のうちどれか。"
result = add_ruby_to_text_simple(test_text)
print(f"Original: {test_text}")
print(f"Result: {result}")

# Test if "問題９" is in the text
print(f"Contains '問題９': {'問題９' in test_text}")
print(f"Contains '問題': {'問題' in test_text}")

# Character-by-character check
print("\nCharacter analysis:")
for i, char in enumerate(test_text[:10]):
    print(f"Position {i}: '{char}' (Unicode: {ord(char)})")
