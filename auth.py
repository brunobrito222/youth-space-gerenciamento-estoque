import hashlib
from database import conectar

def hash_senha(senha):
    return hashlib.sha256(senha.encode()).hexdigest()

def cadastrar_usuario(username, senha):
    senha_hash = hash_senha(senha)
    try:
        with conectar() as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (username, senha) VALUES (?, ?)", (username, senha_hash))
            conn.commit()
        return True
    except:
        return False

def verificar_login(username, senha):
    senha_hash = hash_senha(senha)
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE username = ? AND senha = ?", (username, senha_hash))
        return cursor.fetchone() is not None
