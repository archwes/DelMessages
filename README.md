# DelMessages

Apaga **todas** as mensagens enviadas por você em um chat do Telegram, para todos os participantes, usando a API oficial via [Telethon](https://github.com/LonamiWebs/Telethon).

---

## Pré-requisitos

- Python 3.10+
- Git
- Credenciais de API do Telegram obtidas em [my.telegram.org](https://my.telegram.org)

### Como obter API_ID e API_HASH

1. Acesse [my.telegram.org](https://my.telegram.org) e faça login com seu número de telefone.
2. Clique em **API development tools**.
3. Preencha o formulário (nome e apelido do app podem ser qualquer coisa).
4. Copie o `api_id` (número) e o `api_hash` (texto) exibidos na página.

---

## Instalação e configuração

### Linux / macOS

```bash
# 1. Clone o repositório
git clone https://github.com/archwes/DelMessages.git
cd DelMessages

# 2. Crie e ative o ambiente virtual
python3 -m venv .venv
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Crie o arquivo de configuração
cp .env.example .env
```

Abra o arquivo `.env` em qualquer editor de texto e preencha:

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
PHONE=+5511999999999
TWOFA_PASSWORD=           # deixe vazio se não usar 2FA
AUTO_CONFIRM=true         # true = não pede confirmação manual
```

---

### Windows

```bat
REM 1. Clone o repositório
git clone https://github.com/archwes/DelMessages.git
cd DelMessages

REM 2. Crie e ative o ambiente virtual
python -m venv .venv
.venv\Scripts\activate

REM 3. Instale as dependências
pip install -r requirements.txt

REM 4. Crie o arquivo de configuração
copy .env.example .env
```

Abra o arquivo `.env` no Bloco de Notas ou qualquer editor e preencha:

```env
API_ID=seu_api_id
API_HASH=seu_api_hash
PHONE=+5511999999999
TWOFA_PASSWORD=           # deixe vazio se não usar 2FA
AUTO_CONFIRM=true         # true = não pede confirmação manual
```

> **.env nunca deve ser commitado.** Ele já está no `.gitignore`.

---

## Uso

### Linux / macOS

```bash
python3 delete_telegram.py
```

### Windows

```bat
python delete_telegram.py
```

O script pedirá o nome do chat/contato/grupo no terminal e apagará todas as suas mensagens.

### Opções

| Argumento   | Descrição                                      |
|-------------|------------------------------------------------|
| `--yes`     | Confirma a exclusão sem prompt manual          |
| `--dry-run` | Conta as mensagens sem apagar                  |

### Exemplos

**Linux / macOS**
```bash
# Apagar tudo sem confirmação manual
python3 delete_telegram.py --yes

# Simular sem apagar
python3 delete_telegram.py --dry-run
```

**Windows**
```bat
REM Apagar tudo sem confirmação manual
python delete_telegram.py --yes

REM Simular sem apagar
python delete_telegram.py --dry-run
```

---

## Primeiro login

Na primeira execução, o Telegram envia um código para o seu app ou SMS. Digite-o quando solicitado. Após isso, a sessão fica salva localmente em `session_delete_msgs.session` e as próximas execuções são automáticas.

---

## Avisos

- Mensagens muito antigas ou em supergrupos com restrições podem não ser apagáveis.
- A sessão (`.session`) contém tokens de autenticação — **não compartilhe esse arquivo**.
- Outra pessoa pode usar o mesmo `API_ID/API_HASH` para apagar as mensagens da conta dela: basta ela fazer login com o número de telefone dela.
