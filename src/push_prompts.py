"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate

from utils import (
    load_yaml,
    check_env_vars,
    print_section_header,
    validate_prompt_structure,
)

load_dotenv()

PROMPTS_FILE = Path(__file__).resolve().parent.parent / "prompts" / "bug_to_user_story_v2.yml"
DEFAULT_PROMPT_KEY = "bug_to_user_story_v2"


def _hub_repo_full_name(prompt_name: str) -> str | None:
    username = os.getenv("USERNAME_LANGSMITH_HUB", "").strip()
    if not username:
        return None
    return f"{username}/{prompt_name}"


def _build_readme(prompt_data: dict) -> str | None:
    parts = []
    desc = prompt_data.get("description")
    if desc:
        parts.append(str(desc).strip())
    techniques = prompt_data.get("techniques_applied")
    if techniques:
        parts.append("Técnicas aplicadas:\n- " + "\n- ".join(str(t) for t in techniques))
    version = prompt_data.get("version")
    if version:
        parts.append(f"Versão: {version}")
    if not parts:
        return None
    return "\n\n".join(parts)


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    repo_full_name = _hub_repo_full_name(prompt_name)
    if not repo_full_name:
        print("❌ USERNAME_LANGSMITH_HUB não está definido no .env.")
        print("   Defina o seu usuário do LangSmith Hub (ex.: leonanluppi).")
        return False

    system_prompt = prompt_data.get("system_prompt", "")
    user_prompt = prompt_data.get("user_prompt", "{bug_report}")

    try:
        chat = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", user_prompt),
            ]
        )
    except Exception as e:
        print(f"❌ Erro ao montar ChatPromptTemplate: {e}")
        return False

    tags = prompt_data.get("tags") or []
    description = prompt_data.get("description")
    readme = _build_readme(prompt_data)

    try:
        commit = hub.push(
            repo_full_name,
            chat,
            new_repo_is_public=True,
            new_repo_description=description,
            readme=readme,
            tags=tags if tags else None,
        )
        print(f"✓ Push concluído: {repo_full_name}")
        if commit:
            print(f"  Commit: {commit}")
        return True
    except Exception as e:
        print(f"❌ Erro ao fazer push para o LangSmith Hub: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS AO LANGSMITH HUB")

    required = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required):
        return 1

    yaml_data = load_yaml(str(PROMPTS_FILE))
    if yaml_data is None:
        return 1

    prompt_key = DEFAULT_PROMPT_KEY
    if prompt_key not in yaml_data:
        keys = list(yaml_data.keys())
        if len(keys) == 1:
            prompt_key = keys[0]
            print(f"⚠️  Chave '{DEFAULT_PROMPT_KEY}' não encontrada; usando '{prompt_key}'.")
        else:
            print(
                f"❌ Esperada a chave '{DEFAULT_PROMPT_KEY}' em {PROMPTS_FILE}. "
                f"Chaves encontradas: {keys}"
            )
            return 1

    prompt_data = yaml_data[prompt_key]
    if not isinstance(prompt_data, dict):
        print("❌ Entrada do YAML inválida: esperado um objeto por prompt.")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Validação do prompt falhou:")
        for err in errors:
            print(f"   - {err}")
        return 1

    print("✓ Validação do prompt OK.\n")

    prompt_name = prompt_key
    if not push_prompt_to_langsmith(prompt_name, prompt_data):
        return 1

    print("\nConfira o prompt em: https://smith.langchain.com/prompts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
