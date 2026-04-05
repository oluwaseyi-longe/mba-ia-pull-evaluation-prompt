"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
import re
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

# Adicionar src ao path
sys.path.insert(0, str(ROOT_DIR))

from src.utils import validate_prompt_structure


PROMPTS_FILE = ROOT_DIR / "prompts" / "bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"

def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_payload():
    """Carrega o YAML completo do prompt otimizado."""
    payload = load_prompts(str(PROMPTS_FILE))
    assert payload is not None, "Falha ao carregar o arquivo de prompts"
    assert PROMPT_KEY in payload, f"Chave '{PROMPT_KEY}' não encontrada no YAML"
    return payload


@pytest.fixture(scope="module")
def prompt_data(prompt_payload):
    """Retorna apenas os dados do prompt principal."""
    prompt = prompt_payload[PROMPT_KEY]
    assert isinstance(prompt, dict), "A entrada do prompt deve ser um dicionário"
    return prompt

class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio. (checar se system_prompt contem dado)"""
        is_valid, errors = validate_prompt_structure(prompt_data)

        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado"
        assert prompt_data["system_prompt"].strip(), "Campo 'system_prompt' está vazio"
        assert "system_prompt está vazio" not in errors
        assert is_valid, f"Estrutura básica do prompt inválida: {errors}"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager"). procurar string "Você é" ou "You are" no system_prompt)"""
        system_prompt = prompt_data["system_prompt"]
        assert re.search(r"\b(Você é|You are)\b", system_prompt), (
            "O prompt deve definir uma persona com 'Você é' ou 'You are'"
        )

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data["system_prompt"]
        mentions_format = any(term in system_prompt for term in [
            "User Story",
            "Como um",
            "formato",
            "template",
            "Markdown",
        ])

        assert mentions_format, (
            "O prompt deve exigir um formato de saída, como User Story padrão ou Markdown"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        system_prompt = prompt_data["system_prompt"]

        assert "exemplo" in system_prompt.lower(), "O prompt deve conter exemplos explícitos"
        assert system_prompt.count("Relato do Bug (prompt do usuario)") >= 2, (
            "O prompt deve conter pelo menos 2 exemplos de entrada"
        )
        assert system_prompt.count("Descrição do Bug") >= 3, (
            "O prompt deve conter saídas esperadas nos exemplos few-shot"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto. (verificar se a string '[TODO]' aparece no prompt)"""
        prompt_text = yaml.dump(prompt_data, allow_unicode=True, sort_keys=False)
        assert "[TODO]" not in prompt_text, "O prompt ainda contém marcações [TODO]"
        assert "TODO" not in prompt_text, "O prompt ainda contém marcações TODO"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas. (ver se a array techniques_applied é maior que 2)"""
        techniques = prompt_data.get("techniques_applied", [])

        assert isinstance(techniques, list), "'techniques_applied' deve ser uma lista"
        assert len(techniques) >= 2, (
            "O prompt deve listar pelo menos 2 técnicas em 'techniques_applied'"
        )

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])