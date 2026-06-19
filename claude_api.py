"""
claude_api.py - Claude API ラッパー関数

ライティング採点、単語訳判定、フィードバック生成などを担当
"""

import json
from anthropic import Anthropic

client = Anthropic()

# ============================================================
# ライティング採点関数
# ============================================================

def score_writing_free(text: str) -> dict:
    """
    Free Writing モード採点（高速）
    
    Args:
        text (str): 採点対象のテキスト
    
    Returns:
        dict: {
            "content_score": 0-100,
            "structure_score": 0-100,
            "feedback": "フィードバック"
        }
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        system="""
        英検準2級ライティング採点者です。
        Content（内容）と Structure（構成）のみ採点。
        
        【採点基準】
        Content: 意見は明確か、理由は2つ以上か
        Structure: 段落構成、流れの自然さ
        
        JSON 形式で必ず返してください：
        {
            "content_score": 0-100の数字,
            "structure_score": 0-100の数字,
            "feedback": "日本語フィードバック（3-5行）"
        }
        
        JSON の外に説明は付けないでください。
        """,
        messages=[{
            "role": "user",
            "content": f"採点対象テキスト:\n{text}"
        }]
    )
    
    try:
        result = json.loads(message.content[0].text)
        return result
    except json.JSONDecodeError:
        return {
            "content_score": 50,
            "structure_score": 50,
            "feedback": "採点エラーが発生しました。もう一度試してください。"
        }


def score_writing_polishing(text: str) -> dict:
    """
    Polishing モード採点（詳細）
    
    Args:
        text (str): 採点対象のテキスト
    
    Returns:
        dict: {
            "content_score": 0-100,
            "structure_score": 0-100,
            "vocabulary_score": 0-100,
            "grammar_score": 0-100,
            "spell_errors": [...],
            "feedback": "詳細フィードバック"
        }
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=800,
        system="""
        英検準2級ライティング採点者です。
        Content / Structure / Vocabulary / Grammar を詳細に採点。
        
        【採点基準】
        Content: 意見と理由の明確さ（0-100）
        Structure: 段落構成、流れ（0-100）
        Vocabulary: スペル、表現の自然さ（0-100）
        Grammar: 文法、時制、接続詞（0-100）
        
        【スペルミスがあれば】
        箇所を「行番号: 誤 → 正」形式で明示。
        
        JSON 形式で必ず返してください：
        {
            "content_score": 数字,
            "structure_score": 数字,
            "vocabulary_score": 数字,
            "grammar_score": 数字,
            "spell_errors": [
                {"line": "2行目", "error": "word", "correct": "word"}
            ],
            "feedback": "詳細なフィードバック"
        }
        
        JSON の外に説明は付けないでください。
        """,
        messages=[{
            "role": "user",
            "content": f"採点対象テキスト:\n{text}"
        }]
    )
    
    try:
        result = json.loads(message.content[0].text)
        return result
    except json.JSONDecodeError:
        return {
            "content_score": 50,
            "structure_score": 50,
            "vocabulary_score": 50,
            "grammar_score": 50,
            "spell_errors": [],
            "feedback": "採点エラーが発生しました。"
        }


# ============================================================
# 単語訳判定関数
# ============================================================

def evaluate_vocabulary_translation(user_answer: str, correct_definition: str, word: str) -> dict:
    """
    ユーザーの訳が正確かを AI で判定
    
    Args:
        user_answer (str): ユーザーが入力した和訳
        correct_definition (str): 正答の定義
        word (str): 対象の英単語
    
    Returns:
        dict: {
            "is_correct": True/False,
            "score": 0-100,
            "feedback": "フィードバック"
        }
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=200,
        system="""
        英検準2級の単語訳判定者です。
        
        ユーザーが入力した和訳が、正答の意味として
        適切かを判定してください。
        
        【判定ルール】
        - 意味が完全に合致：正解
        - 意味が部分的に合致：正解（例：「本物の」で「本物の、本当の」は OK）
        - 完全に異なる意味：不正解
        
        JSON 形式で返してください：
        {
            "is_correct": true/false,
            "score": 0-100の数字,
            "feedback": "フィードバック"
        }
        
        JSON の外に説明は付けないでください。
        """,
        messages=[{
            "role": "user",
            "content": f"""
