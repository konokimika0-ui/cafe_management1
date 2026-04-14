from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

DB_NAME = "cafe.db"   # ←あなたのDB名


# -----------------------
# DB接続
# -----------------------
def get_db():
  conn = sqlite3.connect('database/cafe_management.db')
    conn.row_factory = sqlite3.Row
    return conn


# -----------------------
# 商品登録ページ表示
# -----------------------
@app.route("/products/create")
def product_create():
    return render_template("product_create.html")


# -----------------------
# 商品登録処理
# -----------------------
@app.route("/products/store", methods=["POST"])
def product_store():

    name = request.form["name"]
    description = request.form["description"]
    price = request.form["price"]
    sku = request.form["sku"]

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO products
        (name, description, price, sku, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        description,
        price,
        sku,
        datetime.now(),
        datetime.now()
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("product_create"))


if __name__ == "__main__":
    app.run(debug=True)