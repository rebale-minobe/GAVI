"""
data_manager.py - GAVI データ管理モジュール

GitHub JSON ファイルの読み込み・保存・更新を担当
"""

import json
import streamlit as st
from datetime import datetime
from typing import Dict, List, Optional

# ============================================================
# GitHub API 設定（将来実装）
# ============================================================

# 現在のフェーズではローカル JSON を使用
# 将来：GitHub API で自動保存

class DataManager:
    """GAVI のデータを管理するクラス"""
    
    def __init__(self):
        """初期化"""
        self.words_file = "data/words.json"
        self.progress_file = "data/progress.json"
        self.writing_file = "data/writing_records.json"
    
    # ============================================================
    # 単語データ管理
    # ============================================================
    
    @staticmethod
    def load_words() -> List[Dict]:
        """
        words.json から単語データを読み込む
        
        Returns:
            List[Dict]: 単語リスト
        """
        try:
            with open("data/words.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("words", [])
        except FileNotFoundError:
            return []
    
    @staticmethod
    def get_word_by_status(status: str) -> List[Dict]:
        """
        ステータス別に単語を取得
        
        Args:
            status (str): "new" / "quiz_pending" / "translation_pending" / "mastered" / "review_only"
        
        Returns:
            List[Dict]: 該当する単語リスト
        """
        words = DataManager.load_words()
        return [w for w in words if w.get("status") == status]
    
    @staticmethod
    def update_word_status(word_id: str, new_status: str, 
                          attempts: Optional[Dict] = None) -> bool:
        """
        単語のステータスを更新
        
        Args:
            word_id (str): 単語ID
            new_status (str): 新しいステータス
            attempts (dict): 試行回数情報
        
        Returns:
            bool: 成功したか
        """
        try:
            with open("data/words.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for word in data["words"]:
                if word["word_id"] == word_id:
                    word["status"] = new_status
                    word["last_reviewed"] = datetime.now().isoformat()
                    
                    # 試行回数を更新
                    if attempts:
                        if "quiz_attempts" in attempts:
                            word["quiz_attempts"] = attempts["quiz_attempts"]
                        if "translation_attempts" in attempts:
                            word["translation_attempts"] = attempts["translation_attempts"]
                        if "incorrect_count" in attempts:
                            word["incorrect_count"] = attempts["incorrect_count"]
                    
                    # マスター時の日時を記録
                    if new_status == "mastered":
                        word["mastered_date"] = datetime.now().isoformat()
                    
                    break
            
            with open("data/words.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating word status: {e}")
            return False
    
    @staticmethod
    def increment_incorrect_count(word_id: str) -> bool:
        """
        単語の不正解カウントを増やす
        
        Args:
            word_id (str): 単語ID
        
        Returns:
            bool: 成功したか
        """
        try:
            with open("data/words.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            for word in data["words"]:
                if word["word_id"] == word_id:
                    word["incorrect_count"] += 1
                    
                    # 3回以上失敗したら review_only に
                    if word["incorrect_count"] >= 3:
                        word["status"] = "review_only"
                    
                    break
            
            with open("data/words.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error incrementing incorrect count: {e}")
            return False
    
    # ============================================================
    # 進捗管理
    # ============================================================
    
    @staticmethod
    def load_progress() -> Dict:
        """
        進捗データを読み込む
        
        Returns:
            Dict: 進捗データ
        """
        try:
            with open("data/progress.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "user_id": "user01",
                "current_phase": 1,
                "phase_start_date": datetime.now().isoformat(),
                "statistics": {
                    "vocabulary": {
                        "new": 100,
                        "quiz_pending": 0,
                        "translation_pending": 0,
                        "mastered": 0,
                        "review_only": 0
                    },
                    "writing": {
                        "free_writing_count": 0,
                        "polishing_count": 0
                    }
                }
            }
    
    @staticmethod
    def update_progress(stats_update: Dict) -> bool:
        """
        進捗を更新
        
        Args:
            stats_update (Dict): 更新する統計情報
        
        Returns:
            bool: 成功したか
        """
        try:
            progress = DataManager.load_progress()
            progress["statistics"].update(stats_update)
            progress["last_updated"] = datetime.now().isoformat()
            
            with open("data/progress.json", "w", encoding="utf-8") as f:
                json.dump(progress, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error updating progress: {e}")
            return False
    
    @staticmethod
    def get_vocabulary_stats() -> Dict:
        """
        単語学習の統計を計算
        
        Returns:
            Dict: 統計情報
        """
        words = DataManager.load_words()
        
        stats = {
            "new": len([w for w in words if w["status"] == "new"]),
            "quiz_pending": len([w for w in words if w["status"] == "quiz_pending"]),
            "translation_pending": len([w for w in words if w["status"] == "translation_pending"]),
            "mastered": len([w for w in words if w["status"] == "mastered"]),
            "review_only": len([w for w in words if w["status"] == "review_only"]),
            "total": len(words)
        }
        
        # パーセンテージを計算
        if stats["total"] > 0:
            stats["mastered_percentage"] = round(
                (stats["mastered"] / stats["total"]) * 100, 1
            )
        else:
            stats["mastered_percentage"] = 0
        
        return stats

    # ============================================================
    # カテゴリー（品詞）管理
    # ============================================================

    # カテゴリー定義（表示順・ラベル・絵文字・eiloカラー）
    CATEGORIES = [
        {"key": "verb",      "label": "動詞",   "emoji": "📗", "color": "#E03131"},  # 赤
        {"key": "noun",      "label": "名詞",   "emoji": "📘", "color": "#ADB5BD"},  # 薄グレー
        {"key": "adjective", "label": "形容詞", "emoji": "📙", "color": "#4DABF7"},  # 水色
        {"key": "adverb",    "label": "副詞",   "emoji": "📕", "color": "#4DABF7"},  # 水色（形容詞と同系）
        {"key": "idiom",     "label": "熟語",   "emoji": "🔗", "color": "#37B24D"},  # 緑
        {"key": "other",     "label": "その他", "emoji": "📦", "color": "#F59F00"},  # 黄
    ]

    @staticmethod
    def get_category_color(category_key: str) -> str:
        """カテゴリーのeiloカラーを取得"""
        for c in DataManager.CATEGORIES:
            if c["key"] == category_key:
                return c["color"]
        return "#ADB5BD"

    @staticmethod
    def get_words_by_category(category_key: str) -> List[Dict]:
        """
        指定カテゴリーの単語をすべて取得

        Args:
            category_key (str): "verb" / "noun" / ...

        Returns:
            List[Dict]: 該当カテゴリーの単語リスト
        """
        words = DataManager.load_words()
        return [w for w in words if w.get("category", "other") == category_key]

    @staticmethod
    def get_category_progress() -> List[Dict]:
        """
        カテゴリーごとの進捗（マスター数 / 総数）を集計

        Returns:
            List[Dict]: [{key, label, emoji, mastered, total}, ...]
        """
        words = DataManager.load_words()
        result = []
        for cat in DataManager.CATEGORIES:
            cat_words = [w for w in words if w.get("category", "other") == cat["key"]]
            mastered = len([w for w in cat_words if w["status"] == "mastered"])
            result.append({
                "key": cat["key"],
                "label": cat["label"],
                "emoji": cat["emoji"],
                "color": cat["color"],
                "mastered": mastered,
                "total": len(cat_words),
            })
        return result

    @staticmethod
    def get_overall_progress() -> Dict:
        """
        全体の進捗（マスター数 / 総数 / パーセント）

        Returns:
            Dict: {mastered, total, percentage}
        """
        words = DataManager.load_words()
        total = len(words)
        mastered = len([w for w in words if w["status"] == "mastered"])
        percentage = round((mastered / total) * 100, 1) if total > 0 else 0
        return {"mastered": mastered, "total": total, "percentage": percentage}

    # ============================================================
    # ライティング記録
    # ============================================================
    
    @staticmethod
    def save_writing_record(record: Dict) -> bool:
        """
        ライティング記録を保存
        
        Args:
            record (Dict): ライティング記録
        
        Returns:
            bool: 成功したか
        """
        try:
            try:
                with open("data/writing_records.json", "r", encoding="utf-8") as f:
                    data = json.load(f)
            except FileNotFoundError:
                data = {"writing_records": []}
            
            # 新しいレコードに ID を付与
            max_id = max(
                [int(r["record_id"][1:]) for r in data.get("writing_records", [])],
                default=0
            )
            record["record_id"] = f"W{max_id + 1:03d}"
            record["date"] = datetime.now().isoformat()
            
            data["writing_records"].append(record)
            
            with open("data/writing_records.json", "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving writing record: {e}")
            return False
    
    @staticmethod
    def get_writing_stats() -> Dict:
        """
        ライティング学習の統計を計算
        
        Returns:
            Dict: 統計情報
        """
        try:
            with open("data/writing_records.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                records = data.get("writing_records", [])
        except FileNotFoundError:
            return {
                "free_writing_count": 0,
                "free_writing_avg_score": 0,
                "polishing_count": 0,
                "polishing_avg_score": 0
            }
        
        free_writing = [r for r in records if r.get("mode") == "free_writing"]
        polishing = [r for r in records if r.get("mode") == "polishing"]
        
        def calc_avg_score(records_list):
            if not records_list:
                return 0
            scores = []
            for r in records_list:
                score_dict = r.get("scores", {})
                avg = sum([score_dict.get(k, 0) for k in score_dict]) / len(score_dict)
                scores.append(avg)
            return round(sum(scores) / len(scores), 1) if scores else 0
        
        return {
            "free_writing_count": len(free_writing),
            "free_writing_avg_score": calc_avg_score(free_writing),
            "polishing_count": len(polishing),
            "polishing_avg_score": calc_avg_score(polishing),
            "total_count": len(records)
        }
    
    # ============================================================
    # 初期化・リセット
    # ============================================================
    
    @staticmethod
    def initialize_data():
        """初期データを作成"""
        # progress.json の初期化は load_progress() で対応
        # words.json の初期化は別途実装
        pass
