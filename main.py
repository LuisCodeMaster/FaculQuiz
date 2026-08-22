import sqlite3

from database import conectar, criar_banco


# ==========================================
# BANCO DE DADOS
# ==========================================

criar_banco()


# ==========================================
# SALVAR RESPOSTA
# ==========================================

def salvar_resposta(questao_id, resposta, correta):
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO respostas (
            questao_id,
            resposta,
            correta
        )
        VALUES (?, ?, ?)
    """, (
        questao_id,
        resposta,
        correta
    ))

    conexao.commit()
    conexao.close()


# ==========================================
# MOSTRAR RESULTADO
# ==========================================

def mostrar_resultado(acertos, total):
    print("\n" + "=" * 50)
    print("              RESULTADO")
    print("=" * 50)

    if total == 0:
        print("\nNenhuma questão respondida.")
        return

    porcentagem = (acertos / total) * 100

    print(f"\n✅ Acertos: {acertos}")
    print(f"❌ Erros: {total - acertos}")
    print(f"📊 Aproveitamento: {porcentagem:.0f}%")

    if porcentagem >= 80:
        print("\n🎉 Excelente desempenho!")

    elif porcentagem >= 60:
        print("\n👍 Bom desempenho!")

    else:
        print("\n📚 Continue estudando esse assunto!")


# ==========================================
# BUSCAR QUESTÕES
# ==========================================

def buscar_questoes(materia_id=None, assunto_id=None, limite=10):
    conexao = conectar()
    cursor = conexao.cursor()

    if assunto_id is not None:
        cursor.execute("""
            SELECT
                id,
                pergunta,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                correta,
                explicacao,
                dificuldade
            FROM questoes
            WHERE assunto_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (assunto_id, limite))

    elif materia_id is not None:
        cursor.execute("""
            SELECT
                id,
                pergunta,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                correta,
                explicacao,
                dificuldade
            FROM questoes
            WHERE materia_id = ?
            ORDER BY RANDOM()
            LIMIT ?
        """, (materia_id, limite))

    else:
        cursor.execute("""
            SELECT
                id,
                pergunta,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                correta,
                explicacao,
                dificuldade
            FROM questoes
            ORDER BY RANDOM()
            LIMIT ?
        """, (limite,))

    questoes = cursor.fetchall()

    conexao.close()

    return questoes


# ==========================================
# LISTAR DISCIPLINAS
# ==========================================

def listar_disciplinas():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM materias
        ORDER BY nome
    """)

    disciplinas = cursor.fetchall()

    conexao.close()

    print("\n" + "=" * 45)
    print("             DISCIPLINAS")
    print("=" * 45)

    if not disciplinas:

        print("\nNenhuma disciplina cadastrada.")
        return

    for id_disciplina, nome in disciplinas:

        print(f"{id_disciplina}. {nome}")

    input("\nPressione Enter para continuar...")



# ==========================================
# EDITAR DISCIPLINA
# ==========================================

def editar_disciplina():

    listar_disciplinas()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM materias
        ORDER BY nome
    """)

    disciplinas = cursor.fetchall()

    if not disciplinas:

        conexao.close()
        return

    while True:

        try:

            disciplina_id = int(
                input("\nID da disciplina que deseja editar: ")
            )

            if any(d[0] == disciplina_id for d in disciplinas):
                break

            print("❌ ID inválido.")

        except ValueError:

            print("❌ Digite apenas um número.")

    novo_nome = input(
        "\nNovo nome da disciplina: "
    ).strip()

    if not novo_nome:

        print("\n❌ O nome não pode ficar vazio.")
        conexao.close()
        return

    try:

        cursor.execute("""
            UPDATE materias
            SET nome = ?
            WHERE id = ?
        """, (novo_nome, disciplina_id))

        conexao.commit()

        print("\n✅ Disciplina atualizada com sucesso!")

    except sqlite3.IntegrityError:

        print("\n❌ Já existe uma disciplina com esse nome.")

    finally:

        conexao.close()


# ==========================================
# EXCLUIR DISCIPLINA
# ==========================================

