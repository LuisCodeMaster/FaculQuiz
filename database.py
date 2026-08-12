import sqlite3

BANCO = "faculquiz.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assuntos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (materia_id) REFERENCES materias(id),
            UNIQUE(materia_id, nome)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            pergunta TEXT NOT NULL,
            alternativa_a TEXT NOT NULL,
            alternativa_b TEXT NOT NULL,
            alternativa_c TEXT NOT NULL,
            alternativa_d TEXT NOT NULL,
            correta TEXT NOT NULL,
            explicacao TEXT,
            dificuldade INTEGER DEFAULT 1,
            FOREIGN KEY (materia_id) REFERENCES materias(id)
        )
    """)

    # Verifica se a coluna assunto_id já existe
    cursor.execute("PRAGMA table_info(questoes)")
    colunas = [coluna[1] for coluna in cursor.fetchall()]

    # Se não existir, adiciona a coluna automaticamente
    if "assunto_id" not in colunas:
        cursor.execute("""
            ALTER TABLE questoes
            ADD COLUMN assunto_id INTEGER
        """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS respostas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            questao_id INTEGER NOT NULL,
            resposta TEXT NOT NULL,
            correta INTEGER NOT NULL,
            data TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (questao_id) REFERENCES questoes(id)
        )
    """)

    conexao.commit()
    conexao.close()
