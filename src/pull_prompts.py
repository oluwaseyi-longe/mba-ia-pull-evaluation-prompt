"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Extrai os templates (system + human)
4. Salva localmente em YAML
"""

import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub

from utils import save_yaml


load_dotenv()


def pull_prompts_from_langsmith():
    prompt_id = "leonanluppi/bug_to_user_story_v1"
    print(f"Pulling prompt '{prompt_id}' from LangSmith Hub...")

    prompt = hub.pull(prompt_id)
    return prompt


def extract_templates(prompt):
    templates = {
        "system": None,
        "human": None,
    }

    messages = getattr(prompt, "messages", [])

    for msg in messages:
        class_name = msg.__class__.__name__

        if class_name == "SystemMessagePromptTemplate":
            templates["system"] = msg.prompt.template

        elif class_name == "HumanMessagePromptTemplate":
            templates["human"] = msg.prompt.template

    return templates


def main():
    prompt = pull_prompts_from_langsmith()
    print(prompt)

    templates = extract_templates(prompt)

    output_path = Path(__file__).parent.parent / "prompts" / "raw_prompts.yml"

    save_yaml(templates, output_path)

    print(f"Prompt salvo em: {output_path}")


if __name__ == "__main__":
    sys.exit(main())
