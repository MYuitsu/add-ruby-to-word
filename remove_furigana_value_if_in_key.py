import json
import re

def extract_hiragana_chunks(text):
    # Tìm tất cả các cụm hiragana liên tiếp trong chuỗi
    return re.findall(r'[\u3040-\u309F]+', text)

def remove_hiragana_chunks_from_value(key, value):
    hiragana_chunks = extract_hiragana_chunks(key)
    if isinstance(value, list):
        new_values = []
        for v in value:
            new_v = v
            for chunk in hiragana_chunks:
                new_v = new_v.replace(chunk, "")
            new_v = new_v.strip()
            if new_v:  # chỉ giữ lại nếu còn ký tự
                new_values.append(new_v)
        return new_values if new_values else None
    else:
        new_v = value
        for chunk in hiragana_chunks:
            new_v = new_v.replace(chunk, "")
        new_v = new_v.strip()
        return new_v if new_v else None

def process_dictionary(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    new_dict = {}
    for key, value in data.items():
        new_value = remove_hiragana_chunks_from_value(key, value)
        if new_value:
            new_dict[key] = new_value

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(new_dict, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    process_dictionary('dictionary_full_jmdict.json', 'dictionary_hiragana_chunks_removed_from_value.json')