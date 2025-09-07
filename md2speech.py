#!/usr/bin/env python3
"""
md2speech_fast.py – многопроцессорный, кеширующий, без pydub
"""
import re, hashlib, pathlib, subprocess, tempfile, multiprocessing as mp
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm

CACHE_DIR  = pathlib.Path("tts_cache")
CACHE_DIR.mkdir(exist_ok=True)
VOICES     = {"ru": "ru-RU-SvetlanaNeural", "en": "en-US-AriaNeural"}
N_WORKERS  = min(12, mp.cpu_count())   # кол-во параллельных edge-tts

# ---------- утилиты ----------
def md5txt(text: str) -> str:
    return hashlib.md5(text.encode()).hexdigest()

def detect_lang(text: str) -> str:
    return "ru" if len(re.findall(r"[а-яё]", text, re.I)) / max(len(text), 1) > 0.35 else "en"

def split_md(md: str):
    md = re.sub(r"```.*?```", "", md, flags=re.S)
    md = re.sub(r"`[^`]+`", "", md)
    for p in re.split(r"\n{2,}", md.strip()):
        if (p := p.strip()) and not p.startswith("#"):
            yield p

# ---------- синтез ----------
def synth_one(args):
    text, lang, idx = args
    h = md5txt(text)
    out = CACHE_DIR / f"{h}_{lang}.mp3"
    if out.exists():
        return idx, out

    # 1. Убираем символы, которые ломают shell
    text = re.sub(r"[`$<>|;&()\\]", " ", text).strip()
    if not text:                       # 2. на всякий случай
        return idx, None

    voice = VOICES[lang]
    cmd = [
        "edge-tts",
        "--voice", voice,
        "--text", text,
        "--write-media", str(out),
        "--rate", "+0%",
        "--volume", "+0%"
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        # 3. понятное сообщение, но не падаем весь пул
        print(f"\n⚠️  edge-tts error on frag {idx}: {e.stderr[:120]}")
        return idx, None
    return idx, out

# ---------- склейка ----------
def concat_mp3(files: list[pathlib.Path], out: pathlib.Path):
    """Без перекодирования, за один проход ffmpeg."""
    list_path = out.with_suffix(".txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for fp in files:
            f.write(f"file '{fp.resolve()}'\n")
    subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", str(list_path), "-c", "copy", "-y", str(out)], check=True
    )
    list_path.unlink()

# ---------- main ----------
def md2speech(md_path: pathlib.Path, out_mp3: pathlib.Path):
    md_text = md_path.read_text(encoding="utf-8")
    paragraphs = list(split_md(md_text))
    jobs = [(p, detect_lang(p), i) for i, p in enumerate(paragraphs)]

    print(f"Синтез {len(jobs)} фрагментов, {N_WORKERS} workers…")
    files_ordered = [None] * len(jobs)    
    ok_count = 0
    with ProcessPoolExecutor(N_WORKERS) as ex:
        futures = {ex.submit(synth_one, j): j for j in jobs}
        for f in tqdm(as_completed(futures), total=len(futures), unit="frag"):
            idx, mp3_path = f.result()
            if mp3_path is not None:            # <-- успешно
                files_ordered[idx] = mp3_path
                ok_count += 1

    files_ordered = [f for f in files_ordered if f is not None]  # убираем None
    if ok_count == 0:
        sys.exit("Нет успешно синтезированных фрагментов – аудио не создано.")
        
    print("Склейка…")
    if not files_ordered:
        sys.exit("Нечего склеивать.")
    concat_mp3(files_ordered, out_mp3)
    concat_mp3(files_ordered, out_mp3)
    print("✅ Готово:", out_mp3.resolve())

if __name__ == "__main__":
    import argparse, sys
    ap = argparse.ArgumentParser()
    ap.add_argument("md", type=pathlib.Path)
    ap.add_argument("-o", "--out", type=pathlib.Path, default="speech.mp3")
    args = ap.parse_args()
    if not args.md.exists():
        sys.exit("Файл не найден")
    md2speech(args.md, args.out)