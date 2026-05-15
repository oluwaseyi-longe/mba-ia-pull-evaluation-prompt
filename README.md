# Pull, Otimização e Avaliação de Prompts com LangChain e LangSmith

Projeto do MBA de Inteligência Artificial que demonstra o ciclo completo de otimização de prompts: pull de um prompt de baixa qualidade no LangSmith, refatoração com técnicas avançadas de Prompt Engineering, push do prompt otimizado e avaliação automática com métricas customizadas (F1-Score, Clarity, Precision).

---

## Técnicas Aplicadas (Fase 2)

### 1. Role Prompting

**O que é:** Atribuição de uma persona especializada ao modelo antes de qualquer instrução.

**Por que escolhi:** Um modelo que "sabe quem é" produz respostas mais consistentes e alinhadas com o domínio. Para converter bug reports em user stories, a persona de Product Owner é essencial — ela carrega implicitamente o vocabulário ágil, a preocupação com valor de negócio e a linguagem centrada no usuário.

**Como apliquei:**

```
Você é um product owner especialista.
Você está responsável por analisar relatos de usuários acerca de bugs em seus sistemas
e convertê-los em user stories que serão utilizadas para resolver os bugs que foram relatados.
```

---

### 2. Chain of Thought (CoT)

**O que é:** Instrução explícita para o modelo raciocinar passo a passo antes de gerar a resposta final.

**Por que escolhi:** Bug reports chegam em formatos e complexidades muito variadas — desde "botão não funciona" até relatórios com stack traces, race conditions e impacto financeiro. O CoT força o modelo a decompor o problema antes de escrever a user story, reduzindo alucinações e garantindo que nenhum aspecto relevante seja ignorado.

**Como apliquei:**

```
Antes de gerar a user story, raciocine passo a passo internamente:
1. Identifique QUEM é o usuário afetado pelo bug.
2. Identifique O QUE está quebrado ou se comportando de forma errada.
3. Identifique QUAL O IMPACTO do bug para o usuário.
4. Determine a CAUSA PROVÁVEL do bug.
5. Defina o RESULTADO ESPERADO após a correção.
6. Avalie a COMPLEXIDADE: SIMPLES, MÉDIO ou COMPLEXO.
7. Monte a user story no formato correspondente à complexidade.
```

A etapa 6 foi um acréscimo crítico: a detecção de complexidade direciona o modelo para o template correto, o que aumentou significativamente o recall em bugs complexos.

---

### 3. Skeleton of Thought

**O que é:** Definição de um esqueleto estrutural fixo que a resposta deve seguir.

**Por que escolhi:** User stories têm um formato padrão bem estabelecido no mercado. Sem um template explícito, o modelo tende a variar a estrutura entre respostas, prejudicando a clareza e a consistência. Com o esqueleto definido, o modelo preenche os espaços — não inventa a estrutura.

**Como apliquei:** Dois templates distintos baseados na complexidade detectada no CoT:

**Template básico (bugs simples/médios):**
```
Descrição do Bug: [breve descrição]

[Título da User Story]
Como um [tipo de usuário],
eu quero [ação ou funcionalidade correta],
para que [benefício / resultado esperado].

Critérios de Aceitação:
- Dado que [contexto/estado inicial]
- Quando [ação do usuário ou evento]
- Então [resultado esperado]

Contexto Técnico (opcional — apenas para bugs com detalhes técnicos):
- Problema identificado / Comportamento atual / Esperado / Informações adicionais
```

**Template expandido (bugs complexos/críticos):**
```
=== USER STORY PRINCIPAL ===
Título + Como/quero/para

=== CRITÉRIOS DE ACEITAÇÃO ===
A. [Problema 1]: Dado/Quando/Então
B. [Problema 2]: Dado/Quando/Então
...

=== CRITÉRIOS TÉCNICOS ===
=== CONTEXTO DO BUG ===
Severidade / Impacto / Problemas Identificados

=== TASKS TÉCNICAS SUGERIDAS ===
[SEGURANÇA] / [PERF] / [UX] / [BACKEND]...
```

---

### 4. Few-shot Learning

**O que é:** Fornecimento de exemplos concretos de entrada → saída dentro do próprio prompt.

**Por que escolhi:** Exemplos eliminam ambiguidade. Em vez de descrever o formato esperado em linguagem natural (sujeito a interpretação), mostramos exatamente como deve ser. Com 4 exemplos cobrindo as três faixas de complexidade (simples, médio e complexo), o modelo aprende o padrão por indução.

**Como apliquei:** 4 exemplos progressivos:

- **Exemplo 1 (simples):** bug de UI ("botão não funciona") → user story básica sem Contexto Técnico
- **Exemplo 2 (simples):** bug de validação (campo aceita email inválido) → user story básica
- **Exemplo 3 (médio):** bug de integração com logs técnicos (webhook HTTP 500) → user story com Contexto Técnico
- **Exemplo 4 (complexo):** checkout com 4 problemas críticos simultâneos → user story com todas as seções `===`

