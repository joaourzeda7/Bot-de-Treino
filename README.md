# 🏋️ Treino Bot

Bot do Telegram para registrar treinos de musculação (foco em **low volume**) e gerar relatórios de progressão de carga, separando séries de aquecimento, preparatórias e de trabalho.

Projeto pessoal criado para resolver um problema real: substituir anotações manuais de treino por um registro rápido via chat, com histórico organizado e progressão de carga visível por exercício.

**Stack:** Python · python-telegram-bot · SQLite

## Funcionalidades

- Registro de treino via mensagem de texto simples
- Categorização por tipo de série: **aquecimento**, **preparatória** (feeder) e **trabalho**
- Resumo diário do treino (`/hoje`)
- Progressão histórica de carga por exercício (`/progresso`)
- Lista de exercícios já registrados (`/exercicios`)
- Armazenamento local em SQLite — sem dependência de servidor externo

## Formato de registro

Basta mandar uma mensagem de texto pro bot:

```
supino aquecimento 20kg 2x10
supino preparatoria 40kg 1x5
supino trabalho 60kg 4x10
```

Sinônimos aceitos para o tipo de série:
- `aquecimento` / `warm` / `warmup`
- `preparatoria` / `feeder`
- `trabalho` / `work` (assumido como padrão se não especificado)

## Comandos

| Comando | Descrição |
|---|---|
| `/start` | Mensagem de boas-vindas |
| `/ajuda` | Mostra o formato de registro |
| `/hoje` | Resumo do treino do dia |
| `/progresso <exercicio>` | Progressão de carga histórica |
| `/exercicios` | Lista exercícios já registrados |

## Como rodar

1. Clone o repositório:
   ```bash
   git clone https://github.com/joaourzeda7/Bot-de-Treino.git
   cd Bot-de-Treino
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Crie um bot no Telegram via [@BotFather](https://t.me/BotFather) e copie o token gerado.

4. Copie o arquivo de configuração de exemplo e cole seu token:
   ```bash
   cp config.py.example config.py
   ```
   Edite `config.py` e substitua `SEU_TOKEN_AQUI` pelo token real.

5. Rode o bot:
   ```bash
   python main.py
   ```

6. Abra o Telegram, procure pelo seu bot (pelo username escolhido no BotFather) e comece a mandar mensagens.

## Estrutura do projeto

```
treino_bot/
├── main.py                 # Ponto de entrada - handlers do bot
├── config.py.example       # Modelo de configuração (token NÃO incluído)
├── requirements.txt
├── bot/
│   └── parser.py           # Interpretação do texto livre
├── database/
│   └── db.py               # Schema e acesso ao SQLite
├── reports/
│   └── relatorios.py       # Geração de resumos e progressão
└── tests/
    └── teste_manual.py     # Teste manual sem precisar do Telegram
```

## Rodando os testes

```bash
python tests/teste_manual.py
```

## Por que esse projeto

Treino low-volume exige acompanhamento preciso de carga e repetições para garantir progressão real ao longo do tempo. Planilhas manuais funcionam, mas adicionam fricção no momento do treino. A ideia aqui foi reduzir esse atrito: registrar uma série direto no chat que você já usa, sem abrir app nenhum, e ter o histórico organizado automaticamente.

## Próximos passos (roadmap)

- [ ] Hospedar 24/7 em VPS gratuita (Oracle Cloud Free Tier — em andamento)
- [ ] Botões de menu ao invés de texto livre (ConversationHandler)
- [ ] Exportação de relatório em PDF/planilha
- [ ] Gráfico de progressão de carga (matplotlib)
- [ ] Editar/deletar registros incorretos
- [ ] Auto-restart do processo em caso de queda/reinício do servidor