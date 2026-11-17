# SorvGest — Sistema de Gestão de Sorveteria

Sistema para gerenciar pedidos, estoque de sabores/insumos e programa de fidelidade de uma sorveteria.

**Disciplina:** Projeto de Software  
**Instituição:** Universidade Federal Fluminense (UFF)  
**Aluno:** Raphael Mendes Miranda Fernandes

---

## Quem faz o quê

| Integrante | GitHub | Módulo |
|---|---|---|
| Raphael Mendes Miranda Fernandes | @raphael-mendes | Todos os agregados (Pedido, Sabor, ContaFidelidade) — trabalho individual |

---

## Stack

- Python 3
- pytest
- Flask
- SQLAlchemy

---

## Como executar

```bash
pip install -r requirements.txt
python -m pytest -v
```

Para subir a API (no PowerShell):

```powershell
$env:PYTHONPATH="src"
flask --app "sorvgest.entrypoints.flask_app:create_app" run
```

---

## Estrutura atual

```
src/sorvgest/
├── domain/model.py              # Entidades, objetos de valor e agregados
├── adapters/
│   ├── orm.py                   # Mapeamento imperativo SQLAlchemy
│   └── repository.py            # Repositórios: abstrato, testes e SQLAlchemy
├── service_layer/services.py    # Casos de uso
└── entrypoints/flask_app.py     # Flask

tests/
├── conftest.py                  # Fixtures: SQLite em memória e mapeamento
├── unit/                        # Domínio e serviços (com repositórios fake)
├── integration/                 # Repositórios reais
└── e2e/                         # API Flask

docs/
├── arquitetura.md               # Arquitetura e trade-offs (checkpoint 1)
├── adr/                         # Architecture Decision Records
├── solid.md                     # Refatoração SOLID (checkpoint 2)
├── gof.md                       # Padrão State (checkpoint 3)
├── frameworks.md                # Frameworks (entrega final)
└── retrospectiva.md             # Retrospectiva (entrega final)

DECISIONS.md                     # Autorrelato da Fase 2
PROPOSTA.md                      # Proposta do sistema
```