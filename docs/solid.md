# Refatoração SOLID

## 1. Princípios violados

O método `Pedido.finalizar` violava três princípios ao mesmo tempo:

- **SRP (Responsabilidade Única):** o `Pedido` cuidava do próprio ciclo de vida
  (aberto → finalizado) **e** da regra de estoque (conferir e baixar a quantidade
  de cada sabor).
- **DIP (Inversão de Dependência):** o `Pedido` dependia de um detalhe concreto de
  outro agregado, o atributo `quantidade_estoque` do `Sabor`, em vez de uma
  abstração.
- **OCP (Aberto/Fechado):** qualquer regra nova de baixa de estoque obrigava a
  modificar o `Pedido`.

## 2. Código "antes"

Commit `de51790` (29/09/2026), `src/sorvgest/domain/model.py`:

```python
def finalizar(self):
    if self.status != StatusPedido.ABERTO:
        raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido que não está aberto.")
    if not self.itens:
        raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido sem itens.")

    for item in self.itens:
        if item.quantidade > item.sabor.quantidade_estoque:
            raise EstoqueInsuficiente(f"Estoque insuficiente para o sabor {item.sabor.nome}.")

    for item in self.itens:
        item.sabor.baixar_estoque(item.quantidade)

    self.status = StatusPedido.FINALIZADO
```

## 3. O problema concreto

As duas responsabilidades mudam por motivos diferentes. O ciclo de vida do pedido
muda quando surge um status novo; a regra de estoque muda quando a forma de
controlar o estoque muda. Três mudanças de requisito plausíveis para uma sorveteria
mostram o problema:

1. **Encomendas:** potes de 1 kg feitos sob encomenda não devem baixar o estoque na
   finalização, e sim quando forem produzidos.
2. **Lotes com validade:** a `PROPOSTA.md` prevê o `LoteInsumo`; com ele, a baixa
   teria de escolher o lote que vence primeiro e recusar lotes vencidos.
3. **Estoque compartilhado:** dois sabores feitos da mesma base (por exemplo,
   chocolate e chocolate com menta) consomem o mesmo insumo.

Antes da refatoração, qualquer uma delas exigiria editar o `Pedido.finalizar`,
um método que deveria tratar apenas do pedido. Além disso, o `Pedido` lia
diretamente um atributo interno do `Sabor`, acoplando os dois agregados (risco R1
de `docs/arquitetura.md`).

## 4. A refatoração

Commit `4d71bfb` (autor: Raphael Mendes Miranda Fernandes). O commit altera apenas
`src/sorvgest/domain/model.py` e adiciona `tests/unit/test_baixa_estoque.py`;
`tests/unit/test_model.py` não foi tocado.

A regra de estoque saiu do `Pedido` e foi para uma abstração própria:

- `BaixaDeEstoque` (classe abstrata): define o método `baixar(itens)`. É a
  abstração da qual o `Pedido` passa a depender.
- `BaixaNoSabor`: a implementação padrão. Faz exatamente o que o código antigo
  fazia: confere o estoque de todos os itens e só então baixa (tudo ou nada).
- `Sabor.tem_estoque_para(quantidade)`: o `Sabor` responde se tem estoque, em vez
  de expor o atributo para o `Pedido` comparar.

```python
def finalizar(self, baixa_de_estoque=None):
    if self.status != StatusPedido.ABERTO:
        raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido que não está aberto.")
    if not self.itens:
        raise PedidoNaoPodeSerFinalizado("Não é possível finalizar um pedido sem itens.")

    baixa = baixa_de_estoque or BaixaNoSabor()
    baixa.baixar(self.itens)

    self.status = StatusPedido.FINALIZADO
```

Agora cada princípio é atendido:

- **SRP:** o `Pedido` só decide se pode ser finalizado e muda o próprio status.
- **DIP:** o `Pedido` depende da abstração `BaixaDeEstoque`, recebida por parâmetro.
- **OCP:** uma regra nova (encomenda, lotes) é uma nova subclasse de
  `BaixaDeEstoque`, sem alterar o `Pedido`.

## 5. Como os testes garantiram o comportamento

- **Os 26 testes da Fase 1 (`tests/unit/test_model.py`) não foram alterados** e
  continuam passando. Entre eles, `test_finalizar_pedido_debita_estoque`,
  `test_finalizar_pedido_com_estoque_insuficiente` e
  `test_estoque_nao_muda_se_um_item_falhar` cobrem exatamente o comportamento que
  foi movido.
- Os testes de serviço, de integração e e2e também passaram sem alteração, porque
  `services.finalizar_pedido` continua chamando `pedido.finalizar()` sem argumentos.
- Foram adicionados 4 testes em `tests/unit/test_baixa_estoque.py`: o `Pedido`
  delega a baixa à política recebida; uma falha na baixa mantém o pedido aberto;
  a `BaixaNoSabor` é tudo ou nada; e o `Sabor` informa se tem estoque.
- Resultado: a suíte completa passou de 56 para 60 testes, todos verdes.

## 6. Custo da refatoração

- **Mais código e indireção:** duas classes novas e um método, com 28 linhas
  adicionadas e 7 removidas em `model.py` (saldo de 21 linhas), além de 73 linhas
  de testes novos. Para entender a finalização, agora é preciso olhar também a
  `BaixaNoSabor`.
- **DIP parcial:** para manter a assinatura da Fase 1 (`pedido.finalizar()` sem
  argumentos), o `Pedido` ainda cria a `BaixaNoSabor` como padrão; ele continua
  conhecendo uma implementação concreta.
- **Não resolve tudo:** o estoque ainda vive dentro do `Sabor`, e o risco de
  concorrência (R1) continua. A refatoração isola a regra, mas não cria um agregado
  de estoque separado.

**Por que compensa:** o custo é pequeno e localizado, e as três mudanças de
requisito da seção 3 deixam de exigir mexer no `Pedido`. A regra de estoque também
passou a ser testável isoladamente, com dublês simples como a `BaixaQueRegistra`.