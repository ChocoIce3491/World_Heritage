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

# 2. クイズページ：タグを活用したダミー選択肢の自動生成
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
    
    # 同じ系統（tag_others）のダミー候補を絞り込む
    dummies = [
        h['heritage_name'] for h in heritages 
        if h['id'] != correct_item['id'] and h['tag_others'] == correct_item['tag_others']
    ]

    if len(dummies) < 3:
        other_items = [
            h['heritage_name'] for h in heritages 
            if h['id'] != correct_item['id'] and h['heritage_name'] not in dummies
        ]
        dummies.extend(other_items)

    selected_dummies = random.sample(dummies, min(3, len(dummies)))
    choices = selected_dummies + [correct_item['heritage_name']]
    random.shuffle(choices)

    # templates/quiz.html をレンダリングして返す
    return render_template('quiz.html', correct_item=correct_item, choices=choices)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
