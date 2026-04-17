import sqlite3

# データベースに接続
conn = sqlite3.connect('database/cafe_management.db')
cursor = conn.cursor()

try:
    # カテゴリ列を追加する命令を実行
    cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT '未分類'")
    conn.commit()
    print("✅ 成功しました！データベースに『カテゴリ』項目を追加しました。")
except sqlite3.OperationalError:
    # すでに列が存在する場合のエラー回避
    print("ℹ️ すでに『カテゴリ』項目は存在しているか、追加済みです。")

conn.close()