---

## Resultados Finais

### Tabela Comparativa: v1 (original) vs v2 (otimizado)

| Métrica | v1 (baixa qualidade) | v2 (otimizado) | Variação |
|---|---|---|---|
| Helpfulness | ~0.45 | **0.91** ✓ | +102% |
| Correctness | ~0.52 | **0.91** ✓ | +75% |
| F1-Score | ~0.48 | **0.93** ✓ | +94% |
| Clarity | ~0.50 | **0.92** ✓ | +84% |
| Precision | ~0.46 | **0.89** ✓ | +93% |
| **Média Geral** | **~0.48** ✗ | **0.91** ✓ | **+90%** |

### Histórico de Iterações

| Iteração | Mudança Principal | Média | Status |
|---|---|---|---|
| v1 (pull inicial) | Prompt original sem estrutura | ~0.48 | ✗ Reprovado |
| v9 (primeiras otimizações) | Role Prompting + CoT básico + 3 exemplos | 0.87 | ✗ Reprovado |
| v10 (versão final) | Detecção de complexidade + template expandido + exemplo complexo | **0.91** | ✓ **Aprovado** |

### Links LangSmith

- **Dashboard do projeto:** https://smith.langchain.com/o/c3f66322-148a-420c-b6ad-6e1031b53cb5/datasets/c5d85199-cd99-4124-a60b-3960d798952a
- **Experimento final aprovado:** https://smith.langchain.com/o/c3f66322-148a-420c-b6ad-6e1031b53cb5/datasets/c5d85199-cd99-4124-a60b-3960d798952a/compare?selectedSessions=522f455e-af9c-4f37-b44a-963a49549eda
- **Prompt publicado no Hub:** https://smith.langchain.com/prompts/bug_to_user_story_v2

---

## Como Executar

### Pré-requisitos

- Python 3.9+
- Conta no [LangSmith](https://smith.langchain.com) com API Key
- API Key do Google Gemini (gratuito) ou OpenAI

### 1. Configurar variáveis de ambiente

Copie o arquivo de exemplo e preencha as credenciais:

```bash
cp .env.example .env
```

Edite o `.env`:

```env
LANGSMITH_API_KEY=lsv2_...
LANGCHAIN_PROJECT=prompt-optimization-challenge-resolved
USERNAME_LANGSMITH_HUB=seu_usuario_langsmith

# Escolha um provider:
LLM_PROVIDER=google               # ou "openai"
LLM_MODEL=gemini-2.5-flash        # ou "gpt-4o-mini"
EVAL_MODEL=gemini-2.5-flash       # ou "gpt-4o"

# Chave do provider escolhido:
GOOGLE_API_KEY=AIza...            # se usar Google
# OPENAI_API_KEY=sk-...           # se usar OpenAI
```

### 2. Instalar dependências

```bash
python3 -m venv src/venv
source src/venv/bin/activate      # Windows: src\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Fazer push do prompt otimizado para o LangSmith

```bash
python src/push_prompts.py
```

### 4. Executar a avaliação

```bash
python src/evaluate.py
```

Saída esperada:

```
Prompt: bug_to_user_story_v2
- Helpfulness: 0.91 ✓
- Correctness: 0.91 ✓
- F1-Score:    0.93 ✓
- Clarity:     0.92 ✓
- Precision:   0.89 ✓

MÉDIA GERAL: 0.9100
STATUS: APROVADO (média >= 0.9)
```

### 5. Rodar os testes de validação do prompt

```bash
source src/venv/bin/activate
python -m pytest tests/test_prompts.py -v
```

Todos os 6 testes devem passar:

```
tests/test_prompts.py::TestPrompts::test_prompt_has_system_prompt      PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_role_definition    PASSED
tests/test_prompts.py::TestPrompts::test_prompt_mentions_format        PASSED
tests/test_prompts.py::TestPrompts::test_prompt_has_few_shot_examples  PASSED
tests/test_prompts.py::TestPrompts::test_prompt_no_todos               PASSED
tests/test_prompts.py::TestPrompts::test_minimum_techniques            PASSED
6 passed in 0.03s
```

---

## Estrutura do Projeto

```
mba-ia-pull-evaluation-prompt/
├── .env.example                        # Template das variáveis de ambiente
├── requirements.txt                    # Dependências Python
├── README.md                           # Esta documentação
│
├── prompts/
│   └── bug_to_user_story_v2.yml        # Prompt otimizado (v10)
│
├── datasets/
│   └── bug_to_user_story.jsonl         # 15 exemplos de bugs (5 simples, 7 médios, 3 complexos)
│
├── src/
│   ├── push_prompts.py                 # Push ao LangSmith Hub
│   ├── evaluate.py                     # Avaliação automática via LangSmith
│   ├── metrics.py                      # Métricas customizadas (F1, Clarity, Precision)
│   └── utils.py                        # Funções auxiliares
│
└── tests/
    └── test_prompts.py                 # 6 testes de validação do prompt
```
