## Testes webhooks

### Sequências de Teste Implementadas
- [x] Venda realizada -> Cancelamento de assinatura
- [x] Venda Realizada -> Assinatura atrasada
- [x] Métrica de Abandono de Carrinho
- [x] Eventos especiais (card_exchanged, claimed)
- [x] Eventos de pagamento (PIX, boleto)

### Sequências de Teste Pendentes
- [x] Cartão Atualizado - card_exchanged
- [x] Pix Criado - Pix expirado
- [x] Boleto Criado - Boleto Expirado
- [x] Métrica "Claimed" - Venda reclamada diretamente com a ticto para receber reembolso
- [x] Sequencia: Assinatura Cancelada -> uncanceled [Assinatura Retomada]

### Status Documentados para Teste

#### Guru
**Status de Transações:**
- approved
- waiting_payment
- canceled
- abandoned
- refunded
- paid

**Status de Assinaturas:**
- active
- canceled
- expired
- inactive
- pastdue
- started
- trial
- trial canceled

**Métodos de Pagamento:**
- credit_card
- pix
- paypal
- applepay
- google_pay
- samsung_pay
- billet
- bank_transfer
- cryptocurrency
- efecty
- free
- ideal
- mbway
- multibanco
- multicaja
- nupay
- other
- oxxo
- pagoefectivo
- personal_credit
- safetypay
- sencillito
- servipag
- sepa
- spei
- wallet
- webpay

#### Ticto
**Status de Transações:**
- authorized
- refused
- waiting_payment
- pix_created
- pix_expired
- bank_slip_created
- bank_slip_delayed
- subscription_canceled
- subscription_delayed
- refunded
- chargeback
- claimed
- card_exchanged
- abandoned_cart

**Métodos de Pagamento:**
- credit_card
- pix
- bank_slip

### Casos de Teste Específicos

#### Guru
1. **Order Bump:** Testar `is_order_bump: 1`
2. **Cancelamento de Assinatura:** Testar `cancel_at_cycle_end: 1` e `cancel_reason`
3. **Webhook de Assinatura:** Testar `webhook_type: "subscription"`

#### Ticto
1. **Carrinho Abandonado:** Testar `status: "abandoned_cart"` ✅ **IMPLEMENTADO**
2. **Cartão Atualizado:** Testar `status: "card_exchanged"` ✅ **IMPLEMENTADO**
3. **Reclamado:** Testar `status: "claimed"` ✅ **IMPLEMENTADO**
4. **PIX:** Testar ciclo `pix_created` -> `pix_expired` ou `authorized` ✅ **IMPLEMENTADO**
5. **Boleto:** Testar ciclo `bank_slip_created` -> `bank_slip_delayed` ou `authorized` ✅ **IMPLEMENTADO**

### Estruturas de Webhook Suportadas

#### Ticto - Webhooks Normais (Vendas/Assinaturas)
```json
{
  "status": "authorized",
  "order": { "transaction_hash": "...", "paid_amount": 3990 },
  "customer": { "name": "...", "email": "..." },
  "subscriptions": [{ "id": 123, "next_charge": "..." }],
  "item": { "product_name": "...", "offer_code": "..." }
}
```

#### Ticto - Carrinho Abandonado
```json
{
  "status": "abandoned_cart",
  "name": "Nome Cliente",
  "email": "cliente@email.com",
  "product_name": "Produto",
  "created_at": "28/06/2025 01:38:52"
}
```

#### Ticto - Eventos Especiais
```json
{
  "status": "card_exchanged",
  "transaction": { "hash": "..." },
  "customer": { "email": "..." },
  "payment_method": "credit_card"
}
```

#### Ticto - Eventos de Pagamento
```json
{
  "status": "pix_created",
  "order": { "transaction_hash": "...", "paid_amount": 3990 },
  "customer": { "name": "...", "email": "..." },
  "payment_method": "pix"
}
```

### Mapeamento de Status para Testes
- Guru "approved" = Ticto "authorized"
- Guru "waiting_payment" = Ticto "waiting_payment"
- Guru "canceled" = Ticto "subscription_canceled"
- Guru "refunded" = Ticto "refunded"
- Guru "chargeback" = Ticto "chargeback"

### Validações Implementadas

#### Ticto - Validação por Tipo de Evento
- **Todos os webhooks:** Campo `status` obrigatório
- **abandoned_cart:** `email`, `name`, `product_name` obrigatórios
- **card_exchanged/claimed:** `order` ou `transaction` obrigatório
- **Webhooks normais:** `order`, `customer` obrigatórios
- **Webhooks normais:** `subscriptions` obrigatório (exceto para refused, pix_expired, bank_slip_delayed)

### Processamento Específico por Evento

#### Carrinho Abandonado
- ✅ Cria cliente se não existir
- ✅ Registra transação com valor 0
- ✅ Não cria assinatura
- ✅ ID único: `abandoned_{email}_{created_at}`

#### Eventos Especiais (card_exchanged, claimed)
- ✅ Busca cliente existente
- ✅ Registra transação com valor 0
- ✅ Não cria assinatura

#### Eventos de Pagamento (PIX, boleto)
- ✅ Atualiza transação existente se encontrada
- ✅ Cria nova transação se não existir
- ✅ Mantém cliente e assinatura existentes