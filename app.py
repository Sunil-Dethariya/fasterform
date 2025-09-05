from flask import Flask, render_template, request, redirect, url_for, session, send_file
import sqlite3
import openpyxl

app = Flask(__name__)
app.secret_key = "your_secret_key"   # change to something secure


# ---------- Home Page (Public) ----------
@app.route('/')
def index():
    return render_template('index.html')


# ---------- Submit Form (Public) ----------
@app.route('/submit', methods=['POST'])
def submit():
    fname = request.form['first_name']
    lname = request.form['last_name']
    email = request.form['email']
    zipcode = request.form['zip_code']

    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (first_name, last_name, email, zip_code) VALUES (?, ?, ?, ?)",
                   (fname, lname, email, zipcode))
    conn.commit()
    conn.close()

    return render_template("success.html")


# ---------- Admin Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ Change username & password as per your choice
        if username == "Sunil" and password == "143":
            session['admin_logged_in'] = True
            return redirect(url_for('users'))
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


# ---------- Admin Logout ----------
@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('index'))


# ---------- Protect Function ----------
def admin_required():
    if not session.get('admin_logged_in'):
        return redirect(url_for('login'))


# ---------- Show All Users (Admin) ----------
@app.route('/users')
def users():
    check = admin_required()
    if check:
        return check

    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()
    return render_template("users.html", users=data)


# ---------- Edit User (Admin) ----------
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    check = admin_required()
    if check:
        return check

    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    if request.method == 'POST':
        fname = request.form['first_name']
        lname = request.form['last_name']
        email = request.form['email']
        zipcode = request.form['zip_code']
        cursor.execute("UPDATE users SET first_name=?, last_name=?, email=?, zip_code=? WHERE id=?",
                       (fname, lname, email, zipcode, id))
        conn.commit()
        conn.close()
        return render_template("update.html")
    else:
        cursor.execute("SELECT * FROM users WHERE id=?", (id,))
        user = cursor.fetchone()
        conn.close()
        return render_template("edit.html", user=user)


# ---------- Delete User (Admin) ----------
@app.route('/delete/<int:id>')
def delete(id):
    check = admin_required()
    if check:
        return check

    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return render_template("delete.html")


# ---------- Download Excel File (Admin) ----------
@app.route('/download')
def download():
    check = admin_required()
    if check:
        return check

    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    data = cursor.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Users"
    ws.append(["ID", "First Name", "Last Name", "Email", "Zip Code"])
    for row in data:
        ws.append(row)

    file_path = "users.xlsx"
    wb.save(file_path)

    return send_file(file_path, as_attachment=True)


# ---------- Initialize DB ----------
def init_db():
    conn = sqlite3.connect("form.db")
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        first_name TEXT,
                        last_name TEXT,
                        email TEXT,
                        zip_code TEXT)''')
    conn.commit()
    conn.close()


# ---------- Run App ----------
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
