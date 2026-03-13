# DelMessages

Apaga **todas** as mensagens enviadas por você em um chat do Telegram, para todos os participantes, usando a API oficial via [Telethon](https://github.com/LonamiWebs/Telethon).

## Pré-requisitos

- Python 3.10+
- Conta no Telegram com credenciais de API obtidas em [my.telegram.org](https://my.telegram.org)

## Instalação

```bash
git clone https://github.com/archwes/DelMessages.git
cd DelMessages
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuração

Copie o arquivo de exemplo e preencha com suas credenciais:

```bash
cp .env.example .env
```

Edite `.env`:

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
PHONE=+5511999999999
TWOFA_PASSWORD=           # deixe vazio se não usar 2FA
AUTO_CONFIRM=true         # true = não pede confirmação manual
```

> **.env nunca deve ser commitado.** Ele já está no `.gitignore`.

## Uso

```bash
python3 delete_telegram.py
```

O script pedirá o nome do chat/contato/grupo no terminal e apagará todas as suas mensagens.

### Opções

| Argumento  | Descrição                                          |
|------------|----------------------------------------------------|
| `--yes`    | Confirma a exclusão sem prompt manual              |
| `--dry-run`| Conta as mensagens sem apagar                      |

### Exemplos

```bash
# Apagar tudo sem confirmação manual
python3 delete_telegram.py --yes

# Simular sem apagar
python3 delete_telegram.py --dry-run
```

## Primeiro login

Na primeira execução, o Telegram pede o código enviado ao seu app/SMS. Após isso, a sessão fica salva localmente em `session_delete_msgs.session` e as próximas execuções são automáticas.

## Avisos

- Mensagens muito antigas ou em supergrupos com restrições podem não ser apagáveis pelo Telegram.
- A sessão (`.session`) contém tokens de autenticação — não compartilhe esse arquivo.
