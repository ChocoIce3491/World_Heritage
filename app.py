import os
import random
from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# データベース接続用の共通関数
def get_db_connection():
    return pymysql.connect(
        host='db',
        user='root',
        password='Password123',
        database='world_heritage_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

# 1. トップページ：世界遺産データの一覧表示
@app.route('/')
def index():
    heritages = []
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM heritage_questions_grade2")
            heritages = cursor.fetchall()
        db_status = "MySQLデータベースへの接続に成功しました！"
        connection.close()
    except Exception as e:
        db_status = f"データベース接続エラー: {e}"

    return render_template('index.html', db_status=db_status, heritages=heritages)

# 2. クイズページ：優先度スコアを活用したダミー選択肢の自動生成
@app.route('/quiz')
def quiz():
    heritages = []
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM heritage_questions_grade2")
            heritages = cursor.fetchall()
        connection.close()
    except Exception as e:
        return f"データベースエラー: {e}"

    if not heritages:
        return "データが登録されていません。"

    # 正解の問題をランダムに1件選ぶ
    correct_item = random.choice(heritages)

    # 比較用に、正解の「国」と「登録基準」をセット（集合）に分解しておく
    correct_countries = {c.strip() for c in (correct_item.get('country') or '').split(',') if c.strip()}
    correct_criteria = {cr.strip() for cr in (correct_item.get('criteria') or '').split(',') if cr.strip()}
    correct_tag = correct_item.get('tag_others')

    scored_candidates = []
    for h in heritages:
        if h['id'] == correct_item['id']:
            continue
        
        score = 0
        
        # 1. 最優先：tag_others が一致（None同士の一致は除外）
        if correct_tag and h.get('tag_others') == correct_tag:
            score += 100
            
        # 2. 次点：国名が1つでも部分一致
        h_countries = {c.strip() for c in (h.get('country') or '').split(',') if c.strip()}
        if correct_countries & h_countries:  # 積集合（共通要素）があればTrue
            score += 10
            
        # 3. 登録基準が1つでも部分一致（共通する基準の数だけ加点）
        h_criteria = {cr.strip() for cr in (h.get('criteria') or '').split(',') if cr.strip()}
        common_criteria = correct_criteria & h_criteria
        if common_criteria:
            score += 5 * len(common_criteria)

        # スコア、ランダム値（同点時のシャッフル用）、遺産名をタプルで保持
        scored_candidates.append((score, random.random(), h['heritage_name']))

    # スコアが高い順（同点ならランダム順）にソート
    scored_candidates.sort(key=lambda x: (x[0], x[1]), reverse=True)

    # 上位3件をダミーとして取得
    selected_dummies = [item[2] for item in scored_candidates[:3]]

    choices = selected_dummies + [correct_item['heritage_name']]
    random.shuffle(choices)

    return render_template('quiz.html', correct_item=correct_item, choices=choices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
