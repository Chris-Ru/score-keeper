from flask import Flask, render_template, request, g, jsonify
import sqlite3

app = Flask(__name__)

DATABASE = 'billiard.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()

@app.route('/pool/')
def index():
    return render_template('index.html')

@app.route('/pool/get_scores', methods=['GET'])
def get_scores():
    db = get_db()
    cur = db.execute('SELECT p.id, p.name, IFNULL(SUM(s.score), 0) as total_score FROM players p LEFT JOIN scores s ON p.id = s.player_id GROUP BY p.id, p.name')
    players = cur.fetchall()
    return jsonify(players)

@app.route('/pool/add_player', methods=['POST'])
def add_player():
    db = get_db()
    db.execute('INSERT INTO players (name) VALUES (?)', [request.json['name']])
    db.commit()
    return jsonify(success=True)

@app.route('/pool/remove_player/<int:player_id>', methods=['POST'])
def remove_player(player_id):
    db = get_db()
    db.execute('DELETE FROM players WHERE id = ?', [player_id])
    db.execute('DELETE FROM scores WHERE player_id = ?', [player_id])
    db.commit()
    return jsonify(success=True)

@app.route('/pool/increment_score/<int:player_id>', methods=['POST'])
def increment_score(player_id):
    db = get_db()
    db.execute('INSERT INTO scores (player_id, score) VALUES (?, 1)', [player_id])
    db.commit()
    return jsonify(success=True)

@app.route('/pool/decrement_score/<int:player_id>', methods=['POST'])
def decrement_score(player_id):
    db = get_db()
    cur = db.execute('SELECT IFNULL(SUM(score), 0) as total_score FROM scores WHERE player_id = ?', [player_id])
    player_score = cur.fetchone()
    if player_score and player_score[0] > 0:
        db.execute('INSERT INTO scores (player_id, score) VALUES (?, -1)', [player_id])
        db.commit()
    return jsonify(success=True)
