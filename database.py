import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path("db.sqlite")

def conectar():
    return sqlite3.connect(DB_PATH)

def criar_tabelas():
    with conectar() as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT UNIQUE NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            data TEXT NOT NULL,
            FOREIGN KEY (produto_id) REFERENCES produtos(id)
        )
        """)

        conn.commit()

# CRUD de produtos
def adicionar_produto(nome, quantidade, preco):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", (nome, quantidade, preco))
        conn.commit()

def listar_produtos():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM produtos")
        return cursor.fetchall()

def atualizar_produto(produto_id, nova_quantidade, novo_preco):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE produtos SET quantidade = ?, preco = ? WHERE id = ?", (nova_quantidade, novo_preco, produto_id))
        conn.commit()

def remover_produto(produto_id):
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        conn.commit()

# Registro de vendas
def registrar_venda(produto_id, quantidade):
    data = datetime.now().isoformat()
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT quantidade FROM produtos WHERE id = ?", (produto_id,))
        atual = cursor.fetchone()
        if atual and atual[0] >= quantidade:
            cursor.execute("UPDATE produtos SET quantidade = quantidade - ? WHERE id = ?", (quantidade, produto_id))
            cursor.execute("INSERT INTO vendas (produto_id, quantidade, data) VALUES (?, ?, ?)", (produto_id, quantidade, data))
            conn.commit()
            return True
        return False

def listar_vendas():
    with conectar() as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT v.id, p.nome, v.quantidade, v.data
        FROM vendas v
        JOIN produtos p ON v.produto_id = p.id
        ORDER BY v.data DESC
        """)
        return cursor.fetchall()
