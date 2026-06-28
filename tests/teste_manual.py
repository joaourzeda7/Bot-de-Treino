"""
Teste manual rápido - simula um fluxo de uso completo sem precisar do Telegram.
Roda com: python tests/teste_manual.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from database import db
from bot.parser import parse_mensagem, ParseError
from reports import relatorios

# Usa um banco de teste separado pra não misturar com dados reais
db.DB_PATH = Path(__file__).parent / "teste_treinos.db"
db.DB_PATH.unlink(missing_ok=True)  # garante banco limpo a cada execução

USER_ID_TESTE = 12345


def testar_parser():
    print("=== Testando parser ===")
    casos = [
        "supino aquecimento 20kg 2x10",
        "supino preparatoria 40kg 1x5",
        "supino trabalho 60kg 4x10",
        "rosca direta feeder 12kg 1x8",
        "leg press work 100 3x12",
        "agachamento 80kg 3x8",  # sem tipo -> default trabalho
        "texto invalido sem numero",  # deve dar erro
    ]
    for caso in casos:
        try:
            resultado = parse_mensagem(caso)
            print(f"OK   '{caso}' -> {resultado}")
        except ParseError as e:
            print(f"ERRO '{caso}' -> {e}")
    print()


def testar_fluxo_completo():
    print("=== Testando fluxo completo (banco + relatórios) ===")
    db.inicializar_banco()

    registros_teste = [
        "supino aquecimento 20kg 2x10",
        "supino preparatoria 40kg 1x5",
        "supino trabalho 60kg 4x10",
        "agachamento trabalho 80kg 3x8",
    ]

    for texto in registros_teste:
        r = parse_mensagem(texto)
        db.inserir_registro(
            user_id=USER_ID_TESTE,
            exercicio=r.exercicio,
            tipo_serie=r.tipo_serie,
            carga=r.carga,
            series=r.series,
            repeticoes=r.repeticoes,
            texto_original=texto,
        )

    print("\n--- Resumo do dia ---")
    print(relatorios.resumo_dia(USER_ID_TESTE))

    print("\n--- Exercícios registrados ---")
    print(relatorios.listar_exercicios(USER_ID_TESTE))

    print("\n--- Progressão do supino (apenas 1 dia, mas testa a função) ---")
    print(relatorios.progressao_exercicio(USER_ID_TESTE, "supino"))


if __name__ == "__main__":
    testar_parser()
    testar_fluxo_completo()
