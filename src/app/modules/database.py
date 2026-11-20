import sqlite3
import hashlib
import json
from datetime import datetime
from pathlib import Path

# Define o caminho do banco na raiz do projeto
ROOT = Path(__file__).resolve().parents[3]
DB_PATH = ROOT / "healthlens.db"

def init_db():
    """Cria as tabelas se não existirem."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    
    # Tabela de Usuários
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Tabela de Histórico
    # Salvamos os 'inputs' como JSON para poder recarregar depois se quiser
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            date TEXT,
            module TEXT,
            risk_prob REAL,
            risk_level TEXT,
            details_json TEXT,
            FOREIGN KEY(username) REFERENCES users(username)
        )
    ''')
    conn.commit()
    conn.close()

def _hash_password(password):
    """Criptografia simples (SHA-256) para não salvar senha pura."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                  (username, _hash_password(password)))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False # Usuário já existe

def verify_user(username, password):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
    data = c.fetchone()
    conn.close()
    
    if data and data[0] == _hash_password(password):
        return True
    return False

def save_assessment(username, module, risk_prob, risk_level, inputs_dict):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    inputs_json = json.dumps(inputs_dict) # Converte dict para texto
    
    c.execute('''
        INSERT INTO history (username, date, module, risk_prob, risk_level, details_json)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, date_str, module, risk_prob, risk_level, inputs_json))
    
    conn.commit()
    conn.close()

def get_user_history(username, module=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()
    
    if module:
        c.execute("SELECT date, module, risk_prob, risk_level FROM history WHERE username=? AND module=? ORDER BY date DESC", (username, module))
    else:
        c.execute("SELECT date, module, risk_prob, risk_level FROM history WHERE username=? ORDER BY date DESC", (username,))
        
    data = c.fetchall()
    conn.close()
    return data # Lista de tuplas

def clear_user_history(username=None):
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    c = conn.cursor()

    if username:
        c.execute("DELETE FROM history WHERE username = ?", (username,))
    else:
        c.execute("DELETE FROM history")  # apaga tudo

    conn.commit()
    conn.close()
