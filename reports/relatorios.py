"""
Geração de relatórios a partir dos dados salvos no banco.

Dois tipos de relatório:
1. Resumo do dia/sessão (resumo_dia)
2. Progressão de carga por exercício (progressao_exercicio)
"""

from collections import defaultdict
from datetime import datetime

from database import db

EMOJI_TIPO = {
    "aquecimento": "🔸",
    "preparatoria": "🔹",
    "trabalho": "🔴",
}

NOME_TIPO = {
    "aquecimento": "Aquecimento",
    "preparatoria": "Preparatória",
    "trabalho": "Trabalho",
}


def resumo_dia(user_id: int, data: datetime = None) -> str:
    """Gera um resumo formatado de todos os registros de um dia, agrupados por exercício."""
    registros = db.buscar_registros_do_dia(user_id, data)

    if not registros:
        return "Nenhum registro encontrado para hoje. Manda seu primeiro set! 💪"

    # Agrupa por exercício, preservando a ordem de primeira aparição
    por_exercicio = defaultdict(list)
    ordem_exercicios = []
    for r in registros:
        if r["exercicio"] not in por_exercicio:
            ordem_exercicios.append(r["exercicio"])
        por_exercicio[r["exercicio"]].append(r)

    data_label = registros[0]["data_hora"][:10]
    linhas = [f"📋 *Resumo do treino - {data_label}*\n"]

    for exercicio in ordem_exercicios:
        linhas.append(f"*{exercicio.capitalize()}*")
        for r in por_exercicio[exercicio]:
            emoji = EMOJI_TIPO.get(r["tipo_serie"], "⚪")
            nome_tipo = NOME_TIPO.get(r["tipo_serie"], r["tipo_serie"])
            carga = r["carga"]
            carga_fmt = f"{carga:g}"  # remove .0 desnecessário
            linhas.append(
                f"  {emoji} {nome_tipo}: {carga_fmt}kg × {r['series']}x{r['repeticoes']}"
            )
        linhas.append("")  # linha em branco entre exercícios

    # Estatística rápida: volume total de séries de trabalho
    total_sets_trabalho = sum(
        1 for r in registros if r["tipo_serie"] == "trabalho"
    )
    linhas.append(f"✅ Total de séries de trabalho: {total_sets_trabalho}")

    return "\n".join(linhas)


def progressao_exercicio(user_id: int, exercicio: str) -> str:
    """
    Gera um relatório de progressão histórica de carga para um exercício,
    considerando apenas séries de trabalho (que refletem a carga real de esforço).
    """
    registros = db.buscar_historico_exercicio(user_id, exercicio)

    if not registros:
        return (
            f"Não encontrei histórico de '{exercicio}' nas séries de trabalho.\n"
            f"Confere o nome ou manda /exercicios pra ver os já registrados."
        )

    # Agrupa por dia, pegando a maior carga de trabalho do dia como referência
    por_dia = defaultdict(list)
    for r in registros:
        dia = r["data_hora"][:10]
        por_dia[dia].append(r["carga"])

    dias_ordenados = sorted(por_dia.keys())

    linhas = [f"📈 *Progressão - {exercicio.capitalize()}* (séries de trabalho)\n"]

    carga_anterior = None
    for dia in dias_ordenados:
        cargas_do_dia = por_dia[dia]
        carga_maxima = max(cargas_do_dia)
        carga_fmt = f"{carga_maxima:g}"

        seta = ""
        if carga_anterior is not None:
            if carga_maxima > carga_anterior:
                seta = " 📈"
            elif carga_maxima < carga_anterior:
                seta = " 📉"
            else:
                seta = " ➡️"

        linhas.append(f"{dia}: {carga_fmt}kg{seta}")
        carga_anterior = carga_maxima

    # Resumo da evolução total
    primeira_carga = por_dia[dias_ordenados[0]][0]
    ultima_carga = max(por_dia[dias_ordenados[-1]])
    diferenca = ultima_carga - primeira_carga

    linhas.append("")
    if diferenca > 0:
        linhas.append(f"🎉 Evolução total: +{diferenca:g}kg desde o primeiro registro")
    elif diferenca < 0:
        linhas.append(f"⚠️ Variação total: {diferenca:g}kg desde o primeiro registro")
    else:
        linhas.append("➡️ Carga estável desde o primeiro registro")

    return "\n".join(linhas)


def listar_exercicios(user_id: int) -> str:
    """Lista todos os exercícios já registrados pelo usuário, útil pra saber o nome exato a usar."""
    exercicios = db.buscar_todos_exercicios(user_id)
    if not exercicios:
        return "Nenhum exercício registrado ainda."

    linhas = ["📝 *Exercícios registrados:*\n"]
    linhas.extend(f"• {ex}" for ex in exercicios)
    return "\n".join(linhas)
