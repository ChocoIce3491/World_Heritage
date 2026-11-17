import os
from flask import Flask
import pymysql

app = Flask(__name__)

@app.route('/')
def index():
    # データベースに接続できるかの簡易テスト
    try:
        connection = pymysql.connect(
            host='db',
            user='root',
            password='rootpassword',
            database='world_heritage_db',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
        db_status = "MySQLデータベースへの接続に成功しました！"
        connection.close()
    except Exception as e:
        db_status = f"データベース接続エラー: {e}"

    return f"<h1>世界遺産検定対策アプリへようこそ！</h1><p>{db_status}</p>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
