import json

INP = "dict_struct.json"
OUT = "dict_struct.view.json"

def j(x):
    return json.dumps(x, ensure_ascii=False)

def j_compact(x):
    return json.dumps(x, ensure_ascii=False, separators=(",", ":"))

def slim_value(v: dict) -> dict:
    """
    Nếu dict của bạn còn 'segments', 'uncertain'... và bạn chỉ muốn rt+map để đọc:
    giữ lại đúng 2 field này.
    """
    if not isinstance(v, dict):
        return v
    return {
        "rt": v.get("rt"),
        "map": v.get("map"),
    }

def write_custom(d: dict, path: str):
    items = list(d.items())

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("{\n")

        for idx, (k, v) in enumerate(items):
            comma = "," if idx < len(items) - 1 else ""

            # ✅ nếu muốn chỉ rt+map để nhìn cho gọn
            if isinstance(v, dict):
                v = slim_value(v)

            key = j(k)

            # Rule inline: dict chỉ có rt+map và map <= 1 phần tử
            inline = (
                isinstance(v, dict)
                and set(v.keys()) <= {"rt", "map"}
                and isinstance(v.get("map"), list)
                and len(v["map"]) <= 1
            )

            if inline:
                f.write(f"  {key}: {j_compact(v)}{comma}\n")
                continue

            # Multi-line format (giống ảnh)
            if isinstance(v, dict) and "rt" in v and "map" in v and isinstance(v["map"], list):
                f.write(f"  {key}: {{\n")
                f.write(f"    \"rt\": {j(v.get('rt'))},\n")
                f.write(f"    \"map\": [\n")

                mp = v.get("map") or []
                for mi, m in enumerate(mp):
                    m_comma = "," if mi < len(mp) - 1 else ""
                    f.write(f"      {j_compact(m)}{m_comma}\n")

                f.write("    ]\n")
                f.write(f"  }}{comma}\n")
                continue

            # Fallback: các kiểu khác (in compact 1 dòng)
            f.write(f"  {key}: {j_compact(v)}{comma}\n")

        f.write("}\n")

def main():
    with open(INP, "r", encoding="utf-8") as f:
        d = json.load(f)

    write_custom(d, OUT)
    print("Wrote:", OUT)

if __name__ == "__main__":
    main()

