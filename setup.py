from database import conectar, criar_banco


def adicionar_materia(nome):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute(
        "INSERT OR IGNORE INTO materias (nome) VALUES (?)",
        (nome,)
    )

    conexao.commit()

    cursor.execute(
        "SELECT id FROM materias WHERE nome = ?",
        (nome,)
    )

    resultado = cursor.fetchone()
    conexao.close()

    return resultado[0]


def adicionar_assunto(materia_id, nome):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO assuntos (materia_id, nome)
        VALUES (?, ?)
    """, (materia_id, nome))

    conexao.commit()

    cursor.execute("""
        SELECT id
        FROM assuntos
        WHERE materia_id = ? AND nome = ?
    """, (materia_id, nome))

    resultado = cursor.fetchone()
    conexao.close()

    return resultado[0]


def atualizar_questao(pergunta, assunto_id, dificuldade):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE questoes
        SET assunto_id = ?,
            dificuldade = ?
        WHERE pergunta = ?
    """, (
        assunto_id,
        dificuldade,
        pergunta
    ))

    conexao.commit()
    conexao.close()


def adicionar_questao(
    materia_id,
    assunto_id,
    pergunta,
    a,
    b,
    c,
    d,
    correta,
    explicacao,
    dificuldade=1
):
    conexao = conectar()
    cursor = conexao.cursor()

    # Verifica se a questão já existe
    cursor.execute("""
        SELECT id
        FROM questoes
        WHERE pergunta = ?
    """, (pergunta,))

    existente = cursor.fetchone()

    if existente:
        # Atualiza a questão existente
        cursor.execute("""
            UPDATE questoes
            SET assunto_id = ?,
                dificuldade = ?
            WHERE id = ?
        """, (
            assunto_id,
            dificuldade,
            existente[0]
        ))

    else:
        # Cria uma nova questão
        cursor.execute("""
            INSERT INTO questoes (
                materia_id,
                assunto_id,
                pergunta,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                correta,
                explicacao,
                dificuldade
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            materia_id,
            assunto_id,
            pergunta,
            a,
            b,
            c,
            d,
            correta,
            explicacao,
            dificuldade
        ))

    conexao.commit()
    conexao.close()


# ==========================================
# CONFIGURAÇÃO DO BANCO
# ==========================================

criar_banco()

materia = adicionar_materia("Testes de Software")


# ==========================================
# ASSUNTOS
# ==========================================

fundamentos = adicionar_assunto(
    materia,
    "Fundamentos"
)

unitario = adicionar_assunto(
    materia,
    "Teste Unitário"
)

integracao = adicionar_assunto(
    materia,
    "Teste de Integração"
)

caixa_preta = adicionar_assunto(
    materia,
    "Caixa-preta"
)


# ==========================================
# QUESTÕES
# ==========================================

adicionar_questao(
    materia,
    fundamentos,
    "Qual é o principal objetivo dos testes de software?",
    "Aumentar a velocidade do computador",
    "Encontrar defeitos e avaliar a qualidade do software",
    "Escrever o código automaticamente",
    "Substituir os programadores",
    "B",
    "Os testes ajudam a encontrar defeitos e avaliar a qualidade do software.",
    dificuldade=1
)


adicionar_questao(
    materia,
    unitario,
    "O que é um teste unitário?",
    "Teste do sistema inteiro",
    "Teste realizado pelo usuário final",
    "Teste de uma unidade isolada do software",
    "Teste exclusivamente de segurança",
    "C",
    "O teste unitário verifica uma pequena unidade do software de forma isolada.",
    dificuldade=1
)


adicionar_questao(
    materia,
    integracao,
    "Qual teste verifica se diferentes componentes funcionam corretamente juntos?",
    "Teste unitário",
    "Teste de integração",
    "Teste de aceitação",
    "Teste de usabilidade",
    "B",
    "O teste de integração verifica a interação entre diferentes componentes.",
    dificuldade=2
)


adicionar_questao(
    materia,
    fundamentos,
    "O que é um teste de regressão?",
    "Testar apenas código novo",
    "Verificar se alterações quebraram funcionalidades existentes",
    "Testar somente a interface gráfica",
    "Medir a velocidade do computador",
    "B",
    "O teste de regressão verifica se mudanças no software causaram problemas em funcionalidades que já funcionavam.",
    dificuldade=2
)


adicionar_questao(
    materia,
    caixa_preta,
    "Em testes de caixa-preta, o foco principal está em:",
    "Estrutura interna do código",
    "Código-fonte linha por linha",
    "Comportamento e entradas e saídas do sistema",
    "Arquitetura do processador",
    "C",
    "O teste de caixa-preta avalia o comportamento observável do sistema, sem depender da estrutura interna do código.",
    dificuldade=2
)


print()
print("=" * 50)
print("              FACULQUIZ")
print("=" * 50)
print()
print("✅ Banco configurado!")
print("✅ Assuntos configurados!")
print("✅ Questões configuradas!")
print("✅ Dificuldades atualizadas!")
print()
print("Nenhuma resposta ou histórico foi apagado.")
print("=" * 50)
