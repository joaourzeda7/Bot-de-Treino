"""
Parser de texto livre para extrair dados de treino.

Formato esperado (flexível):
    <exercicio> <tipo_serie> <carga>kg <series>x<repeticoes>

Exemplos válidos:
    supino aquecimento 20kg 2x10
    supino trabalho 60kg 4x10
    rosca direta feeder 12kg 1x8
    leg press work 100 3x12
"""

import re
from dataclasses import dataclass

from database.db import TIPOS_SERIE


class ParseError(Exception):
    """Levantada quando o texto não pôde ser interpretado."""
    pass


@dataclass
class RegistroTreino:
    exercicio: str
    tipo_serie: str
    carga: float
    series: int
    repeticoes: int


# Regex que captura: carga (com ou sem "kg") e o padrão SxR (series x repeticoes)
# O "kg" é opcional, permitindo tanto "100 3x12" quanto "60kg 4x10"
_PADRAO_CARGA_SERIES = re.compile(
    r"(?P<carga>\d+(?:[.,]\d+)?)\s*(?:kg)?\s+(?P<series>\d+)\s*x\s*(?P<reps>\d+)",
    re.IGNORECASE,
)


def _identificar_tipo_serie(texto: str) -> tuple[str, str]:
    """
    Procura por uma palavra-chave de tipo de série no texto.
    Retorna (tipo_normalizado, texto_sem_a_palavra_chave).
    Se nenhuma palavra-chave for encontrada, assume 'trabalho' como default.
    """
    palavras = texto.split()
    for i, palavra in enumerate(palavras):
        chave = palavra.lower().strip(".,!?")
        if chave in TIPOS_SERIE:
            tipo = TIPOS_SERIE[chave]
            texto_restante = " ".join(palavras[:i] + palavras[i + 1:])
            return tipo, texto_restante
    # Nenhuma palavra-chave encontrada -> default é série de trabalho
    return "trabalho", texto


def parse_mensagem(texto: str) -> RegistroTreino:
    """
    Interpreta uma linha de texto e retorna um RegistroTreino.
    Levanta ParseError se não conseguir interpretar.
    """
    texto_original = texto.strip()
    if not texto_original:
        raise ParseError("Mensagem vazia.")

    tipo_serie, texto_sem_tipo = _identificar_tipo_serie(texto_original)

    match = _PADRAO_CARGA_SERIES.search(texto_sem_tipo)
    if not match:
        raise ParseError(
            "Não entendi o formato. Use algo como:\n"
            "supino trabalho 60kg 4x10"
        )

    carga_str = match.group("carga").replace(",", ".")
    carga = float(carga_str)
    series = int(match.group("series"))
    repeticoes = int(match.group("reps"))

    # O nome do exercício é tudo que vem ANTES da carga
    exercicio = texto_sem_tipo[:match.start()].strip()
    if not exercicio:
        raise ParseError(
            "Não identifiquei o nome do exercício. Use algo como:\n"
            "supino trabalho 60kg 4x10"
        )

    return RegistroTreino(
        exercicio=exercicio,
        tipo_serie=tipo_serie,
        carga=carga,
        series=series,
        repeticoes=repeticoes,
    )
