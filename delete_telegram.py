#!/usr/bin/env python3

"""
Apaga TODAS as mensagens enviadas por voce em um chat do Telegram, para todos.

Requisitos:
- pip install telethon
- Definir API_ID e API_HASH (env/.env ou prompt)

Exemplos:
- python3 delete_telegram.py
- API_ID=12345 API_HASH=abc123 python3 delete_telegram.py

Arquivo .env (opcional, recomendado para automacao):
- API_ID=12345
- API_HASH=abc123
- PHONE=+5511999999999
- TWOFA_PASSWORD=sua_senha_2fa
- AUTO_CONFIRM=true
"""

import argparse
import asyncio
import os
import unicodedata
from typing import Optional

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

SESSION_NAME = "session_delete_msgs"
BATCH_SIZE = 100
ENV_FILE = ".env"


def parse_bool(value: str) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "y", "on", "sim", "s"}


def load_dotenv(dotenv_path: str = ENV_FILE) -> None:
    if not os.path.exists(dotenv_path):
        return

    with open(dotenv_path, "r", encoding="utf-8") as fp:
        for raw_line in fp:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip("\"'")
            if key and key not in os.environ:
                os.environ[key] = value


def normalize_text(value: str) -> str:
    raw = (value or "").strip().lower()
    return "".join(
        ch
        for ch in unicodedata.normalize("NFD", raw)
        if unicodedata.category(ch) != "Mn"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Apaga todas as suas mensagens de um chat do Telegram para todos."
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Confirma exclusao automaticamente sem perguntar no terminal.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Nao apaga; apenas conta quantas mensagens suas seriam apagadas.",
    )
    return parser.parse_args()


def read_api_credentials() -> tuple[int, str]:
    api_id_raw = os.getenv("API_ID", "").strip()
    api_hash = os.getenv("API_HASH", "").strip()

    if not api_id_raw:
        api_id_raw = input("API_ID: ").strip()
    if not api_hash:
        api_hash = input("API_HASH: ").strip()

    if not api_id_raw.isdigit():
        raise RuntimeError("API_ID invalido. Deve ser numero inteiro.")
    if not api_hash:
        raise RuntimeError("API_HASH vazio.")

    return int(api_id_raw), api_hash


async def connect_client(api_id: int, api_hash: str) -> TelegramClient:
    client = TelegramClient(SESSION_NAME, api_id, api_hash)
    await client.connect()

    if not await client.is_user_authorized():
        phone = os.getenv("PHONE", "").strip()
        if not phone:
            phone = input("Telefone com DDI (ex.: +5511999999999): ").strip()
        await client.send_code_request(phone)

        # O codigo de login sempre depende do Telegram (SMS/app), entao prompt e inevitavel.
        code = input("Codigo recebido no Telegram: ").strip()
        try:
            await client.sign_in(phone=phone, code=code)
        except SessionPasswordNeededError:
            password = os.getenv("TWOFA_PASSWORD", "").strip()
            if not password:
                password = input("Senha 2FA: ").strip()
            await client.sign_in(password=password)

    return client


async def resolve_chat(client: TelegramClient, chat_query: str):
    # 1) Tenta resolver diretamente (username, link, id, etc.)
    try:
        return await client.get_entity(chat_query)
    except Exception:
        pass

    # 2) Fallback: procura por semelhanca no titulo dos dialogs
    target = normalize_text(chat_query)
    best_entity = None

    async for dialog in client.iter_dialogs():
        name_norm = normalize_text(dialog.name or "")
        if not name_norm:
            continue
        if target == name_norm or target in name_norm:
            best_entity = dialog.entity
            break

    if best_entity is None:
        raise RuntimeError(f"Nao encontrei chat/contato/grupo: {chat_query}")

    return best_entity


async def count_own_messages(client: TelegramClient, entity) -> int:
    total = 0
    async for _ in client.iter_messages(entity, from_user="me"):
        total += 1
    return total


async def delete_all_own_messages(client: TelegramClient, entity) -> tuple[int, int]:
    deleted_total = 0
    failed_total = 0
    buffer: list[int] = []

    async for msg in client.iter_messages(entity, from_user="me"):
        if not msg or not msg.id:
            continue
        buffer.append(msg.id)

        if len(buffer) >= BATCH_SIZE:
            try:
                await client.delete_messages(entity, buffer, revoke=True)
                deleted_total += len(buffer)
                print(f"Apagadas ate agora: {deleted_total}")
            except Exception:
                failed_total += len(buffer)
            finally:
                buffer = []

    if buffer:
        try:
            await client.delete_messages(entity, buffer, revoke=True)
            deleted_total += len(buffer)
            print(f"Apagadas ate agora: {deleted_total}")
        except Exception:
            failed_total += len(buffer)

    return deleted_total, failed_total


async def async_main() -> int:
    load_dotenv()
    args = parse_args()

    chat = input("Digite o nome do chat/contato/grupo: ").strip()
    if not chat:
        print("Nome do chat vazio. Encerrando.")
        return 1

    auto_confirm = args.yes or parse_bool(os.getenv("AUTO_CONFIRM", ""))
    api_id, api_hash = read_api_credentials()

    client: Optional[TelegramClient] = None
    try:
        client = await connect_client(api_id, api_hash)
        me = await client.get_me()
        print(f"Conectado como: {me.first_name or ''} (@{me.username or 'sem_username'})")

        entity = await resolve_chat(client, chat)
        print(f"Chat alvo resolvido com sucesso: {chat}")

        if args.dry_run:
            total = await count_own_messages(client, entity)
            print(f"[DRY-RUN] Total de mensagens suas no chat: {total}")
            return 0

        if not auto_confirm:
            confirmation = input(
                "Confirma apagar TODAS as suas mensagens para todos nesse chat? (digite APAGAR): "
            ).strip()
            if confirmation != "APAGAR":
                print("Operacao cancelada pelo usuario.")
                return 0

        deleted, failed = await delete_all_own_messages(client, entity)
        print(f"Finalizado. Apagadas: {deleted} | Falhas: {failed}")

        if failed > 0:
            print(
                "Algumas mensagens podem nao ter sido removidas por restricoes do Telegram "
                "(muito antigas, permissao, tipo de chat ou tipo de mensagem)."
            )

        return 0
    finally:
        if client:
            await client.disconnect()


def main() -> None:
    try:
        raise SystemExit(asyncio.run(async_main()))
    except KeyboardInterrupt:
        print("Interrompido pelo usuario.")
        raise SystemExit(130)
    except RuntimeError as err:
        print(f"Erro: {err}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
