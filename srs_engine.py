"""
srs_engine.py - GAVI 記憶定着エンジン

間隔反復（SRS）、今日のミッション計算、ストリーク管理、カレンダー生成
科学的根拠: 1→3→7→14→30日の間隔反復で長期記憶に定着
"""

import json
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional

DATA_DIR = Path(__file__).parent / "data"
WORDS_FILE = DATA_DIR / "words.json"
STATE_FILE = DATA_DIR / "srs_state.json"


# ============================================================
# データ読み書き
# ============================================================

def load_words() -> List[Dict]:
    with open(WORDS_FILE, encoding="utf-8") as f:
        return json.load(f)["words"]


def save_words(words: List[Dict]):
    with open(WORDS_FILE, "w", encoding="utf-8") as f:
        json.dump({"words": words}, f, ensure_ascii=False, indent=2)


def load_state() -> Dict:
    with open(STATE_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_state(state: Dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def today_str() -> str:
    """今日の日付を YYYY-MM-DD で返す"""
    return date.today().isoformat()


# ============================================================
# 今日のミッション計算
# ============================================================

def get_today_mission(target_date: Optional[str] = None) -> Dict:
    """
    今日のミッション（新規＋復習）を計算

    Returns:
        Dict: {
            "new_words": [単語...],      # 今日の新規（最大25語）
            "review_words": [単語...],   # 今日の復習（SRSで選出、最大40語）
            "new_count": int,
            "review_count": int
        }
    """
    if target_date is None:
        target_date = today_str()

    words = load_words()
    state = load_state()
    settings = state["settings"]
    new_per_day = settings["new_words_per_day"]
    review_max = settings["review_max_per_day"]

    # --- 復習対象: next_review_date が今日以前の単語 ---
    review_candidates = []
    for w in words:
        nrd = w.get("next_review_date")
        if nrd is not None and w.get("srs_level", 0) >= 1:
            if nrd <= target_date:
                review_candidates.append(w)

    # 優先順位: 不正解が多い順 → 復習日が古い順
    review_candidates.sort(
        key=lambda w: (-w.get("wrong_count", 0), w.get("next_review_date", ""))
    )
    review_words = review_candidates[:review_max]

    # --- 新規対象: srs_level 0 かつ未学習（learned_date が None）---
    new_candidates = [
        w for w in words
        if w.get("srs_level", 0) == 0 and w.get("learned_date") is None
    ]
    new_words = new_candidates[:new_per_day]

    return {
        "new_words": new_words,
        "review_words": review_words,
        "new_count": len(new_words),
        "review_count": len(review_words),
        "review_overflow": max(0, len(review_candidates) - review_max),
    }


def get_today_mission_by_categories(categories: List[str], target_date: Optional[str] = None) -> Dict:
    """
    指定カテゴリーから新規単語を選ぶ版（復習は全カテゴリー対象）
    """
    if target_date is None:
        target_date = today_str()

    words = load_words()
    state = load_state()
    new_per_day = state["settings"]["new_words_per_day"]
    review_max = state["settings"]["review_max_per_day"]

    # 復習は全カテゴリーから
    review_candidates = [
        w for w in words
        if w.get("next_review_date") and w.get("srs_level", 0) >= 1
        and w["next_review_date"] <= target_date
    ]
    review_candidates.sort(
        key=lambda w: (-w.get("wrong_count", 0), w.get("next_review_date", ""))
    )
    review_words = review_candidates[:review_max]

    # 新規は選択カテゴリーから
    new_candidates = [
        w for w in words
        if w.get("srs_level", 0) == 0 and w.get("learned_date") is None
        and w.get("category", "other") in categories
    ]
    new_words = new_candidates[:new_per_day]

    return {
        "new_words": new_words,
        "review_words": review_words,
        "new_count": len(new_words),
        "review_count": len(review_words),
        "review_overflow": max(0, len(review_candidates) - review_max),
    }


# ============================================================
# SRSレベル更新（正解・不正解）
# ============================================================

def mark_new_learned(word_id: str, target_date: Optional[str] = None):
    """
    新規単語を「学習済み」にする（Part 1 完了時）
    → srs_level 1、翌日に最初の復習
    """
    if target_date is None:
        target_date = today_str()

    words = load_words()
    intervals = load_state()["settings"]["srs_intervals"]

    for w in words:
        if w["word_id"] == word_id:
            w["srs_level"] = 1
            w["learned_date"] = target_date
            w["last_review_date"] = target_date
            w["status"] = "learning"
            # 次回復習日 = 今日 + intervals[0]（1日後）
            next_d = date.fromisoformat(target_date) + timedelta(days=intervals[0])
            w["next_review_date"] = next_d.isoformat()
            break

    save_words(words)


def mark_review_result(word_id: str, correct: bool, target_date: Optional[str] = None):
    """
    復習（記憶TEST）の結果を反映

    正解 → srs_level +1、間隔を伸ばす
    不正解 → srs_level 1 に戻す（翌日また）
    """
    if target_date is None:
        target_date = today_str()

    words = load_words()
    intervals = load_state()["settings"]["srs_intervals"]
    max_level = len(intervals)  # 5段階 → level 6 で mastered

    for w in words:
        if w["word_id"] == word_id:
            w["review_count"] = w.get("review_count", 0) + 1
            w["last_review_date"] = target_date

            if correct:
                w["correct_count"] = w.get("correct_count", 0) + 1
                w["srs_level"] = w.get("srs_level", 1) + 1

                if w["srs_level"] > max_level:
                    # 全間隔クリア → 定着（mastered）
                    w["status"] = "mastered"
                    w["next_review_date"] = None  # もう出題しない（または超長期）
                else:
                    # 次の間隔へ
                    interval = intervals[w["srs_level"] - 1]
                    next_d = date.fromisoformat(target_date) + timedelta(days=interval)
                    w["next_review_date"] = next_d.isoformat()
            else:
                # 不正解 → レベル1に戻す（翌日再出題）
                w["wrong_count"] = w.get("wrong_count", 0) + 1
                w["srs_level"] = 1
                w["status"] = "learning"
                next_d = date.fromisoformat(target_date) + timedelta(days=intervals[0])
                w["next_review_date"] = next_d.isoformat()
            break

    save_words(words)


# ============================================================
# ストリーク・カレンダー
# ============================================================

def complete_today_mission(target_date: Optional[str] = None):
    """
    今日のミッション完了を記録 → ストリーク更新、カレンダーに🔥
    """
    if target_date is None:
        target_date = today_str()

    state = load_state()

    # 既に今日完了済みなら何もしない
    if state["daily_log"].get(target_date, {}).get("completed"):
        return state

    # daily_log に記録
    state["daily_log"][target_date] = {
        "completed": True,
        "date": target_date,
    }

    # ストリーク更新
    last = state["streak"].get("last_completed_date")
    if last is None:
        state["streak"]["current"] = 1
    else:
        last_d = date.fromisoformat(last)
        today_d = date.fromisoformat(target_date)
        diff = (today_d - last_d).days
        if diff == 1:
            state["streak"]["current"] += 1  # 連続
        elif diff == 0:
            pass  # 同日（念のため）
        else:
            state["streak"]["current"] = 1  # 途切れた → リセット

    state["streak"]["last_completed_date"] = target_date
    state["streak"]["longest"] = max(
        state["streak"]["longest"], state["streak"]["current"]
    )

    # マスター数を再集計
    words = load_words()
    state["total_mastered"] = len([w for w in words if w.get("status") == "mastered"])

    save_state(state)
    return state


def get_calendar(year: int, month: int) -> Dict:
    """
    指定月のカレンダーデータを生成

    Returns:
        Dict: {
            "year", "month",
            "days": [{date, day, completed, is_today, is_australia, is_exam, in_range}],
        }
    """
    import calendar as cal

    state = load_state()
    daily_log = state["daily_log"]
    start = state["start_date"]
    exam = state["exam_date"]
    au_start = state["australia_start"]
    au_end = state["australia_end"]
    today = today_str()

    _, num_days = cal.monthrange(year, month)
    days = []
    for d in range(1, num_days + 1):
        ds = date(year, month, d).isoformat()
        days.append({
            "date": ds,
            "day": d,
            "completed": daily_log.get(ds, {}).get("completed", False),
            "is_today": ds == today,
            "is_australia": au_start <= ds <= au_end,
            "is_exam": ds == exam,
            "in_range": ds >= start,
        })

    return {
        "year": year,
        "month": month,
        "days": days,
    }


# ============================================================
# 進捗サマリー
# ============================================================

def get_word_mark(word: Dict) -> str:
    """
    単語の学習状態に応じたマークを返す
    未学習 → "" / 学習中Lv1-2 → "✓" / Lv3-4 → "🔥" / マスター → "⭐"
    """
    status = word.get("status", "new")
    level = word.get("srs_level", 0)
    if status == "mastered":
        return "⭐"
    if word.get("learned_date") is None:
        return ""
    if level >= 3:
        return "🔥"
    if level >= 1:
        return "✓"
    return ""


def get_progress_summary() -> Dict:
    """全体の進捗サマリー"""
    words = load_words()
    state = load_state()

    total = len(words)
    mastered = len([w for w in words if w.get("status") == "mastered"])
    learning = len([w for w in words if w.get("status") == "learning"])
    new = len([w for w in words if w.get("srs_level", 0) == 0 and w.get("learned_date") is None])

    # 試験までの日数
    exam_d = date.fromisoformat(state["exam_date"])
    days_left = (exam_d - date.today()).days

    return {
        "total": total,
        "mastered": mastered,
        "learning": learning,
        "new": new,
        "streak_current": state["streak"]["current"],
        "streak_longest": state["streak"]["longest"],
        "days_until_exam": days_left,
        "percentage": round(mastered / total * 100, 1) if total > 0 else 0,
    }
