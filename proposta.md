# PROPOSTA.md
## Sistema
**SorvGest** — Sistema de Gestão de Sorveteria

Sistema para gerenciar pedidos, estoque de insumos/sabores e um programa de fidelidade de uma sorveteria, cobrindo desde a criação do pedido até o controle de estoque e recompensas para clientes recorrentes.

## Entidades de negócio (8)

1. **Cliente**
2. **Sabor**
3. **Pedido**
4. **ItemPedido**
5. **LoteInsumo** 
6. **Funcionário**
7. **Fornecedor**
8. **ContaFidelidade**

## Agregados previstos

### 1. `Pedido` (raiz: `Pedido`, contém `ItemPedido`)
- **Invariante:** o total do pedido deve ser sempre igual à soma dos subtotais dos itens.
- **Invariante:** um pedido não pode ser confirmado/fechado se algum item exceder a quantidade disponível do sabor correspondente em estoque.

### 2. `Estoque` (raiz: `LoteInsumo`, por sabor/insumo)
- **Invariante:** a quantidade de um lote nunca pode ficar negativa (não é possível dar baixa além do disponível).
- **Invariante:** um lote vencido não pode ser utilizado para baixa em novos pedidos.

### 3. `ContaFidelidade`
- **Invariante:** o saldo de pontos nunca pode ficar negativo.
- **Invariante:** um resgate de recompensa só é permitido se o saldo for suficiente para cobri-lo.

## Casos de uso

1. Criar pedido
2. Adicionar item a um pedido
3. Confirmar/fechar pedido (valida estoque e calcula total)
4. Cancelar pedido
5. Cadastrar sabor
6. Repor estoque (entrada de novo lote de insumo)
7. Dar baixa em estoque (saída por venda, ao confirmar pedido)
8. Acumular pontos de fidelidade (ao confirmar pedido)
9. Resgatar recompensa com pontos
10. Relatório de sabores mais vendidos (consulta que atravessa `Pedido` e `Estoque`)

## Stack

Python 3, pytest, Flask, SQLAlchemy