"""Extract text from PDF using stdlib only (best-effort, fast)."""
import os
import re
import zlib


def decode_pdf_string(raw: bytes) -> str:
    s = raw.replace(b"\\n", b"\n").replace(b"\\r", b"\r").replace(b"\\t", b"\t")
    s = s.replace(b"\\(", b"(").replace(b"\\)", b")").replace(b"\\\\", b"\\")
    try:
        return s.decode("utf-8")
    except UnicodeDecodeError:
        return s.decode("latin-1", errors="replace")


def strings_from_bytes(blob: bytes) -> list[str]:
    out: list[str] = []
    for m in re.finditer(rb"\((?:\\.|[^\\()])*\)", blob):
        out.append(decode_pdf_string(m.group(0)[1:-1]))
    return out


def extract_pdf_text(path: str, max_streams: int = 400) -> str:
    with open(path, "rb") as f:
        data = f.read()

    parts: list[str] = []
    n = 0
    pos = 0
    marker = b"stream"
    while n < max_streams:
        idx = data.find(marker, pos)
        if idx == -1:
            break
        start = idx + len(marker)
        if start < len(data) and data[start : start + 2] in (b"\r\n", b"\n"):
            start += 2 if data[start : start + 2] == b"\r\n" else 1
        end = data.find(b"endstream", start)
        if end == -1:
            break
        raw = data[start:end]
        if raw.endswith(b"\r\n"):
            raw = raw[:-2]
        elif raw.endswith(b"\n"):
            raw = raw[:-1]
        pos = end + 9
        n += 1
        if len(raw) > 2_000_000:
            continue
        try:
            dec = zlib.decompress(raw)
        except Exception:
            parts.extend(strings_from_bytes(raw))
            continue
        parts.extend(strings_from_bytes(dec))

    text = " ".join(parts)
    return re.sub(r"\s+", " ", text).strip()


def main() -> None:
    folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(folder, "extracted")
    os.makedirs(out_dir, exist_ok=True)
    for name in sorted(os.listdir(folder)):
        if not name.lower().endswith(".pdf"):
            continue
        path = os.path.join(folder, name)
        text = extract_pdf_text(path)
        slug = name.replace(".pdf", "").replace(" ", "_")
        out_path = os.path.join(out_dir, slug + ".txt")
        with open(out_path, "w", encoding="utf-8") as out:
            out.write(text)
        print(name, len(text), "chars")


if __name__ == "__main__":
    main()
