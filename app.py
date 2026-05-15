from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "jobs.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company TEXT NOT NULL,
                role TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Applied',
                applied_date TEXT,
                link TEXT,
                notes TEXT,
                created_at TEXT DEFAULT (datetime('now'))
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    status_filter = request.args.get('status', 'All')
    search = request.args.get('search', '')
    with get_db() as conn:
        query = "SELECT * FROM jobs WHERE 1=1"
        params = []
        if status_filter != 'All':
            query += " AND status = ?"
            params.append(status_filter)
        if search:
            query += " AND (company LIKE ? OR role LIKE ?)"
            params += [f'%{search}%', f'%{search}%']
        query += " ORDER BY created_at DESC"
        jobs = conn.execute(query, params).fetchall()

        stats = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status='Applied' THEN 1 ELSE 0 END) as applied,
                SUM(CASE WHEN status='Interview' THEN 1 ELSE 0 END) as interview,
                SUM(CASE WHEN status='Offer' THEN 1 ELSE 0 END) as offer,
                SUM(CASE WHEN status='Rejected' THEN 1 ELSE 0 END) as rejected
            FROM jobs
        ''').fetchone()

    return render_template('index.html', jobs=jobs, stats=stats,
                           status_filter=status_filter, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        company = request.form['company']
        role = request.form['role']
        status = request.form['status']
        applied_date = request.form['applied_date']
        link = request.form['link']
        notes = request.form['notes']
        with get_db() as conn:
            conn.execute(
                "INSERT INTO jobs (company, role, status, applied_date, link, notes) VALUES (?,?,?,?,?,?)",
                (company, role, status, applied_date, link, notes)
            )
            conn.commit()
        return redirect(url_for('index'))
    return render_template('add_job.html')

@app.route('/edit/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
    with get_db() as conn:
        if request.method == 'POST':
            conn.execute(
                "UPDATE jobs SET company=?, role=?, status=?, applied_date=?, link=?, notes=? WHERE id=?",
                (request.form['company'], request.form['role'], request.form['status'],
                 request.form['applied_date'], request.form['link'], request.form['notes'], job_id)
            )
            conn.commit()
            return redirect(url_for('index'))
        job = conn.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
    return render_template('edit_job.html', job=job)

@app.route('/delete/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    with get_db() as conn:
        conn.execute("DELETE FROM jobs WHERE id=?", (job_id,))
        conn.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
