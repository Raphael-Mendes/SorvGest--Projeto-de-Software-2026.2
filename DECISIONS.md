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

## Checkpoint 2 — Refatoração SOLID

### Raphael Mendes Miranda Fernandes (@Raphael-Mendes) — todos os agregados

**O que eu fiz**

- Identifiquei no `Pedido.finalizar` (código do commit `de51790`, de 29/09) uma
  violação de SRP, DIP e OCP: o pedido conferia e baixava o estoque lendo
  diretamente um atributo do `Sabor`.
- Extraí a regra para a abstração `BaixaDeEstoque`, com a implementação padrão
  `BaixaNoSabor`, e criei `Sabor.tem_estoque_para`.
- Escrevi 4 testes novos para a refatoração.
- Escrevi o `docs/solid.md`.

**Arquivos:** `src/sorvgest/domain/model.py`, `tests/unit/test_baixa_estoque.py`,
`docs/solid.md`, `DECISIONS.md`

**Commits**

- `4d71bfb` — 17/11 — refatoração da baixa de estoque
- `32e791c` — 17/11 — docs/solid.md

**Decisão: manter `finalizar()` sem argumentos, com a BaixaNoSabor como padrão**

2026-11-17

O `finalizar` passou a aceitar uma `BaixaDeEstoque` por parâmetro, mas usa a
`BaixaNoSabor` quando nenhuma é passada. Considerei tornar o parâmetro obrigatório,
o que deixaria o DIP completo, mas isso obrigaria a alterar os testes da Fase 1 e a
camada de serviço. Mantendo o padrão, os 26 testes da Fase 1 continuaram passando
sem nenhuma alteração, que era a garantia de que o comportamento não mudou. O custo
é o `Pedido` ainda conhecer uma implementação concreta, registrado no `solid.md`.

**Uso de IA**

Usei o Claude (Anthropic), no modo Cowork, neste checkpoint. Após eu identificar o rompimento dos principios SOLID, pedi para A IA gerar a primeira versão do
código com o problema corrigido e dos testes novos. Além disso, pedi pra ia estruturar a segunda parte do DECISIONS.md e do SOLID.md, com as informações que detectei e passei.
Por fim, pedi para ela revisar todo o conteudo entre todo os commits, para garantir que estava tudo feito e sem erros. como na primeira parte, a responsabilidade pelo conteúdo é minha.

## Checkpoint 3 — Padrão GoF

### Raphael Mendes Miranda Fernandes (@Raphael-Mendes) — todos os agregados

**O que eu fiz**

- Apliquei o padrão **State** ao ciclo de vida do `Pedido`: os três `if` sobre o
  status foram substituídos pelas classes `EstadoPedido`, `PedidoAberto`,
  `PedidoFinalizado` e `PedidoCancelado`.
- Mantive a `BaixaDeEstoque` da refatoração SOLID, que agora é usada pelo
  `PedidoAberto` ao finalizar.
- Escrevi 8 testes para o padrão, sem alterar os testes anteriores.
- Escrevi o `docs/gof.md`, com o diagrama de classes em Mermaid.

**Arquivos:** `src/sorvgest/domain/model.py`, `tests/unit/test_estado_pedido.py`,
`docs/gof.md`, `DECISIONS.md`

**Commits**

- `0ab6418` — 17/11 — padrão State no ciclo de vida do Pedido
- `e29b4f4` — 17/11 — docs/gof.md

**Decisão: o estado é derivado do status gravado, não guardado como objeto**

2026-11-17

O `Pedido` continua guardando o `status` como texto, e o estado é obtido dele pelo
dicionário `_ESTADOS`. Considerei guardar o objeto de estado direto no pedido, mas
isso obrigaria a mudar o mapeamento em `orm.py` e a reconstruir o estado ao
carregar do banco. Derivando do texto, o padrão não exigiu nenhuma mudança na
persistência, e os testes de integração e e2e passaram sem alteração.

**Uso de IA**

Usei o Claude (Anthropic), no modo Cowork, neste checkpoint. Inicialmente, estava em dúvida entre a implementação do Strategy e o State, que foi tirada com a ajuda da IA, me fazendo optar pelo state na implementação do pedido. pedi para a IA gerar a primeira versão do código do padrão (as classes de estado e as mudanças no `Pedido`), dos
testes e a estrutura do `docs/gof.md`. Como nas fases anteriores, a responsabilidade pelo
conteúdo é minha.

## Entrega final — Frameworks e retrospectiva

### Raphael Mendes Miranda Fernandes (@Raphael-Mendes) — todos os agregados

**O que eu fiz**

- Escrevi o `docs/frameworks.md`: o papel do Flask, do SQLAlchemy e do pytest, três
  pontos de inversão de controle, cinco padrões usados pelos frameworks localizados
  no código e a comparação com o Django.
- Escrevi o `docs/retrospectiva.md`, revisitando os atributos, trade-offs e riscos
  do checkpoint 1 com evidências do histórico da Fase 2.
- Completei este `DECISIONS.md` com a reflexão final.

**Arquivos:** `docs/frameworks.md`, `docs/retrospectiva.md`, `DECISIONS.md`

**Commits**

- `897a427` — 17/11 — docs/frameworks.md
- `9dbe8b6` — 17/11 — docs/retrospectiva.md

**Decisão: arquitetura híbrida, simplificando os repositórios**

2026-11-17

Na retrospectiva, decidi manter o domínio isolado e a camada de serviço, mas
simplificar os repositórios. Considerei trocar pelo Active Record, que seria mais
simples, mas as duas mudanças da Fase 2 só ficaram restritas ao domínio graças à
separação entre regra e persistência. Já as 12 classes de `repository.py` não foram
usadas nem alteradas em nenhuma refatoração, e por isso são a parte que eu enxugaria.

**Uso de IA**

Usei o Claude (Anthropic), no modo Cowork, nesta entrega. A IA estruturou a base do que mandei para a criação da primeira versão do `docs/frameworks.md` e do `docs/retrospectiva.md`, revisei e fiz as alterações necessárias. A
responsabilidade pelo conteúdo é minha.

**Reflexão**

A principal lição da Fase 2 foi aprender os padrões de projeto que podem ser
aplicados. Antes, o importante era apenas gerar código e me certificar de que ele
estivesse funcionando. Ao utilizar os padrões arquiteturais e de projeto e aplicar
os princípios SOLID, ficou perceptível na prática o impacto, principalmente na
legibilidade e na expansão do código. Na Fase 1, houve um momento em que foi
necessário expandir as funcionalidades, e tive uma dificuldade bem maior do que
agora na Fase 2, quando existia de fato um padrão a ser seguido, principalmente
porque eu já sabia onde cada coisa deveria estar e como expandir. Um exemplo foi o
padrão State: ele mudou só o `model.py`, e todos os testes anteriores continuaram
passando sem alteração. O que eu faria diferente, com certeza, é aplicar esses
padrões de arquitetura desde o início, o que me ajudaria bastante ao longo do
desenvolvimento. Em relação à Fase 1, também planejaria melhor os casos de uso
desde o princípio, pois no início da Fase 2 tive que rever grande parte desse
aspecto.