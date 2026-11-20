import re
import unicodedata


def normalize_text(t: str) -> str:
    if not t:
        return ""
    t = t.lower()
    t = unicodedata.normalize("NFD", t)
    t = "".join(ch for ch in t if unicodedata.category(ch) != "Mn")
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\r\n", "\n", t)
    t = re.sub(r"\n{2,}", "\n", t)
    return t.strip()


def split_lines(t: str):
    lines = [x.strip() for x in t.split("\n")]
    return [l for l in lines if l]
