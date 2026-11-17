# Frameworks

O SorvGest usa três frameworks: **Flask**, **SQLAlchemy**
e **pytest**. Este documento analisa o papel de cada um, onde a aplicação cede o
controle a eles e quais padrões eles trazem para dentro do código.

## 1. Papel de cada framework

| Framework | Papel | Camada | Arquivos |
|---|---|---|---|
| Flask | Recebe as requisições HTTP, escolhe a função de cada rota e devolve JSON | Entrypoints | `entrypoints/flask_app.py` |
| SQLAlchemy | Liga as classes do domínio às tabelas e controla as transações | Adapters | `adapters/orm.py`, `adapters/repository.py` |
| pytest | Descobre e executa os testes, montando o ambiente de cada um | Testes (fora de `src/`) | `tests/conftest.py`, `tests/**` |

**Por que o domínio não depende deles.** `domain/model.py` e
`service_layer/services.py` não importam nem Flask nem SQLAlchemy; A dependência vai sempre de
fora para dentro:

- o **Flask** só aparece em `flask_app.py`, que traduz HTTP em chamadas de serviço;
- o **SQLAlchemy** liga as tabelas às classes do domínio com mapeamento imperativo
  (`start_mappers` em `orm.py`), sem que as classes herdem de nada;
- os **serviços** recebem a `session` e os repositórios como parâmetros, e por isso
  funcionam com a `FakeSession` e os repositórios fake nos testes unitários.

Essa separação é a decisão registrada no ADR 0001.

## 2. Inversão de controle

**Biblioteca × framework.** Com uma biblioteca, o nosso código decide quando
chamá-la e controla o fluxo. Com um framework, é o contrário: nós fornecemos
pedaços de código (funções, classes, configurações) e **o framework decide quando
chamá-los**. É o chamado princípio de Hollywood: "não nos chame, nós chamamos você".

O SQLAlchemy mostra os dois lados. `session.get(Sabor, referencia)` em
`repository.py` é uso de biblioteca: nós chamamos quando queremos. Já o mapeamento
em `orm.py` é uso de framework: nós só descrevemos as tabelas, e é o SQLAlchemy que
decide quando criar e preencher os objetos.

### 2.1 Registro de rotas e de tratadores de erro (Flask)

Em `flask_app.py`, as funções decoradas com `@app.post("/sabores")`,
`@app.post("/pedidos/<pedido_id>/finalizar")` etc. nunca são chamadas pelo nosso
código. Nós só as **registramos**; quando chega uma requisição, o Flask escolhe a
função pela URL, extrai os parâmetros (`pedido_id`) e a chama. O mesmo vale para
`app.register_error_handler`: registramos qual função trata cada exceção de negócio,
e o Flask a chama quando a exceção acontece, convertendo em 400 ou 404.

### 2.2 Fixtures (pytest)

Em `tests/conftest.py`, as funções `engine_em_memoria`, `session_factory` e
`session` são marcadas com `@pytest.fixture`. Nenhum teste as chama diretamente: o
teste só **declara um parâmetro com o mesmo nome** (por exemplo,
`def client(session_factory)` em `tests/e2e/test_api.py`), e o pytest monta a cadeia
de dependências, executa as fixtures na ordem certa, entrega os objetos e, ao final,
roda a limpeza (`clear_mappers` depois do `yield`). O pytest também descobre os
testes sozinho, pelo prefixo `test_`.

### 2.3 Reconstrução de objetos do banco (SQLAlchemy)

Ao carregar um `Pedido` com `session.get`, o SQLAlchemy cria o objeto **sem chamar
o `__init__`** e preenche os atributos a partir das colunas, inclusive os privados
mapeados em `orm.py` (`_itens`, `_saldo`). É por isso que o padrão State (ver
`gof.md`) deriva o estado do `status` gravado em vez de guardar o objeto de estado:
o framework controla a criação do objeto, e o nosso código precisa se adaptar a isso.

## 3. Padrões usados pelos frameworks

| Padrão | Framework | Onde aparece no nosso código | Como funciona |
|---|---|---|---|
| **Data Mapper** | SQLAlchemy | `start_mappers()` em `adapters/orm.py` | Um objeto separado (o mapper) transfere dados entre tabela e objeto, e as classes do domínio não sabem que são persistidas. É o oposto do Active Record do Django. |
| **Unit of Work** | SQLAlchemy | `session.commit()` em cada função de `services.py` | A `Session` registra tudo o que mudou nos objetos carregados (o pedido, o estoque do sabor, o saldo da conta) e grava tudo de uma vez no `commit`. Os serviços nunca escrevem SQL de `UPDATE`. |
| **Identity Map** | SQLAlchemy | `session.get(...)` nos repositórios de `repository.py` | Dentro de uma mesma `Session`, o mesmo registro do banco vira sempre o mesmo objeto. Por isso, em `finalizar_pedido`, o `Sabor` alterado pelo pedido é o mesmo que será gravado. |
| **Factory** | SQLAlchemy e Flask | `sessionmaker(bind=engine)` em `conftest.py` e em `create_app` | O `sessionmaker` é uma fábrica: cada rota chama `session_factory()` para obter uma sessão nova já configurada. O próprio `create_app` segue o padrão *application factory* do Flask, que permite criar a aplicação com outra configuração, como o banco em memória dos testes e2e. |
| **Injeção de dependência** | pytest | Parâmetros das fixtures (`client(session_factory)`) | O pytest resolve as dependências pelo nome do parâmetro e as injeta no teste, como um contêiner de injeção de dependência. |

## 4. E se fosse Django?

O Django é um framework *full-stack*: traz ORM, roteamento, painel de administração,
autenticação e migrações. Com ele, o SorvGest mudaria assim:

- **O domínio dependeria do framework.** O ORM do Django é Active Record: `Sabor` e
  `Pedido` teriam de herdar de `models.Model`. O mapeamento imperativo e o domínio
  como Python puro deixariam de existir, e o ADR 0001 seria impossível.
- **Os testes ficariam mais lentos e acoplados.** Testar uma regra do `Pedido`
  exigiria banco (o `TestCase` do Django cria um banco de testes). Os repositórios
  fake e a suíte unitária de 0,10 s perderiam o sentido.
- **Haveria menos código de infraestrutura.** `orm.py` e `repository.py` (223
  linhas) seriam substituídos pelos próprios modelos, e as migrações viriam prontas.
- **Viriam recursos que hoje estão fora do escopo**, como autenticação e um painel
  de administração para cadastrar sabores sem escrever API.
- **A estrutura seguiria a convenção do Django** (`models.py`, `views.py`, `urls.py`
  por app), e não a do Apêndice B. Uma camada de serviço até seria possível, mas
  iria contra a convenção do framework, que coloca a lógica nos modelos e nas views.

Para o SorvGest, o Django aceleraria a parte de infraestrutura, mas tiraria
justamente o que a arquitetura atual prioriza: o domínio isolado e testável
(QA1 e QA2 de `arquitetura.md`).