単語: {word}
正答の定義: {correct_definition}
ユーザー入力: {user_answer}

この入力は正答として認められるか判定してください。
            """
        }]
    )
    
    try:
        result = json.loads(message.content[0].text)
        return result
    except json.JSONDecodeError:
        return {
            "is_correct": False,
            "score": 0,
            "feedback": "判定エラーが発生しました。"
        }


# ============================================================
# フリートーク機能
# ============================================================

def free_talk(user_message: str, conversation_history: list = None) -> str:
    """
    ユーザーとの英語会話（フリートーク）
    
    Args:
        user_message (str): ユーザーのメッセージ（英語）
        conversation_history (list): 会話履歴
    
    Returns:
        str: GAVI の応答
    """
    if conversation_history is None:
        conversation_history = []
    
    # 会話履歴に新しいメッセージを追加
    messages = conversation_history + [{
        "role": "user",
        "content": user_message
    }]
    
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        system="""
        あなたは GAVI、知の啓示の天使です。
        準2級学習中の莉亜さんと英語で会話します。
        
        【対応方針】
        - ユーザーの英文が不完全でも、優しく続きを促す
        - 文法ミスがあれば、さりげなく修正案を提示
        - 励ましながら会話を続ける
        - 日本語は使わない（英語のみ）
        - 準2級レベルの語彙を使う
        - 返答は 2-3 文程度にする
        
        例：
        ユーザー: "I think AI is very...uh..."
        GAVI: "Yes, you're on the right track! 
               AI is indeed very powerful. 
               What do you think about that?"
        """,
        messages=messages
    )
    
    return response.content[0].text


# ============================================================
# 面接シミュレーション
# ============================================================

def interview_simulation(user_answer: str, question: str = None) -> dict:
    """
    英検準2級面接対策
    
    Args:
        user_answer (str): ユーザーの回答
        question (str): 質問（指定しない場合は生成）
    
    Returns:
        dict: {
            "score": 0-100,
            "fluency": 0-100,
            "accuracy": 0-100,
            "feedback": "フィードバック",
            "better_expression": "より自然な表現例"
        }
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system="""
        あなたは英検準2級の面接官です。
        ユーザーの回答を採点し、改善提案をしてください。
        
        【採点項目】
        Score: 全体的な評価（0-100）
        Fluency: 流暢さ、自然さ（0-100）
        Accuracy: 文法、表現の正確さ（0-100）
        
        JSON 形式で返してください：
        {
            "score": 数字,
            "fluency": 数字,
            "accuracy": 数字,
            "feedback": "日本語フィードバック",
            "better_expression": "より自然な表現例"
        }
        
        JSON の外に説明は付けないでください。
        """,
        messages=[{
            "role": "user",
            "content": f"""
質問: {question if question else "Tell me about your hobby."}
回答: {user_answer}

この回答を採点してください。
            """
        }]
    )
    
    try:
        result = json.loads(message.content[0].text)
        return result
    except json.JSONDecodeError:
        return {
            "score": 50,
            "fluency": 50,
            "accuracy": 50,
            "feedback": "採点エラーが発生しました。",
            "better_expression": ""
        }


# ============================================================
# 学習プラン生成
# ============================================================

def generate_study_plan(progress_data: dict) -> str:
    """
    ユーザーの進捗に基づいて学習プランを生成
    
    Args:
        progress_data (dict): 進捗データ
    
    Returns:
        str: 学習プランの推奨
    """
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=400,
        system="""
        英検準2級対策のアドバイザーです。
        ユーザーの進捗に基づいて、今日の学習内容を提案してください。
        日本語で返答してください。
        """,
        messages=[{
            "role": "user",
            "content": f"""
現在の進捗:
{json.dumps(progress_data, ensure_ascii=False, indent=2)}

このデータに基づいて、今日の学習内容と優先事項を提案してください。
2-3段落で簡潔に。
            """
        }]
    )
    
    return response.content[0].text
