# Retrospectiva

**Depois de conviver com essa arquitetura, refatorar e aplicar padrões, eu a
escolheria de novo?** Sim, mas simplificada: manteria o domínio isolado e a camada
de serviço, e enxugaria os repositórios. A seguir, o que se confirmou, o que pesou
na prática e a decisão final.

## 1. As previsões do checkpoint 1 se confirmaram?

| Previsão em `arquitetura.md` | O que aconteceu na Fase 2 |
|---|---|
| **QA1 (integridade):** violações de estoque e de saldo são sempre rejeitadas | **Confirmada e reforçada.** As invariantes continuaram nos agregados durante as duas mudanças: a `BaixaNoSabor` manteve a regra "tudo ou nada" (`test_baixa_no_sabor_e_tudo_ou_nada`), e o padrão State passou a garantir que pedidos finalizados ou cancelados recusem qualquer operação (`test_estados_encerrados_bloqueiam_todas_as_operacoes`). |
| **QA2 (testabilidade):** domínio e serviços testáveis sem banco | **Confirmada.** A suíte foi de 56 para 68 testes e a parte unitária continuou rodando em frações de segundo. Os testes de cada refatoração foram escritos e rodados sem banco. |
| **QA3 (modificabilidade):** mudanças ficam restritas a uma camada | **Confirmada.** A refatoração SOLID (`4d71bfb`) e o padrão State (`0ab6418`) alteraram só `domain/model.py` e acrescentaram testes; nenhum commit dos checkpoints 2 e 3 tocou `adapters/`, `service_layer/` ou `entrypoints/`. Pelo histórico, os únicos commits em `adapters/` são `bc085d4` e `5872095`, ambos do checkpoint 1. |
| **TP1:** o repositório abstrato custa caro para o que entrega | **Confirmada.** Nas refatorações e no padrão, as 12 classes de `repository.py` não foram usadas nem alteradas. A abstração só serviu aos testes de serviço, e para isso um fake simples bastaria. |
| **TP2:** o mapeamento imperativo tem armadilhas | **Confirmada, e pesou mais do que eu previa.** O SQLAlchemy reconstrói o `Pedido` sem chamar o `__init__`, então o padrão State teve de derivar o estado do `status` gravado em vez de guardar o objeto de estado (`gof.md`, seção 4). |
| **R1:** o `Pedido` altera o estoque de outro agregado | **Parcialmente mitigado.** A refatoração SOLID tirou a regra de dentro do `Pedido` (`BaixaDeEstoque`), mas o estoque continua no `Sabor` e o risco de concorrência continua. |
| **R2:** a atomicidade depende de disciplina | **Não testado.** Nenhum caso de uso novo foi criado na Fase 2, então o risco continua igual. |

## 2. As camadas ajudaram ou atrapalharam?

**Ajudaram nas refatorações.** As duas mudanças da Fase 2 aconteceram dentro do
domínio, e as camadas de fora não perceberam: `services.finalizar_pedido` continuou
chamando `pedido.finalizar()` como antes, e os testes de serviço, integração e e2e
passaram sem alteração. Os 26 testes da Fase 1 (`test_model.py`) também não foram
tocados em nenhum commit da Fase 2 (o último commit no arquivo é o `de51790`, de
29/09), e funcionaram como rede de segurança: se uma refatoração mudasse o
comportamento, eles quebrariam.

**Atrapalharam em dois pontos:**

- **O ORM limitou o desenho do padrão.** Com Active Record, eu também teria essa
  limitação; mas, com o mapeamento separado, ela ficou escondida em `orm.py` e só
  apareceu quando o padrão já estava sendo desenhado.
- **O custo inicial foi alto para o tamanho do sistema.** Construir ORM,
  repositórios, serviços e API levou a maior parte do tempo da Fase 2, mais do que
  a refatoração e o padrão juntos. Num sistema de uma loja, com quatro agregados,
  boa parte desse código existe para sustentar a arquitetura, e não o negócio.

## 3. Decisão final: híbrida

Eu manteria a arquitetura em camadas, com três ajustes:

1. **Manter** o domínio em Python puro, o mapeamento imperativo e a camada de
   serviço. Foram eles que permitiram refatorar e aplicar o padrão sem tocar no
   resto do sistema, que é o que eu mais valorizei na Fase 2.
2. **Simplificar** os repositórios: em vez de três classes por agregado, uma
   implementação SQLAlchemy e fakes simples só onde os testes de serviço precisam.
   Foi a parte de menor retorno, como a conclusão do `arquitetura.md` já previa.
3. **Adiar** a Unit of Work própria: a `Session` do SQLAlchemy já cumpre esse papel
   (ver `frameworks.md`). Só valeria a pena se o número de agregados crescesse a
   ponto de o risco R2 virar problema real.

Não trocaria pelo Active Record. Ele seria mais rápido de montar, mas as duas
mudanças da Fase 2 teriam sido mais arriscadas sem testes rápidos e sem a separação
entre regra e persistência.

## 4. O que eu faria diferente

- **Separar o estoque em um agregado próprio desde o início.** A `PROPOSTA.md` já
  previa o `LoteInsumo`, mas o estoque ficou dentro do `Sabor`. Isso gerou o risco
  R1 e obrigou a refatoração SOLID a contornar o problema em vez de resolvê-lo.
- **Construir a infraestrutura mínima junto com o domínio.** Com o repositório real
  e a API desde o começo, as armadilhas do mapeamento imperativo (como o objeto ser
  criado sem o `__init__`) teriam aparecido antes de desenhar o padrão State.