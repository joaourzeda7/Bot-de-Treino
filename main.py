"""
Bot do Telegram para registro de treinos.

Comandos disponíveis:
    /start       - mensagem de boas-vindas e instruções
    /hoje        - resumo do treino do dia
    /progresso <exercicio> - progressão de carga histórica de um exercício
    /exercicios  - lista os exercícios já registrados
    /ajuda       - mostra o formato de registro

Para registrar um treino, basta mandar uma mensagem de texto livre, ex:
    supino trabalho 60kg 4x10
"""

import logging

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_TOKEN
from database import db
from bot.parser import parse_mensagem, ParseError
from reports import relatorios

# Configuração básica de log - ajuda a debugar quando algo dá errado
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


MENSAGEM_AJUDA = (
    "📌 *Como registrar um treino:*\n\n"
    "Manda uma mensagem no formato:\n"
    "`exercicio tipo carga kg seriesxrepeticoes`\n\n"
    "*Tipos de série aceitos:*\n"
    "• aquecimento / warm\n"
    "• preparatoria / feeder\n"
    "• trabalho / work (default, se não especificar)\n\n"
    "*Exemplos:*\n"
    "`supino aquecimento 20kg 2x10`\n"
    "`supino preparatoria 40kg 1x5`\n"
    "`supino trabalho 60kg 4x10`\n\n"
    "*Comandos:*\n"
    "/hoje - resumo do treino de hoje\n"
    "/progresso supino - progressão de carga no supino\n"
    "/exercicios - lista exercícios já registrados\n"
    "/ajuda - mostra esta mensagem"
)


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /start."""
    await update.message.reply_text(
        "💪 Bot de registro de treinos ativado!\n\n" + MENSAGEM_AJUDA,
        parse_mode="Markdown",
    )


async def cmd_ajuda(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /ajuda."""
    await update.message.reply_text(MENSAGEM_AJUDA, parse_mode="Markdown")


async def cmd_hoje(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /hoje - mostra o resumo do treino do dia."""
    user_id = update.effective_user.id
    texto = relatorios.resumo_dia(user_id)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_progresso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /progresso <exercicio> - mostra a progressão de carga."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "Uso: /progresso <nome do exercicio>\nEx: /progresso supino"
        )
        return

    exercicio = " ".join(context.args)
    texto = relatorios.progressao_exercicio(user_id, exercicio)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def cmd_exercicios(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handler do comando /exercicios - lista todos os exercícios já registrados."""
    user_id = update.effective_user.id
    texto = relatorios.listar_exercicios(user_id)
    await update.message.reply_text(texto, parse_mode="Markdown")


async def handler_mensagem_texto(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para qualquer mensagem de texto que não seja comando.
    Tenta interpretar como um registro de treino.
    """
    user_id = update.effective_user.id
    texto = update.message.text

    try:
        registro = parse_mensagem(texto)
    except ParseError as e:
        await update.message.reply_text(f"❌ {e}")
        return

    db.inserir_registro(
        user_id=user_id,
        exercicio=registro.exercicio,
        tipo_serie=registro.tipo_serie,
        carga=registro.carga,
        series=registro.series,
        repeticoes=registro.repeticoes,
        texto_original=texto,
    )

    carga_fmt = f"{registro.carga:g}"
    await update.message.reply_text(
        f"✅ Registrado: *{registro.exercicio}* ({registro.tipo_serie}) "
        f"{carga_fmt}kg {registro.series}x{registro.repeticoes}",
        parse_mode="Markdown",
    )


def main() -> None:
    """Inicializa o banco de dados e inicia o bot em modo polling."""
    db.inicializar_banco()
    logger.info("Banco de dados inicializado.")

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("ajuda", cmd_ajuda))
    app.add_handler(CommandHandler("hoje", cmd_hoje))
    app.add_handler(CommandHandler("progresso", cmd_progresso))
    app.add_handler(CommandHandler("exercicios", cmd_exercicios))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handler_mensagem_texto))

    logger.info("Bot iniciado. Esperando mensagens...")
    app.run_polling()


if __name__ == "__main__":
    main()
