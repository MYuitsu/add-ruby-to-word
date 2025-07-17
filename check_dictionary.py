#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

# Load dictionary
with open('dictionary_full_jmdict.json', 'r', encoding='utf-8') as f:
    dictionary = json.load(f)

# Check if "生産" is in dictionary
if "生産" in dictionary:
    print(f"'生産' found in dictionary: {dictionary['生産']}")
else:
    print("'生産' NOT found in dictionary")

# Check similar words
for word in dictionary:
    if "生産" in word:
        print(f"Related word: {word} -> {dictionary[word]}")
        if len(word) > 2:
            break  # Just show a few examples