def excluir_disciplina():

    listar_disciplinas()

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome
        FROM materias
        ORDER BY nome
    """)

    disciplinas = cursor.fetchall()

    if not disciplinas:

        conexao.close()
        return

    while True:

        try:

            disciplina_id = int(
                input("\nID da disciplina que deseja excluir: ")
            )

            disciplina = next(
                (
                    d for d in disciplinas
                    if d[0] == disciplina_id
                ),
                None
            )

            if disciplina:
                break

            print("❌ ID inválido.")

        except ValueError:

            print("❌ Digite apenas um número.")

    nome = disciplina[1]

    cursor.execute("""
        SELECT COUNT(*)
        FROM questoes
        WHERE materia_id = ?
    """, (disciplina_id,))

    quantidade_questoes = cursor.fetchone()[0]

    if quantidade_questoes > 0:

        print(
            f"\n❌ Não é possível excluir '{nome}'."
        )

        print(
            f"Ela possui {quantidade_questoes} questão(ões) cadastrada(s)."
        )

        print(
            "\nRemova ou transfira as questões antes de excluir a disciplina."
        )

        conexao.close()
        return

    cursor.execute("""
        SELECT COUNT(*)
        FROM assuntos
        WHERE materia_id = ?
    """, (disciplina_id,))

    quantidade_assuntos = cursor.fetchone()[0]

    if quantidade_assuntos > 0:

        print(
            f"\n❌ Não é possível excluir '{nome}'."
        )

        print(
            f"Ela possui {quantidade_assuntos} assunto(s) cadastrado(s)."
        )

        conexao.close()
        return

    confirmacao = input(
        f"\nTem certeza que deseja excluir '{nome}'? (S/N): "
    ).strip().upper()

    if confirmacao != "S":

        print("\nOperação cancelada.")
        conexao.close()
        return

    cursor.execute("""
        DELETE FROM materias
        WHERE id = ?
    """, (disciplina_id,))

    conexao.commit()
    conexao.close()

    print("\n✅ Disciplina excluída com sucesso!")


# ==========================================
# FAZER QUIZ
# ==========================================

def iniciar_quiz():
    questoes = buscar_questoes(limite=10)

    if not questoes:
        print("\nNenhuma questão cadastrada.")
        return

    pontos = 0

    print("\n" + "=" * 50)
    print("                 🎯 QUIZ")
    print("=" * 50)

    for numero, questao in enumerate(questoes, 1):

        (
            questao_id,
            pergunta,
            a,
            b,
            c,
            d,
            correta,
            explicacao,
            dificuldade
        ) = questao

        print("\n" + "=" * 50)
        print(f"Questão {numero}/{len(questoes)}")
        print("=" * 50)

        print(f"\n{pergunta}\n")

        print(f"A) {a}")
        print(f"B) {b}")
        print(f"C) {c}")
        print(f"D) {d}")

        while True:
            resposta = input("\nSua resposta: ").strip().upper()

            if resposta in ["A", "B", "C", "D"]:
                break

            print("Digite apenas A, B, C ou D.")

        if resposta == correta:
            print("\n✅ CORRETO!")
            pontos += 1
            acertou = 1

        else:
            print("\n❌ INCORRETO!")
            print(f"Resposta correta: {correta}")
            print(f"💡 {explicacao}")
            acertou = 0

        salvar_resposta(
            questao_id,
            resposta,
            acertou
        )

    mostrar_resultado(
        pontos,
        len(questoes)
    )


# ==========================================
# DESEMPENHO
# ==========================================

def mostrar_desempenho():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            COUNT(*),
            COALESCE(SUM(correta), 0)
        FROM respostas
    """)

    total, acertos = cursor.fetchone()

    print("\n" + "=" * 50)
    print("              MEU DESEMPENHO")
    print("=" * 50)

    if total == 0:
        print("\nVocê ainda não respondeu nenhuma questão.")
        conexao.close()
        return

    porcentagem = (acertos / total) * 100
    erros = total - acertos

    print(f"\n📝 Questões respondidas: {total}")
    print(f"✅ Acertos: {acertos}")
    print(f"❌ Erros: {erros}")
    print(f"📊 Aproveitamento geral: {porcentagem:.0f}%")

    # ======================================
    # POR MATÉRIA
    # ======================================

    print("\n" + "-" * 50)
    print("📚 DESEMPENHO POR MATÉRIA")
    print("-" * 50)

    cursor.execute("""
        SELECT
            m.nome,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        JOIN materias m ON q.materia_id = m.id
        GROUP BY m.id
        ORDER BY m.nome
    """)

    materias = cursor.fetchall()

    for nome, total_materia, acertos_materia in materias:

        aproveitamento = (
            acertos_materia / total_materia
        ) * 100

        if aproveitamento >= 80:
            indicador = "🟢"

        elif aproveitamento >= 60:
            indicador = "🟡"

        else:
            indicador = "🔴"

        print(
            f"\n{indicador} {nome}: "
            f"{acertos_materia}/{total_materia} "
            f"({aproveitamento:.0f}%)"
        )

    # ======================================
    # POR ASSUNTO
    # ======================================

    print("\n" + "-" * 50)
    print("🧠 DESEMPENHO POR ASSUNTO")
    print("-" * 50)

    cursor.execute("""
        SELECT
            m.nome,
            a.nome,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        JOIN materias m ON q.materia_id = m.id
        JOIN assuntos a ON q.assunto_id = a.id
        GROUP BY a.id
        ORDER BY m.nome, a.nome
    """)

    assuntos = cursor.fetchall()

    if not assuntos:
        print("\nNenhum assunto possui respostas ainda.")

    else:

        materia_atual = None

        for (
            materia,
            assunto,
            total_assunto,
            acertos_assunto
        ) in assuntos:

            if materia != materia_atual:
                print(f"\n📚 {materia}")
                materia_atual = materia

            aproveitamento = (
                acertos_assunto / total_assunto
            ) * 100

            if aproveitamento >= 80:
                indicador = "🟢"

            elif aproveitamento >= 60:
                indicador = "🟡"

            else:
                indicador = "🔴"

            print(
                f"   {indicador} {assunto}: "
                f"{acertos_assunto}/{total_assunto} "
                f"({aproveitamento:.0f}%)"
            )

    # ======================================
    # POR DIFICULDADE
    # ======================================

    print("\n" + "-" * 50)
    print("🎯 DESEMPENHO POR DIFICULDADE")
    print("-" * 50)

    cursor.execute("""
        SELECT
            q.dificuldade,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        GROUP BY q.dificuldade
        ORDER BY q.dificuldade
    """)

    dificuldades = cursor.fetchall()

    nomes_dificuldade = {
        1: "🟢 Fácil",
        2: "🟡 Médio",
        3: "🔴 Difícil"
    }

    for dificuldade, total_dificuldade, acertos_dificuldade in dificuldades:

        aproveitamento = (
            acertos_dificuldade / total_dificuldade
        ) * 100

        nome = nomes_dificuldade.get(
            dificuldade,
            "Desconhecida"
        )

        print(
            f"\n{nome}: "
            f"{acertos_dificuldade}/{total_dificuldade} "
            f"({aproveitamento:.0f}%)"
        )

    # ======================================
    # PONTO FRACO
    # ======================================

    cursor.execute("""
        SELECT
            a.nome,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        JOIN assuntos a ON q.assunto_id = a.id
        GROUP BY a.id
        HAVING COUNT(r.id) >= 3
        ORDER BY
            CAST(SUM(r.correta) AS FLOAT) / COUNT(r.id) ASC
        LIMIT 1
    """)

    pior = cursor.fetchone()

    if pior:

        assunto, total_pior, acertos_pior = pior

        aproveitamento = (
            acertos_pior / total_pior
        ) * 100

        print("\n" + "-" * 50)
        print("🎯 RECOMENDAÇÃO")
        print("-" * 50)

        if aproveitamento >= 80:
            indicador = "🟢"
            recomendacao = "Você está indo muito bem neste assunto!"

        elif aproveitamento >= 60:
           indicador = "🟡"
           recomendacao = "Continue praticando este assunto."

        else:
            indicador = "🔴"
            recomendacao = "Revise este assunto antes de continuar."

        print(
            f"\n{indicador} {assunto} — "
            f"{aproveitamento:.0f}%"
        )

        print(
            f"Você acertou {acertos_pior} "
            f"de {total_pior} questões."
        )

        print(
            f"\n💡 Recomendação: {recomendacao}"
        )

    conexao.close()


