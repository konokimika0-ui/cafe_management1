from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database/cafe_management.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()
    return render_template('index.html', products=products)

@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO products (name, price, stock) VALUES (?, ?, ?)',
            (name, price, stock)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('product_create.html')

@app.route('/edit/<int:id>', methods=('GET', 'POST'))
def edit(id):
    conn = get_db_connection()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']

        conn.execute(
            'UPDATE products SET name = ?, price = ?, stock = ? WHERE id = ?',
            (name, price, stock, id)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    product = conn.execute(
        'SELECT * FROM products WHERE id = ?',
        (id,)
    ).fetchone()

    conn.close()

    return render_template('edit.html', product=product)

@app.route('/stock', methods=('GET', 'POST'))
def stock():
    conn = get_db_connection()

    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        type = request.form['type']
        quantity = int(request.form['quantity'])

        # 現在の在庫取得
        product = conn.execute(
            'SELECT stock FROM products WHERE id = ?',
            (product_id,)
        ).fetchone()

        current_stock = product['stock']

        error = None

        # 在庫計算
        if type == 'in':
            new_stock = current_stock + quantity
        else:
            if quantity > current_stock:
                error = "在庫が不足しています"
            else:
                new_stock = current_stock - quantity

        # エラーがある場合
        if error:
            products = conn.execute(
                'SELECT * FROM products'
            ).fetchall()
            conn.close()
            return render_template(
                'stock.html',
                products=products,
                error=error,
                selected_product_id=product_id
            )

        # 在庫更新
        conn.execute(
            'UPDATE products SET stock = ? WHERE id = ?',
            (new_stock, product_id)
        )

        # 履歴保存
        conn.execute(
            'INSERT INTO stock_history (product_id, type, quantity, created_at) VALUES (?, ?, ?, ?)',
            (product_id, type, quantity, datetime.now())
        )

        conn.commit()
        conn.close()

        return redirect('/')

    # GETのとき（初期表示）
    products = conn.execute('SELECT * FROM products').fetchall()
    conn.close()

    return render_template('stock.html', products=products)

@app.route('/history')
def history():
    conn = get_db_connection()

    histories = conn.execute('''
        SELECT stock_history.*, products.name
        FROM stock_history
        JOIN products ON stock_history.product_id = products.id
        ORDER BY stock_history.id DESC
    ''').fetchall()

    conn.close()

    return render_template('history.html', histories=histories)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM products WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/')

if __name__ == '__main__':
   app.run(debug=True)