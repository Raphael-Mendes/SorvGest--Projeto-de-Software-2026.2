# SorvGest — Sistema de Gestão de Sorveteria

Sistema para gerenciar pedidos, estoque de sabores/insumos e programa de fidelidade de uma sorveteria.

**Disciplina:** Projeto de Software  
**Instituição:** Universidade Federal Fluminense (UFF)  
**Aluno:** Raphael Mendes Miranda Fernandes

---

## Quem faz o quê

| Integrante | GitHub | Módulo |
|---|---|---|
| Raphael Mendes Miranda Fernandes | @raphael-mendes | Todos os agregados (Pedido, Estoque, ContaFidelidade) — trabalho individual|

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
├── unit/                        # Domínio e serviços (para testes)
├── integration/                 # Repositórios reais
└── e2e/                         # API Flask
```