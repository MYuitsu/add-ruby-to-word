import json
import re
from pathlib import Path

# =========================
# Regex
# =========================
KANJI_RE = re.compile(r'[\u4e00-\u9fff々]')
KANA_RE  = re.compile(r'[\u3040-\u309f\u30a0-\u30ffー]')

SMALL_KANA = set("ゃゅょぁぃぅぇぉゎャュョァィゥェォヮ")
PROLONG = "ー"


def is_kanji(ch: str) -> bool:
    return bool(KANJI_RE.fullmatch(ch or ""))


def is_kana(ch: str) -> bool:
    return bool(KANA_RE.fullmatch(ch or ""))


def split_to_moras(s: str):
    """Tách kana thành mora (đủ tốt để chia đều)."""
    moras = []
    for ch in (s or ""):
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
        ch = surface[i]
        if is_kana(ch) and not is_kanji(ch):
            j = i + 1
            while j < n and is_kana(surface[j]) and not is_kanji(surface[j]):
                j += 1
            runs.append((i, surface[i:j]))
            i = j
        else:
            i += 1
    return runs


def find_best_anchor(kana_run: str, reading: str, rp: int):
    """
    Tìm anchor của kana-run trong reading theo thứ tự.
    - Ưu tiên match đầy đủ.
    - Nếu không có: thử suffix/prefix từ dài -> ngắn.
    Return: (surface_offset_in_run, matched_str, r_from, r_to) hoặc None
    """
    pos = reading.find(kana_run, rp)
    if pos != -1:
        return (0, kana_run, pos, pos + len(kana_run))

    for L in range(len(kana_run) - 1, 0, -1):
        suf = kana_run[-L:]
        pos = reading.find(suf, rp)
        if pos != -1:
            off = len(kana_run) - L
            return (off, suf, pos, pos + L)

        pre = kana_run[:L]
        pos = reading.find(pre, rp)
        if pos != -1:
            return (0, pre, pos, pos + L)

    return None


def infer_segments(surface: str, reading: str):
    """
    Suy luận segments dựa trên kana anchor trong surface.
    - Không fallback ngay khi 1 kana-run không match -> skip kana-run đó.
    - segments tạo theo "vùng" để tránh duplicate rt cho nhiều kanji-run.
    Return:
      segments: list of (s0, s1, rt_slice)
      skipped_any: bool
    """
    kana_runs = extract_kana_runs(surface)
    anchors = []
    rp = 0
    skipped_any = False

    for si, kana in kana_runs:
        a = find_best_anchor(kana, reading, rp)
        if a is None:
            skipped_any = True
            continue
        off, sub, r0, r1 = a
        anchors.append((si + off, sub, r0, r1))
        rp = r1

    segments = []
    prev_s = 0
    prev_r = 0

    def add_region(s_from, s_to, r_from, r_to):
        """Add 1 segment cho vùng [s_from, s_to) nếu vùng đó có kanji."""
        if s_from >= s_to or r_from > r_to:
            return
        region = surface[s_from:s_to]
        if any(is_kanji(ch) for ch in region):
            segments.append((s_from, s_to, reading[r_from:r_to]))

    for (si, sub, r0, r1) in anchors:
        add_region(prev_s, si, prev_r, r0)
        prev_s = si + len(sub)
        prev_r = r1

    add_region(prev_s, len(surface), prev_r, len(reading))

    # Nếu không tạo được segment nào nhưng surface có kanji -> fallback 1 segment
    if not segments and any(is_kanji(ch) for ch in surface):
        segments = [(0, len(surface), reading)]
        skipped_any = True

    return segments, skipped_any


def segments_to_map(surface: str, segments, full_reading: str):
    """
    Chuyển segments -> map per-kanji.
    - Nếu 1 segment có nhiều kanji: chia reading theo mora đều (uncertain=True)
    - Nếu thiếu mora: gán cả rt cho kanji đầu (uncertain=True)
    - Dedup theo index i (giữ object, không xoá object rt:"")
    - Nếu uncertain và rt TRÙNG NHAU -> chữ sau rt:""
      ✅ Nhưng nếu đã có chữ sau rt:"" (tức là "không biết") -> chữ đầu giữ FULL reading
    """
    mapping = []
    uncertain = False

    for s0, s1, rt in segments:
        if rt is None:
            continue
        rt = str(rt)

        kanjis = [(i, surface[i]) for i in range(s0, s1) if is_kanji(surface[i])]
        if not kanjis:
            continue

        if len(kanjis) == 1:
            i, ch = kanjis[0]
            mapping.append({"i": i, "ch": ch, "rt": rt})
            continue

        moras = split_to_moras(rt)
        k = len(kanjis)

        if len(moras) < k:
            uncertain = True
            i, ch = kanjis[0]
            mapping.append({"i": i, "ch": ch, "rt": rt})
            # không auto-add các chữ sau (vì không biết chia)
            continue

        uncertain = True
        base = len(moras) // k
        rem = len(moras) % k

        idx = 0
        for t in range(k):
            take = base + (1 if t < rem else 0)
            part = "".join(moras[idx: idx + take])
            idx += take
            i, ch = kanjis[t]
            mapping.append({"i": i, "ch": ch, "rt": part})

    # dedup by i (giữ phần tử đầu tiên theo index)
    seen_i = set()
    dedup = []
    for m in mapping:
        if m["i"] in seen_i:
            continue
        seen_i.add(m["i"])
        dedup.append(m)

    dedup.sort(key=lambda x: x["i"])

    # ✅ Rule: rt trùng -> chữ sau để trống, nhưng nếu đã trống thì chữ đầu giữ FULL reading
    blanked_any = False
    if uncertain:
        prev_rt = None
        for m in dedup:
            cur = (m.get("rt") or "")
            if cur == "":
                continue
            if prev_rt is not None and cur == prev_rt:
                m["rt"] = ""          # giữ object, chỉ blank rt
                blanked_any = True
            else:
                prev_rt = cur

        # Nếu có blank => coi như "các chữ sau không biết" => chữ đầu giữ full reading
        if blanked_any:
            for m in dedup:
                if (m.get("rt") or "").strip():
                    m["rt"] = full_reading
                    break

    return dedup, uncertain


def convert(in_path: str, out_path: str):
    src = json.loads(Path(in_path).read_text(encoding="utf-8"))
    dst = {}

    total = 0
    kept = 0

    for surface, reading in src.items():
        total += 1
        if not isinstance(surface, str) or not isinstance(reading, str) or not reading:
            continue
        if not any(is_kanji(ch) for ch in surface):
            continue

        segments, skipped_any = infer_segments(surface, reading)
        mapping, uncertain_map = segments_to_map(surface, segments, reading)

        dst[surface] = {
            "rt": reading,
            "map": mapping,
            "segments": [{"s": [s0, s1], "rt": rt} for (s0, s1, rt) in segments],
            "uncertain": bool(skipped_any or uncertain_map),
        }
        kept += 1

    Path(out_path).write_text(
        json.dumps(dst, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Converted: {kept}/{total} entries -> {out_path}")


if __name__ == "__main__":
    convert("dictionary 20250816 2301.json", "dict_struct.json")
