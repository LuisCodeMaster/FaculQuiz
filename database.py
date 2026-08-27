import sqlite3

BANCO = "faculquiz.db"


def conectar():
    return sqlite3.connect(BANCO)


def criar_banco():
    conexao = conectar()
    cursor = conexao.cursor()

    # ==========================================
    # DISCIPLINAS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS materias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    # ==========================================
    # ASSUNTOS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS assuntos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            materia_id INTEGER NOT NULL,
            nome TEXT NOT NULL,
            FOREIGN KEY (materia_id) REFERENCES materias(id),
            UNIQUE(materia_id, nome)
        )
    """)

    # ==========================================
    # TEMAS
    # ==========================================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS temas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    """)

    # ==========================================
    # VERIFICAR ESTRUTURA ATUAL DE QUESTOES
    # ==========================================

    cursor.execute("PRAGMA table_info(questoes)")
    questoes_existem = len(cursor.fetchall()) > 0

    if not questoes_existem:

        # Cria a tabela já com a estrutura correta
        cursor.execute("""
            CREATE TABLE questoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                materia_id INTEGER,
                pergunta TEXT NOT NULL,
                alternativa_a TEXT NOT NULL,
                alternativa_b TEXT NOT NULL,
                alternativa_c TEXT NOT NULL,
                alternativa_d TEXT NOT NULL,
                correta TEXT NOT NULL,
                explicacao TEXT,
                dificuldade INTEGER DEFAULT 1,
                assunto_id INTEGER,
                tema_id INTEGER,
                FOREIGN KEY (materia_id) REFERENCES materias(id),
                FOREIGN KEY (assunto_id) REFERENCES assuntos(id),
                FOREIGN KEY (tema_id) REFERENCES temas(id)
            )
        """)

    else:

        # ==========================================
        # MIGRAÇÃO DA TABELA QUESTOES
        # ==========================================

        cursor.execute("PRAGMA table_info(questoes)")
        colunas_info = cursor.fetchall()

        nomes_colunas = [
            coluna[1]
            for coluna in colunas_info
        ]

        materia_not_null = False

        for coluna in colunas_info:

            nome = coluna[1]
            not_null = coluna[3]

            if nome == "materia_id" and not_null == 1:
                materia_not_null = True

        # Se materia_id for NOT NULL,
        # recria a tabela permitindo NULL.
        if materia_not_null:

            cursor.execute("""
                ALTER TABLE questoes
                RENAME TO questoes_old
            """)

            cursor.execute("""
                CREATE TABLE questoes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    materia_id INTEGER,
                    pergunta TEXT NOT NULL,
                    alternativa_a TEXT NOT NULL,
                    alternativa_b TEXT NOT NULL,
                    alternativa_c TEXT NOT NULL,
                    alternativa_d TEXT NOT NULL,
                    correta TEXT NOT NULL,
                    explicacao TEXT,
                    dificuldade INTEGER DEFAULT 1,
                    assunto_id INTEGER,
                    tema_id INTEGER,
                    FOREIGN KEY (materia_id) REFERENCES materias(id),
                    FOREIGN KEY (assunto_id) REFERENCES assuntos(id),
                    FOREIGN KEY (tema_id) REFERENCES temas(id)
                )
            """)

            # Copia os dados antigos
            cursor.execute("""
                INSERT INTO questoes (
                    id,
                    materia_id,
                    pergunta,
                    alternativa_a,
                    alternativa_b,
                    alternativa_c,
                    alternativa_d,
                    correta,
                    explicacao,
                    dificuldade,
                    assunto_id,
                    tema_id
                )
                SELECT
                    id,
                    materia_id,
                    pergunta,
                    alternativa_a,
                    alternativa_b,
                    alternativa_c,
                    alternativa_d,
                    correta,
                    explicacao,
                    dificuldade,
                    assunto_id,
                    tema_id
                FROM questoes_old
            """)

            cursor.execute("""
                DROP TABLE questoes_old
            """)

        else:

            # Adiciona assunto_id se necessário
            if "assunto_id" not in nomes_colunas:

                cursor.execute("""
                    ALTER TABLE questoes
                    ADD COLUMN assunto_id INTEGER
                """)

            # Adiciona tema_id se necessário
            if "tema_id" not in nomes_colunas:

                cursor.execute("""
                    ALTER TABLE questoes
                    ADD COLUMN tema_id INTEGER
                """)

    # ==========================================
    # RESPOSTAS
    # ==========================================

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