# ==========================================
# ESTUDAR PONTO FRACO
# ==========================================

def estudar_ponto_fraco():
    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            a.id,
            a.nome,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        JOIN assuntos a ON q.assunto_id = a.id
        GROUP BY a.id
        HAVING COUNT(r.id) >= 3
        ORDER BY
            CAST(SUM(r.correta) AS FLOAT) / COUNT(r.id) ASC
        LIMIT 1
    """)

    ponto_fraco = cursor.fetchone()

    conexao.close()

    if not ponto_fraco:
        print("\nAinda não existem dados suficientes.")
        print("Faça alguns quizzes primeiro.")
        return

    assunto_id = ponto_fraco[0]
    assunto_nome = ponto_fraco[1]

    print("\n" + "=" * 50)
    print("          📖 ESTUDAR PONTO FRACO")
    print("=" * 50)

    print(f"\n🔴 Assunto: {assunto_nome}")

    questoes = buscar_questoes(
        assunto_id=assunto_id,
        limite=10
    )

    if not questoes:
        print("\nNão existem questões nesse assunto.")
        return

    pontos = 0

    for numero, questao in enumerate(questoes, 1):

        (
            questao_id,
            pergunta,
            a,
            b,
            c,
            d,
            correta,
            explicacao,
            dificuldade
        ) = questao

        print("\n" + "=" * 50)
        print(f"Questão {numero}/{len(questoes)}")
        print("=" * 50)

        print(f"\n{pergunta}\n")

        print(f"A) {a}")
        print(f"B) {b}")
        print(f"C) {c}")
        print(f"D) {d}")

        while True:
            resposta = input("\nSua resposta: ").strip().upper()

            if resposta in ["A", "B", "C", "D"]:
                break

            print("Digite apenas A, B, C ou D.")

        if resposta == correta:

            print("\n✅ CORRETO!")
            pontos += 1
            acertou = 1

        else:

            print("\n❌ INCORRETO!")
            print(f"Resposta correta: {correta}")
            print(f"💡 {explicacao}")
            acertou = 0

        salvar_resposta(
            questao_id,
            resposta,
            acertou
        )

    mostrar_resultado(
        pontos,
        len(questoes)
    )


# ==========================================
# QUIZ ADAPTATIVO
# ==========================================

def quiz_adaptativo():

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            a.id,
            a.nome,
            COUNT(r.id),
            COALESCE(SUM(r.correta), 0)
        FROM respostas r
        JOIN questoes q ON r.questao_id = q.id
        JOIN assuntos a ON q.assunto_id = a.id
        GROUP BY a.id
        HAVING COUNT(r.id) >= 1
        ORDER BY
            CAST(SUM(r.correta) AS FLOAT) / COUNT(r.id) ASC
        LIMIT 1
    """)

    assunto = cursor.fetchone()

    conexao.close()

    if not assunto:
        print("\nAinda não temos dados suficientes.")
        print("Faça alguns quizzes primeiro.")
        return

    assunto_id = assunto[0]
    assunto_nome = assunto[1]

    nivel = 1
    pontos = 0
    total_questoes = 10

    questoes_usadas = set()

    print("\n" + "=" * 50)
    print("             🤖 QUIZ ADAPTATIVO")
    print("=" * 50)

    print(f"\n🧠 Assunto: {assunto_nome}")
    print("O nível será ajustado conforme suas respostas.")

    for numero in range(1, total_questoes + 1):

        conexao = conectar()
        cursor = conexao.cursor()

        # Primeiro tenta encontrar questões
        # do nível atual que ainda não foram usadas.
        cursor.execute("""
            SELECT
                id,
                pergunta,
                alternativa_a,
                alternativa_b,
                alternativa_c,
                alternativa_d,
                correta,
                explicacao,
                dificuldade
            FROM questoes
            WHERE assunto_id = ?
              AND dificuldade = ?
            ORDER BY RANDOM()
        """, (assunto_id, nivel))

        candidatos = cursor.fetchall()

        candidatos = [
            questao
            for questao in candidatos
            if questao[0] not in questoes_usadas
        ]

        # Se não houver questões disponíveis
        # no nível atual, procura em qualquer nível.
        if not candidatos:

            cursor.execute("""
                SELECT
                    id,
                    pergunta,
                    alternativa_a,
                    alternativa_b,
                    alternativa_c,
                    alternativa_d,
                    correta,
                    explicacao,
                    dificuldade
                FROM questoes
                WHERE assunto_id = ?
                ORDER BY RANDOM()
            """, (assunto_id,))

            candidatos = [
                questao
                for questao in cursor.fetchall()
                if questao[0] not in questoes_usadas
            ]

        conexao.close()

        # Se todas as questões já foram usadas,
        # encerra o quiz.
        if not candidatos:

            print("\n⚠️ Não existem mais questões diferentes nesse assunto.")

            print(
                f"\nVocê respondeu "
                f"{len(questoes_usadas)} questão(ões)."
            )

            break

        # Escolhe uma questão aleatória ainda não utilizada.
        questao = candidatos[0]

        questoes_usadas.add(questao[0])

        (
            questao_id,
            pergunta,
            a,
            b,
            c,
            d,
            correta,
            explicacao,
            dificuldade
        ) = questao

        niveis = {
            1: "🟢 Fácil",
            2: "🟡 Médio",
            3: "🔴 Difícil"
        }

        print("\n" + "=" * 50)
        print(f"Questão {numero}/{total_questoes}")
        print(
            f"Nível: {niveis.get(dificuldade, 'Desconhecido')}"
        )
        print("=" * 50)

        print(f"\n{pergunta}\n")

        print(f"A) {a}")
        print(f"B) {b}")
        print(f"C) {c}")
        print(f"D) {d}")

        while True:

            resposta = input(
                "\nSua resposta: "
            ).strip().upper()

            if resposta in ["A", "B", "C", "D"]:
                break

            print("Digite apenas A, B, C ou D.")

        if resposta == correta:

            print("\n✅ CORRETO!")

            pontos += 1
            acertou = 1

            # Acertou → aumenta a dificuldade.
            if nivel < 3:
                nivel += 1

        else:

            print("\n❌ INCORRETO!")

            print(f"Resposta correta: {correta}")
            print(f"💡 {explicacao}")

            acertou = 0

            # Errou → diminui a dificuldade.
            if nivel > 1:
                nivel -= 1

        salvar_resposta(
            questao_id,
            resposta,
            acertou
        )

    mostrar_resultado(
        pontos,
        len(questoes_usadas)
    )
