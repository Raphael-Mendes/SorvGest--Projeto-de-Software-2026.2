# DECISIONS.md

A DECISIONS.md não foi entregue no prazo da Fase 1. Portanto, como houve a mudança de cronograma e de formato do trabalho, decidi realizar apenas a parte 2 em diante.

# Parte 2 — Arquitetura, Refatoração e Padrões (Fase 2)

Trabalho individual: todas as entregas são de Raphael Mendes Miranda Fernandes
(@Raphael-Mendes). Os checkpoints 1, 2 e 3 não foram entregues nos prazos
originais; o conteúdo foi produzido entre 15/11/2026 e 17/11/2026, e cada
checkpoint está marcado com sua tag anotada.

## Checkpoint 1 — Arquitetura e trade-offs

### Raphael Mendes Miranda Fernandes (@Raphael-Mendes) — todos os agregados

**O que eu fiz**

- Completei as camadas que faltavam desde a Fase 1: repositórios abstratos, fake e
  SQLAlchemy para os 4 agregados, mapeamento imperativo, camada de serviço com 8
  casos de uso e API Flask com testes de integração e e2e.
- Criei a entidade `Cliente` e o agregado `ContaFidelidade`, previstos na proposta.
- Configurei a CI no GitHub Actions.
- Escrevi o `docs/arquitetura.md` completo e o ADR 0001.

**Arquivos:** `.github/workflows/ci.yml`, `requirements.txt`, `.gitignore`,
`src/sorvgest/domain/model.py`, `src/sorvgest/adapters/orm.py`,
`src/sorvgest/adapters/repository.py`, `src/sorvgest/service_layer/services.py`,
`src/sorvgest/entrypoints/flask_app.py`, `tests/`, `docs/arquitetura.md`,
`docs/adr/0001-dominio-isolado.md`, `README.md`, `PROPOSTA.md`, `DECISIONS.md`

**Commits**

- `e7a902b` — 15/11 — CI, requirements.txt e .gitignore
- `bc085d4` — 15/11 — repositório de Sabor e testes
- `4603037` — 15/11 — Cliente e ContaFidelidade com testes
- `5872095` — 16/11 — ORM e repositórios SQLAlchemy com testes de integração
- `6d51c28` — 16/11 — camada de serviço, casos de uso e testes
- `38a6ffc` — 17/11 — API Flask, testes e2e e README
- `3f4765a` — 17/11 — arquitetura: escopo, requisitos e arquitetura atual
- `8f70423` — 17/11 — arquitetura: trade-offs, alternativa e evidências
- `e6b410f` — 17/11 — ADR 0001
- `dd28658` — 17/11 — renomeação de README.md e PROPOSTA.md

**Decisão: pontos de fidelidade creditados no serviço, não no Pedido**

2026-11-16

Os pontos são creditados por `finalizar_pedido`, na camada de serviço. Considerei
colocar essa regra dentro do `Pedido`, mas aí o agregado de pedidos passaria a
conhecer e alterar a `ContaFidelidade`, o mesmo tipo de acoplamento que já existe
entre `Pedido` e `Sabor` (risco R1). No serviço, cada agregado continua protegendo
apenas as próprias invariantes; o custo é a regra "1 ponto por real" ficar fora do
domínio (trade-off TP3 do `arquitetura.md`).

**Uso de IA**

Usei o Claude (Anthropic), no modo Cowork, com acesso de leitura à pasta do projeto:

- para analisar o enunciado e o estado do repositório e montar o cronograma de entrega;
- para gerar as versões iniciais de todo o código novo deste checkpoint (as pastas `adapters/`, `service_layer/` e `entrypoints/`, as classes `Cliente` e
`ContaFidelidade`) assim como dos testes novos. Analisei e revisei todos os códigos gerados, adicionando ou removendo informações quando necessário;
- - para estrturar os arquivos da pasta docs a partir da estrutura e das informações que eu passei. Revisei e alterei os textos e os números das evidências foram medidos por mim no repositório;
- Revisar e detectar a existência de erros e a completude das etapas antes de cada commit.

Revisei tudo o que foi commitado, e a responsabilidade pelo conteúdo é minha.