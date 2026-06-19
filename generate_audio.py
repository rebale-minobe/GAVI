import os, json, sys, time
from pathlib import Path

API_KEY = os.environ.get("OPENAI_API_KEY", "")
VOICE = "alloy"
MODEL = "tts-1-hd"
SPEED = 0.85
WORDS_JSON = "data/words.json"
AUDIO_DIR = Path("assets/audio")

def main():
    if not API_KEY:
        print("APIキーが未設定です")
        sys.exit(1)
    from openai import OpenAI
    client = OpenAI(api_key=API_KEY)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    words = json.load(open(WORDS_JSON, encoding="utf-8"))["words"]
    total = len(words)
    print(f"{total}語の音声を生成（声:{VOICE} / {MODEL} / speed:{SPEED}）")
    made, skipped, failed = 0, 0, 0
    for i, w in enumerate(words, 1):
        wid, text = w["word_id"], w["english"]
        out = AUDIO_DIR / f"{wid}.mp3"
        if out.exists():
            skipped += 1; continue
        try:
            resp = client.audio.speech.create(model=MODEL, voice=VOICE, input=text, speed=SPEED)
            resp.stream_to_file(str(out))
            made += 1
            if i % 25 == 0 or made <= 5:
                print(f"  [{i}/{total}] OK {text}")
            time.sleep(0.3)
        except Exception as e:
            failed += 1
            print(f"  [{i}/{total}] NG {text}: {e}")
    print(f"完了: 生成{made} スキップ{skipped} 失敗{failed}")

if __name__ == "__main__":
    main()
