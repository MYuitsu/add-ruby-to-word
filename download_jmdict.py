import requests
import gzip
import xml.etree.ElementTree as ET
import json
import os
from typing import Dict, Set
import re
import time

def download_jmdict():
    """Tải JMdict từ server chính thức"""
    print("=== Bắt đầu download JMdict ===")
    url = "http://ftp.edrdg.org/pub/Nihongo/JMdict_e.gz"
    print(f"URL: {url}")
    
    try:
        print("Bắt đầu request...")
        response = requests.get(url, stream=True)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        
        print("Bắt đầu ghi file...")
        total_size = 0
        with open("JMdict_e.gz", "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                total_size += len(chunk)
                if total_size % (5*1024*1024) == 0:  # Mỗi 5MB
                    print(f"Đã tải {total_size // (1024*1024)} MB")
        
        print(f"Tổng kích thước file: {total_size // (1024*1024)} MB")
        print("Đã tải xong JMdict_e.gz")
        return True
    except Exception as e:
        print(f"Lỗi khi tải JMdict: {e}")
        return False

def parse_jmdict_to_dict_full():
    """Parse toàn bộ JMdict XML và tạo dictionary kanji-hiragana"""
    print("=== Bắt đầu parse toàn bộ JMdict ===")
    
    # Kiểm tra file tồn tại
    if not os.path.exists("JMdict_e.gz"):
        print("File JMdict_e.gz không tồn tại!")
        return {}
    
    file_size = os.path.getsize("JMdict_e.gz")
    print(f"Kích thước file JMdict_e.gz: {file_size // (1024*1024)} MB")
    
    kanji_dict = {}
    entry_count = 0
    line_count = 0
    error_count = 0
    successful_entries = 0
    start_time = time.time()
    
    try:
        print("Mở file gzip...")
        with gzip.open("JMdict_e.gz", "rt", encoding="utf-8") as f:
            print("File đã mở thành công")
            
            # Đọc từng dòng để xử lý file lớn
            current_entry = ""
            in_entry = False
            
            print("Bắt đầu đọc và parse toàn bộ file...")
            print("(Quá trình này có thể mất 10-30 phút tùy vào tốc độ máy)")
            
            for line in f:
                line_count += 1
                
                # Progress update mỗi 100,000 dòng
                if line_count % 100000 == 0:
                    elapsed = time.time() - start_time
                    print(f"Đã đọc {line_count:,} dòng | Entries thành công: {successful_entries:,} | Tổng từ: {len(kanji_dict):,} | Thời gian: {elapsed:.1f}s")
                
                if "<entry>" in line:
                    in_entry = True
                    current_entry = line
                    
                elif "</entry>" in line:
                    current_entry += line
                    in_entry = False
                    entry_count += 1
                    
                    # Parse entry này với fix entity
                    try:
                        entry_dict = parse_single_entry_fixed(current_entry)
                        if entry_dict:
                            kanji_dict.update(entry_dict)
                            successful_entries += 1
                            
                            # Progress update cho entries thành công
                            if successful_entries % 5000 == 0:
                                elapsed = time.time() - start_time
                                rate = successful_entries / elapsed if elapsed > 0 else 0
                                print(f"✓ {successful_entries:,} entries thành công | {len(kanji_dict):,} từ | {rate:.1f} entries/sec")
                            
                    except Exception as e:
                        error_count += 1
                        if error_count <= 5:  # Chỉ in 5 lỗi đầu
                            print(f"Lỗi parse entry {entry_count}: {e}")
                    
                    current_entry = ""
                elif in_entry:
                    current_entry += line
    
    except Exception as e:
        print(f"Lỗi khi parse JMdict: {e}")
        return {}
    
    elapsed_time = time.time() - start_time
    print(f"\n=== Kết thúc parse toàn bộ JMdict ===")
    print(f"Tổng thời gian: {elapsed_time:.1f} giây ({elapsed_time/60:.1f} phút)")
    print(f"Tổng dòng đọc: {line_count:,}")
    print(f"Tổng entries trong file: {entry_count:,}")
    print(f"Entries parse thành công: {successful_entries:,}")
    print(f"Entries lỗi: {error_count:,}")
    print(f"Tổng từ kanji-hiragana tạo được: {len(kanji_dict):,}")
    print(f"Tỷ lệ thành công: {successful_entries/entry_count*100:.1f}%" if entry_count > 0 else "0%")
    
    return kanji_dict

def parse_single_entry_fixed(entry_xml: str) -> Dict[str, str]:
    """Parse một entry XML thành dictionary - fix entity problems"""
    try:
        # Remove XML entities that cause problems
        cleaned_xml = clean_xml_entities(entry_xml)
        
        root = ET.fromstring(cleaned_xml)
        
        # Lấy các kanji và reading
        kanjis = []
        readings = []
        
        # Lấy kanji (keb = kanji element)
        for keb in root.findall(".//keb"):
            if keb.text and has_kanji(keb.text):
                kanjis.append(keb.text)
        
        # Lấy reading (reb = reading element)
        for reb in root.findall(".//reb"):
            if reb.text and is_hiragana(reb.text):
                readings.append(reb.text)
        
        # Tạo dictionary từ kanji-reading pairs
        result = {}
        if kanjis and readings:
            # Ghép kanji đầu tiên với reading đầu tiên
            primary_kanji = kanjis[0]
            primary_reading = readings[0]
            
            result[primary_kanji] = primary_reading
            
            # Thêm các variant khác nếu có
            for kanji in kanjis[1:]:
                if has_kanji(kanji):
                    result[kanji] = primary_reading
        
        return result
        
    except Exception as e:
        return {}

def clean_xml_entities(xml_string: str) -> str:
    """Remove XML entities that cause parsing problems"""
    # Remove entities in <pos>, <misc>, etc.
    entities_to_remove = [
        r'<pos>&[^;]+;</pos>',
        r'<misc>&[^;]+;</misc>',
        r'<field>&[^;]+;</field>',
        r'<dial>&[^;]+;</dial>',
        r'<s_inf>&[^;]+;</s_inf>',
        r'<ke_inf>&[^;]+;</ke_inf>',
        r'<re_inf>&[^;]+;</re_inf>',
        r'<lsource>&[^;]+;</lsource>',
        r'<ant>&[^;]+;</ant>',
        r'<xref>&[^;]+;</xref>'
    ]
    
    cleaned = xml_string
    for pattern in entities_to_remove:
        cleaned = re.sub(pattern, '', cleaned)
    
    # Remove any remaining entities
    cleaned = re.sub(r'&[^;]+;', '', cleaned)
    
    return cleaned

def is_hiragana(text: str) -> bool:
    """Kiểm tra xem text có phải toàn hiragana không"""
    if not text:
        return False
    
    for char in text:
        if not (0x3041 <= ord(char) <= 0x3096):
            return False
    
    return True

def has_kanji(text: str) -> bool:
    """Kiểm tra xem text có chứa kanji không"""
    if not text:
        return False
    
    for char in text:
        if 0x4e00 <= ord(char) <= 0x9faf:  # Kanji unicode range
            return True
    
    return False

def merge_with_existing_dict(new_dict: Dict[str, str]) -> Dict[str, str]:
    """Gộp với dictionary hiện có"""
    print(f"=== Merge dictionaries ===")
    print(f"Dictionary mới: {len(new_dict):,} từ")
    
    existing_dict = {}
    
    if os.path.exists("dictionary.json"):
        try:
            with open("dictionary.json", "r", encoding="utf-8") as f:
                existing_dict = json.load(f)
            print(f"Dictionary hiện có: {len(existing_dict):,} từ")
        except Exception as e:
            print(f"Không thể load dictionary hiện có: {e}")
    else:
        print("Không có dictionary.json hiện tại")
    
    # Gộp dictionaries (ưu tiên từ mới, nhưng giữ lại từ cũ nếu không conflict)
    merged = existing_dict.copy()
    merged.update(new_dict)  # New dict sẽ overwrite existing
    
    print(f"Dictionary sau merge: {len(merged):,} từ")
    print(f"Đã thêm {len(merged) - len(existing_dict):,} từ mới")
    return merged

def save_dictionary(dictionary: Dict[str, str], filename: str):
    """Lưu dictionary vào file"""
    print(f"=== Lưu dictionary vào {filename} ===")
    print(f"Số từ: {len(dictionary):,}")
    
    try:
        # Backup file cũ nếu có
        if os.path.exists(filename):
            backup_name = filename.replace('.json', '_backup.json')
            os.rename(filename, backup_name)
            print(f"Đã backup file cũ thành {backup_name}")
        
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(dictionary, f, ensure_ascii=False, indent=2, sort_keys=True)
        
        file_size = os.path.getsize(filename)
        print(f"Đã lưu thành công: {filename} ({file_size // 1024} KB)")
        return True
    except Exception as e:
        print(f"Lỗi khi lưu dictionary: {e}")
        return False

def get_jmdict_statistics():
    """Xem thống kê về file JMdict"""
    if not os.path.exists("JMdict_e.gz"):
        print("File JMdict_e.gz không tồn tại!")
        return
    
    print("=== Thống kê JMdict ===")
    file_size = os.path.getsize("JMdict_e.gz")
    print(f"Kích thước file: {file_size // (1024*1024)} MB")
    
    try:
        entry_count = 0
        line_count = 0
        
        with gzip.open("JMdict_e.gz", "rt", encoding="utf-8") as f:
            for line in f:
                line_count += 1
                if "<entry>" in line:
                    entry_count += 1
                
                if line_count % 100000 == 0:
                    print(f"Đã đọc {line_count:,} dòng, tìm thấy {entry_count:,} entries")
        
        print(f"Tổng số dòng: {line_count:,}")
        print(f"Tổng số entries: {entry_count:,}")
        
    except Exception as e:
        print(f"Lỗi đọc file: {e}")

def main():
    print("=== JMdict Full Dictionary Generator ===")
    print("1. Tải JMdict từ internet")
    print("2. Parse toàn bộ JMdict (TẤT CẢ entries)")
    print("3. Xem thống kê JMdict")
    print("4. Tải + Parse toàn bộ (All-in-one)")
    print("5. Tạo dictionary mẫu")
    
    choice = input("Chọn option (1/2/3/4/5): ").strip()
    
    if choice == "1":
        # Chỉ tải JMdict
        if download_jmdict():
            print("Đã tải xong JMdict. Chạy lại và chọn option 2 để parse.")
        else:
            print("Không thể tải JMdict")
    
    elif choice == "2":
        # Parse toàn bộ JMdict
        if os.path.exists("JMdict_e.gz"):
            print("⚠️  Cảnh báo: Quá trình này sẽ parse TẤT CẢ JMdict (~200,000+ entries)")
            print("   Có thể mất 10-30 phút và tạo ra dictionary với 50,000+ từ")
            confirm = input("Bạn có chắc muốn tiếp tục? (y/N): ").strip().lower()
            
            if confirm == 'y':
                new_dict = parse_jmdict_to_dict_full()
                
                if new_dict:
                    merged_dict = merge_with_existing_dict(new_dict)
                    
                    # Lưu vào nhiều file
                    save_dictionary(merged_dict, "dictionary_full_jmdict.json")
                    save_dictionary(merged_dict, "dictionary.json")
                    
                    print(f"\n🎉 Hoàn thành! Dictionary với {len(merged_dict):,} từ đã được tạo.")
                    print("📁 Files đã tạo:")
                    print("   - dictionary_full_jmdict.json (full dictionary)")
                    print("   - dictionary.json (để sử dụng)")
                else:
                    print("Không thể parse JMdict")
            else:
                print("Đã hủy")
        else:
            print("File JMdict_e.gz không tồn tại. Chọn option 1 để tải trước.")
    
    elif choice == "3":
        # Xem thống kê
        get_jmdict_statistics()
    
    elif choice == "4":
        # All-in-one
        print("⚠️  Cảnh báo: Sẽ tải và parse toàn bộ JMdict")
        print("   Quá trình có thể mất 30-60 phút")
        confirm = input("Bạn có chắc muốn tiếp tục? (y/N): ").strip().lower()
        
        if confirm == 'y':
            if download_jmdict():
                new_dict = parse_jmdict_to_dict_full()
                
                if new_dict:
                    merged_dict = merge_with_existing_dict(new_dict)
                    save_dictionary(merged_dict, "dictionary_full_jmdict.json")
                    save_dictionary(merged_dict, "dictionary.json")
                    
                    print(f"\n🎉 Hoàn thành! Dictionary với {len(merged_dict):,} từ đã được tạo.")
                else:
                    print("Không thể parse JMdict")
            else:
                print("Không thể tải JMdict")
        else:
            print("Đã hủy")
    
    elif choice == "5":
        # Tạo dictionary mẫu (không thay đổi)
        from download_jmdict import create_sample_dict
        sample_dict = create_sample_dict()
        merged_dict = merge_with_existing_dict(sample_dict)
        
        save_dictionary(merged_dict, "dictionary_sample.json")
        save_dictionary(merged_dict, "dictionary.json")
        print(f"Đã tạo dictionary mẫu với {len(merged_dict):,} từ!")
    
    else:
        print("Option không hợp lệ")

if __name__ == "__main__":
    main()