import sqlite3

def init_db():
    # 既存のデータベースファイルに接続します
    conn = sqlite3.connect('database.db')
    
    # ユーザーテーブルを作成するSQL命令
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ usersテーブルの作成（確認）が完了しました！")

if __name__ == '__main__':
    init_db()