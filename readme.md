# SorvGest — Sistema de Gestão de Sorveteria

Sistema para gerenciar pedidos, estoque de sabores/insumos e programa de fidelidade de uma sorveteria.

**Disciplina:** Projeto de Software  
**Instituição:** Universidade Federal Fluminense (UFF)  
**Aluno:** Raphael Mendes Miranda Fernandes

---

## Quem faz o quê

| Integrante | GitHub | Módulo |
|---|---|---|
| Raphael Mendes Miranda Fernandes | @raphael-mendes | Todo o projeto |

---

## Stack

- Python 3
- pytest

---

## Como executar

```bash
python -m pytest tests/unit/test_model.py -v
```

---

## Estrutura atual

```
src/sorvgest/
└── domain/
    └── model.py          # Entidades, objetos de valor e agregados

tests/
└── unit/
    └── test_model.py     # Testes do modelo de domínio
```