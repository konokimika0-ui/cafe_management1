from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    conn = sqlite3.connect('database/cafe_management.db')
    conn.row_factory = sqlite3.Row
    return conn
@app.route('/')
def index():
    # ブラウザから送られてきたデータを受け取る
    search_query = request.args.get('search', '')
    category_query = request.args.get('category', '')
    
    conn = get_db_connection()
    
    # 検索の基本命令
    query = 'SELECT * FROM products WHERE 1=1'
    params = []

    # 商品名が入力されていたら絞り込む
    if search_query:
        query += ' AND name LIKE ?'
        params.append(f'%{search_query}%')
    
    # カテゴリが選択されていたら絞り込む
    if category_query:
        query += ' AND category = ?'
        params.append(category_query)

    # 最後に ID 順に並べる（任意）
    query += ' ORDER BY id DESC'

    products = conn.execute(query, params).fetchall()
    conn.close()

    # 画面を表示する。このとき search_query と category_query も送る
    return render_template('index.html', 
                           products=products, 
                           search_query=search_query, 
                           category_query=category_query)
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        category = request.form['category']  # ←ここを追加！

        conn = get_db_connection()
        # INSERT文に category を追加しました
        conn.execute(
            'INSERT INTO products (name, price, stock, category) VALUES (?, ?, ?, ?)',
            (name, price, stock, category)
        )
        conn.commit()
        conn.close()

        return redirect('/')

    return render_template('product_create.html')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db_connection()
    product = conn.execute('SELECT * FROM products WHERE id = ?', (id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        # ★ここを追加！HTMLから送られてきたカテゴリを受け取ります
        category = request.form['category']

        # ★SQL文を修正！ category = ? を追加して、5つの値を渡します
        conn.execute('UPDATE products SET name = ?, price = ?, stock = ?, category = ? WHERE id = ?',
                     (name, price, stock, category, id))
        conn.commit()
        conn.close()
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', product=product)
@app.route('/stock', methods=('GET', 'POST'))
def stock():
    conn = get_db_connection()
    if request.method == 'POST':
        product_id = int(request.form['product_id'])
        type = request.form['type']
        quantity = int(request.form['quantity'])

        product = conn.execute('SELECT stock FROM products WHERE id = ?', (product_id,)).fetchone()
        current_stock = product['stock']
        error = None

        if type == 'in':
            new_stock = current_stock + quantity
        else:
            if quantity > current_stock:
                error = "在庫が不足しています"
            else:
                new_stock = current_stock - quantity

        if error:
            products = conn.execute('SELECT * FROM products').fetchall()
            conn.close()
            return render_template('stock.html', products=products, error=error, selected_product_id=product_id)

        conn.execute('UPDATE products SET stock = ? WHERE id = ?', (new_stock, product_id))
        conn.execute('INSERT INTO stock_history (product_id, type, quantity, created_at) VALUES (?, ?, ?, ?)',
                     (product_id, type, quantity, datetime.now()))
        conn.commit()
        conn.close()
        return redirect('/')

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