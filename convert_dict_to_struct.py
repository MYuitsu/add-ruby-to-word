import json
import re
from pathlib import Path

KANJI_RE = re.compile(r'[\u4e00-\u9fff々]')
KANA_RE  = re.compile(r'[\u3040-\u309f\u30a0-\u30ffー]')

SMALL_KANA = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")
PROLONG = "ー"

def is_kanji(ch: str) -> bool:
    return bool(KANJI_RE.fullmatch(ch))

def is_kana(ch: str) -> bool:
    return bool(KANA_RE.fullmatch(ch))

def split_to_moras(s: str):
    """Tách kana thành mora (đủ tốt để chia đều)."""
    moras = []
    for ch in s:
        if not moras:
            moras.append(ch)
            continue
        if ch in SMALL_KANA or ch == PROLONG:
            moras[-1] += ch
        else:
            moras.append(ch)
    return moras

def extract_kana_runs(surface: str):
    """Lấy các đoạn kana liên tiếp trong surface: [(start_idx, kana_str), ...]"""
    runs = []
    i = 0
    n = len(surface)
    while i < n:
        if is_kana(surface[i]) and not is_kanji(surface[i]):
            j = i + 1
            while j < n and is_kana(surface[j]) and not is_kanji(surface[j]):
                j += 1
            runs.append((i, surface[i:j]))
            i = j
        else:
            i += 1
    return runs

def infer_segments(surface: str, reading: str):
    """
    Suy luận segments cho các cụm kanji dựa trên kana anchor trong surface.
    Return: list of (start_idx, end_idx_excl, rt_slice)
    """
    kana_runs = extract_kana_runs(surface)

    # Tìm các anchor kana trong reading theo thứ tự
    anchors = []
    rp = 0
    for si, kana in kana_runs:
        pos = reading.find(kana, rp)
        if pos == -1:
            # Không tìm thấy anchor -> bỏ cơ chế anchor (fallback)
            return fallback_segment(surface, reading)
        anchors.append((si, kana, pos, pos + len(kana)))
        rp = pos + len(kana)

    segments = []
    prev_s = 0
    prev_r = 0

    # helper: add segment cho region [s_from, s_to) và reading [r_from, r_to)
    def add_region(s_from, s_to, r_from, r_to):
        if s_from >= s_to:
            return
        region = surface[s_from:s_to]
        rt = reading[r_from:r_to]
        # tìm các run kanji liên tiếp trong region
        idx = 0
        while idx < len(region):
            if is_kanji(region[idx]):
                j = idx + 1
                while j < len(region) and is_kanji(region[j]):
                    j += 1
                # run kanji: region[idx:j]
                segments.append((s_from + idx, s_from + j, rt))
                idx = j
            else:
                idx += 1

    for (si, kana, r_from, r_to) in anchors:
        # region trước kana anchor
        add_region(prev_s, si, prev_r, r_from)

        # vùng kana itself: bỏ qua (không ruby)
        prev_s = si + len(kana)
        prev_r = r_to

    # tail
    add_region(prev_s, len(surface), prev_r, len(reading))
    return segments

def fallback_segment(surface: str, reading: str):
    """Fallback: gom tất cả kanji trong surface thành 1 segment đọc toàn bộ."""
    # lấy run kanji đầu tiên đến cuối (thực tế: gom các run kanji liên tiếp)
    segments = []
    i = 0
    n = len(surface)
    while i < n:
        if is_kanji(surface[i]):
            j = i + 1
            while j < n and is_kanji(surface[j]):
                j += 1
            segments.append((i, j, reading))
            i = j
        else:
            i += 1
    return segments

def segments_to_map(surface: str, segments):
    """
    Chuyển segments -> map per-kanji.
    Nếu 1 segment có nhiều kanji:
      - chia reading theo mora đều cho số kanji (uncertain=True)
    """
    mapping = []
    uncertain = False

    for s0, s1, rt in segments:
        kanjis = [ (i, surface[i]) for i in range(s0, s1) if is_kanji(surface[i]) ]
        if not kanjis:
            continue

        if len(kanjis) == 1:
            i, ch = kanjis[0]
            mapping.append({"i": i, "ch": ch, "rt": rt})
            continue

        # nhiều kanji trong 1 segment -> chia đều mora
        moras = split_to_moras(rt)
        if len(moras) < len(kanjis):
            # không đủ để chia -> gán cả rt cho run đầu (vẫn uncertain)
            uncertain = True
            i, ch = kanjis[0]
            mapping.append({"i": i, "ch": ch, "rt": rt})
            continue

        uncertain = True
        k = len(kanjis)
        base = len(moras) // k
        rem  = len(moras) % k

        idx = 0
        for t in range(k):
            take = base + (1 if t < rem else 0)
            part = "".join(moras[idx: idx + take])
            idx += take
            i, ch = kanjis[t]
            mapping.append({"i": i, "ch": ch, "rt": part})

    return mapping, uncertain

def convert(in_path: str, out_path: str):
    src = json.loads(Path(in_path).read_text(encoding="utf-8"))
    dst = {}

    for surface, reading in src.items():
        if not isinstance(reading, str):
            continue

        segments = infer_segments(surface, reading)
        mapping, uncertain = segments_to_map(surface, segments)

        # map dùng index theo surface gốc -> đổi về index tương đối 0..len-1 nếu bạn muốn:
        # (hiện tại để i theo surface gốc, dễ apply)
        dst[surface] = {
            "rt": reading,
            "map": mapping,
            "segments": [{"s": [s0, s1], "rt": rt} for (s0, s1, rt) in segments],
            "uncertain": uncertain
        }

    Path(out_path).write_text(json.dumps(dst, ensure_ascii=False, indent=2), encoding="utf-8")
    print("Converted:", len(dst), "entries ->", out_path)

if __name__ == "__main__":
    convert("dictionary 20250816 2301.json", "dict_struct.json")
