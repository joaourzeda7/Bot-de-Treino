# Treino Bot 🏋️

Bot do Telegram para registrar treinos de musculação (foco em low volume) e gerar relatórios de progressão de carga, separando séries de aquecimento, preparatórias e de trabalho.

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
   git clone <seu-repo>
   cd treino-bot
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

## Próximos passos (roadmap)

- [ ] Hospedar em servidor (Render/Railway) para funcionar 24/7
- [ ] Botões de menu ao invés de texto livre (ConversationHandler)
- [ ] Exportação de relatório em PDF/planilha
- [ ] Gráfico de progressão de carga (matplotlib)
- [ ] Editar/deletar registros incorretos
