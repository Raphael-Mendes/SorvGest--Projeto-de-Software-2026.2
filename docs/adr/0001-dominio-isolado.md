# ADR 0001 — Domínio isolado do banco e do Flask

- **Status:** aceito
- **Data:** 17/11/2026
- **Autor:** Raphael Mendes Miranda Fernandes
- **Commits relacionados:** `5872095` (ORM e repositórios), `6d51c28` (camada de
  serviço), `38a6ffc` (API Flask)

## Contexto

O SorvGest precisa persistir sabores, pedidos, clientes e contas de fidelidade em
banco relacional (SQLAlchemy é obrigatório na disciplina) e expô-los por uma API
Flask. As regras de negócio mais importantes (não vender além do estoque, não
deixar o saldo de pontos negativo) já estavam implementadas e testadas no domínio
desde a Fase 1, em `domain/model.py`, como classes Python puras.

A dúvida era como acrescentar persistência e API sem perder duas propriedades que
o domínio já tinha: ser testável sem banco e não depender de nenhum framework.

## Decisão

Manter o domínio como Python puro e organizar o sistema em camadas:

- `adapters/orm.py` liga tabelas às classes do domínio com **mapeamento
  imperativo** (`registry.map_imperatively`), de fora para dentro. O domínio não
  importa SQLAlchemy.
- `adapters/repository.py` define **um repositório por agregado**, com uma
  interface abstrata, uma implementação SQLAlchemy e uma fake em memória para os
  testes.
- `service_layer/services.py` concentra os **casos de uso**. Cada função recebe os
  repositórios e a `session` como parâmetros, chama o domínio e faz `commit`.
- `entrypoints/flask_app.py` apenas traduz HTTP em chamadas de serviço e exceções
  em códigos 400 e 404.

## Alternativas consideradas

1. **Active Record (Flask-SQLAlchemy).** As classes herdariam de `db.Model` e as
   rotas chamariam os modelos diretamente. Seria a solução mais curta, mas obrigaria
   a reescrever as classes do domínio e faria quase todo teste depender de banco e
   de contexto Flask.
2. **Mapeamento declarativo dentro do domínio.** Manter as regras nas classes, mas
   fazê-las herdar de `DeclarativeBase`. Menos código que o mapeamento imperativo,
   porém o domínio passaria a importar SQLAlchemy, quebrando o isolamento.
3. **Transaction Script.** Colocar a lógica em funções que manipulam dados direto
   no banco. Descartado porque as invariantes já estavam bem protegidas nos
   agregados e se espalhariam pelas funções.

## Consequências

**Positivas**

- O domínio continua sem dependências externas: o commit `5872095` adicionou toda a
  persistência alterando apenas 3 linhas do diff em `domain/model.py`.
- A suíte unitária (48 testes, inclusive os 11 de serviço) roda em 0,10 s, sem
  banco, usando os repositórios fake.
- Os testes da Fase 1 continuaram passando sem nenhuma alteração.

**Negativas**

- Mais código de infraestrutura: 223 linhas em `orm.py` e `repository.py`, com 3
  classes de repositório por agregado.
- O mapeamento fica separado das classes, e atributos privados (`_saldo`,
  `_itens`) precisam ser mapeados pelo nome; erros desse tipo só aparecem nos
  testes de integração.
- Sem Unit of Work, a atomicidade depende de cada serviço usar uma única `session`
  e chamar `commit` no final.

## Riscos e evolução

- Se o número de agregados ou de casos de uso crescer, a disciplina de "uma
  `session` e um `commit` por serviço" tende a falhar; nesse caso, introduzir uma
  Unit of Work seria o próximo passo.
- O `Pedido` ainda altera o estoque do `Sabor` diretamente (risco R1 em
  `arquitetura.md`). A refatoração SOLID do checkpoint 2 deve separar o estoque,
  sem mudar esta decisão.
- Se o repositório abstrato continuar com uma única implementação real, ele pode
  ser simplificado, como sugerido na conclusão de `arquitetura.md`.