# ==========================================
# REVISÃO INTELIGENTE
# ==========================================

def revisao_inteligente():
    print("\n" + "=" * 50)
    print("          🧠 REVISÃO INTELIGENTE")
    print("=" * 50)

    conexao = conectar()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            q.id,
            q.pergunta,
            a.nome,
            COUNT(r.id) AS tentativas,
            COALESCE(SUM(r.correta), 0) AS acertos
        FROM questoes q
        JOIN assuntos a ON q.assunto_id = a.id
        LEFT JOIN respostas r ON q.id = r.questao_id
        GROUP BY q.id
        HAVING tentativas > 0
        ORDER BY
            CAST(acertos AS FLOAT) / tentativas ASC
        LIMIT 5
    """)

    questoes = cursor.fetchall()

    conexao.close()

    if not questoes:

        print("\nAinda não existem questões suficientes para revisão.")
        return

    print("\n📌 Questões que merecem sua atenção:\n")

    for numero, questao in enumerate(questoes, 1):

        (
            questao_id,
            pergunta,
            assunto,
            tentativas,
            acertos
        ) = questao

        aproveitamento = (
            acertos / tentativas
        ) * 100

        print(f"{numero}. {assunto}")
        print(f"   {pergunta}")
        print(
            f"   📊 Aproveitamento: "
            f"{aproveitamento:.0f}%"
        )
        print()

# ==========================================
# GERENCIAR DISCIPLINAS
# ==========================================

def gerenciar_disciplinas():

    while True:

        print("\n")
        print("=" * 45)
        print("             DISCIPLINAS")
        print("=" * 45)

        print("\n1. Criar disciplina")
        print("2. Listar disciplinas")
        print("3. Editar disciplina")
        print("4. Excluir disciplina")
        print("5. Voltar")

        escolha = input("\nEscolha uma opção: ").strip()

        if escolha == "1":
            criar_disciplina()

        elif escolha == "2":
            listar_disciplinas()

        elif escolha == "3":
            editar_disciplina()

        elif escolha == "4":
            excluir_disciplina()

        elif escolha == "5":
            break

        else:
            print("\n❌ Opção inválida.")

# ==========================================
# CRIAR DISCIPLINA
# ==========================================

def criar_disciplina():

    print("\n" + "=" * 45)
    print("           CRIAR DISCIPLINA")
    print("=" * 45)

    nome = input("\nNome da disciplina: ").strip()

    if not nome:
        print("\n❌ O nome não pode ficar vazio.")
        return

    conexao = conectar()
    cursor = conexao.cursor()

    try:

        cursor.execute("""
            INSERT INTO materias (nome)
            VALUES (?)
        """, (nome,))

        conexao.commit()

        print("\n✅ Disciplina criada com sucesso!")

    except sqlite3.IntegrityError:

        print("\n❌ Essa disciplina já existe.")

    finally:

        conexao.close()

# ==========================================
# CADASTRAR QUESTÕES
# ==========================================

def cadastrar_questao():

    print("\n")
    print("=" * 45)
    print("          ✏️ CADASTRAR QUESTÃO")
    print("=" * 45)

    conexao = conectar()
    cursor = conexao.cursor()

    # ==============================
    # ESCOLHER MATÉRIA
    # ==============================

    cursor.execute("""
        SELECT id, nome
        FROM materias
        ORDER BY nome
    """)

    materias = cursor.fetchall()

    if not materias:
        print("\n❌ Nenhuma matéria cadastrada.")
        conexao.close()
        return

    print("\n📚 Matérias:")

    for materia in materias:
        print(f"{materia[0]}. {materia[1]}")

    while True:

        try:
            materia_id = int(
                input("\nEscolha a matéria: ")
            )

            if any(m[0] == materia_id for m in materias):
                break

            print("❌ Matéria inválida.")

        except ValueError:
            print("❌ Digite apenas o número da matéria.")

    # ==============================
    # ESCOLHER ASSUNTO
    # ==============================

    cursor.execute("""
        SELECT id, nome
        FROM assuntos
        WHERE materia_id = ?
        ORDER BY id
    """, (materia_id,))

    assuntos = cursor.fetchall()

    if not assuntos:
        print("\n❌ Essa matéria não possui assuntos cadastrados.")
        conexao.close()
        return

    print("\n🧠 Assuntos:")

    for assunto in assuntos:
        print(f"{assunto[0]}. {assunto[1]}")

    while True:

        try:
            assunto_id = int(
                input("\nEscolha o assunto: ")
            )

            if any(a[0] == assunto_id for a in assuntos):
                break

            print("❌ Assunto inválido.")

        except ValueError:
            print("❌ Digite apenas o número do assunto.")

    # ==============================
    # PERGUNTA
    # ==============================

    pergunta = input("\n📝 Pergunta: ").strip()

    while not pergunta:
        print("❌ A pergunta não pode ficar vazia.")
        pergunta = input("📝 Pergunta: ").strip()

    # ==============================
    # ALTERNATIVAS
    # ==============================

    alternativa_a = input("\nA) ").strip()
    alternativa_b = input("B) ").strip()
    alternativa_c = input("C) ").strip()
    alternativa_d = input("D) ").strip()

    # ==============================
    # RESPOSTA CORRETA
    # ==============================

    while True:

        correta = input(
            "\n✅ Resposta correta (A/B/C/D): "
        ).strip().upper()

        if correta in ["A", "B", "C", "D"]:
            break

        print("❌ Digite A, B, C ou D.")

    # ==============================
    # EXPLICAÇÃO
    # ==============================

    explicacao = input(
        "\n💡 Explicação: "
    ).strip()

    # ==============================
    # DIFICULDADE
    # ==============================

    print("\n🎯 Dificuldade:")
    print("1. 🟢 Fácil")
    print("2. 🟡 Médio")
    print("3. 🔴 Difícil")

    while True:

        dificuldade = input(
            "\nEscolha a dificuldade: "
        ).strip()

        if dificuldade in ["1", "2", "3"]:
            dificuldade = int(dificuldade)
            break

        print("❌ Escolha 1, 2 ou 3.")

    # ==============================
    # SALVAR
    # ==============================

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
        alternativa_a,
        alternativa_b,
        alternativa_c,
        alternativa_d,
        correta,
        explicacao,
        dificuldade
    ))

    conexao.commit()
    conexao.close()

    print("\n" + "=" * 45)
    print("✅ QUESTÃO CADASTRADA COM SUCESSO!")
    print("=" * 45)


# ==========================================
# MENU
# ==========================================
def menu():

    while True:

        print("\n")
        print("=" * 45)
        print("                 FACULQUIZ")
        print("=" * 45)

        print("\n1. 🎯 Fazer quiz")
        print("2. 📊 Meu desempenho")
        print("3. 🧠 Revisão inteligente")
        print("4. 📖 Estudar ponto fraco")
        print("5. 🤖 Quiz adaptativo")
        print("6. ✏️ Cadastrar questão")
        print("7. 📚 Disciplinas")
        print("7. ❌ Sair")

        escolha = input(
            "\nEscolha uma opção: "
        ).strip()

        if escolha == "1":

            iniciar_quiz()

        elif escolha == "2":

            mostrar_desempenho()

        elif escolha == "3":

            revisao_inteligente()

        elif escolha == "4":

            estudar_ponto_fraco()

        elif escolha == "5":

            quiz_adaptativo()

        elif escolha == "6":

            cadastrar_questao()

        elif escolha == "7":

            gerenciar_disciplinas()

        elif escolha == "8":

            print("\nAté a próxima! 👋")
            break

        else:

            print("\n❌ Opção inválida.")


# ==========================================
# INICIAR PROGRAMA
# ==========================================

if __name__ == "__main__":
    menu()
