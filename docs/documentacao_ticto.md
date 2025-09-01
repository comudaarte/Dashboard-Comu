# Documentação Ticto - Webhooks e API

## Visão Geral

A Ticto é uma plataforma de pagamentos brasileira que oferece múltiplos métodos de pagamento e gestão de assinaturas. Esta documentação cobre os webhooks e estrutura de dados da API v2.0.

## Estrutura do Webhook

### Campos Principais

```json
{
  "version": "2.0",
  "status": "authorized",
  "status_date": "2024-02-10 19:19:17",
  "payment_method": "credit_card",
  "checkout_url": "https://checkout.ticto.app/O84ABA07F",
  "token": "AqmMaY4OjKCdxSwIk1bsGLtlOzTvlJQmZ2w3nEC6Edqn5am7uJZ88tTp1RuN2T8MD4aWVWvqFzh4M6hFKvFr1EjM4u7zvgNbwuIc",
  "commission_type": "producer",
  "marketplace_commission": 279,
  "order": {
    "id": 797057,
    "hash": "TOC8C0E11002NKR132S",
    "transaction_hash": "TPC1D86F1002MAF0JRF",
    "paid_amount": 3990,
    "installments": 1,
    "order_date": "2024-02-10 19:19:14"
  },
  "customer": {
    "name": "Julia Lazaro Barone",
    "email": "julia.lbarone@gmail.com",
    "email_confirmation": "julia.lbarone@gmail.com",
    "cpf": "13123404790",
    "cnpj": null,
    "type": "person",
    "is_foreign": false,
    "phone": {
      "ddi": "+55",
      "ddd": "21",
      "number": "982100352"
    },
    "address": {
      "street": "Avenida Brigadeiro Faria Lima",
      "street_number": "1811",
      "complement": null,
      "neighborhood": "Jardim Paulistano",
      "city": "São Paulo",
      "state": "SP",
      "zip_code": "01451001",
      "country": "Brasil",
      "reference": null,
      "is_mock": 1
    }
  },
  "item": {
    "product_name": "Comunidade da Arte",
    "product_id": 23292,
    "offer_name": "Assinatura Mensal",
    "offer_id": 32038,
    "offer_code": "O84ABA07F",
    "quantity": 1,
    "amount": 3990,
    "days_of_access": 30,
    "trial_days": 0,
    "refund_deadline": 7,
    "members_portal_id": 6004,
    "members_classroom_id": 11446,
    "coupon_id": null,
    "coupon_name": null
  },
  "subscriptions": [
    {
      "id": 121783,
      "interval": 1,
      "successful_charges": 1,
      "failed_charges": 0,
      "max_charges": null,
      "next_charge": "2024-03-10 00:00:00",
      "canceled_at": null,
      "change_card_url": "https://dash.ticto.com.br/change-card/1234?orderCode=TOC139213AA123&email=teste@ticto.com.br"
    }
  ],
  "transaction": {
    "hash": "TPC1D86F1002MAF0JRF",
    "cards": [
      {
        "first_digits": "230650",
        "holder": "JULIA LAZARO BARONE",
        "brand": "master",
        "last_digits": "6981"
      }
    ]
  },
  "producer": {
    "id": 516779,
    "name": "Comunidade da Arte",
    "email": "lucasrneves11@gmail.com",
    "phone": "5533333333333",
    "document": "49204590000163",
    "amount": 3462,
    "cms": "34.62"
  },
  "shipping": {
    "type": null,
    "method": null,
    "amount": 0,
    "delivery_days": null
  },
  "tracking": {
    "utm_source": "Não Informado",
    "utm_medium": "Não Informado",
    "utm_campaign": "Não Informado",
    "utm_content": "Não Informado",
    "utm_term": "Não Informado",
    "src": "Não Informado",
    "sck": "Não Informado",
    "manychat_user_id": "Não Informado"
  },
  "query_params": {
    "event": "InitiateCheckout",
    "code": "O84ABA07F"
  },
  "affiliates": [],
  "coproducers": []
}
```

## Status de Transações

### Status Principais
- **authorized**: Transação autorizada e aprovada
- **refused**: Transação recusada
- **waiting_payment**: Aguardando confirmação de pagamento
- **pix_created**: PIX gerado, aguardando pagamento
- **pix_expired**: PIX expirado sem pagamento
- **bank_slip_created**: Boleto gerado
- **bank_slip_delayed**: Boleto em atraso
- **subscription_canceled**: Assinatura cancelada
- **subscription_delayed**: Assinatura em atraso
- **refunded**: Transação reembolsada
- **chargeback**: Chargeback realizado
- **claimed**: Reclamado diretamente com a Ticto
- **card_exchanged**: Cartão atualizado
- **abandoned_cart**: Carrinho abandonado

### Status Específicos por Método de Pagamento

#### PIX
- **pix_created**: PIX gerado, aguardando pagamento
- **pix_expired**: PIX expirado sem pagamento
- **authorized**: PIX pago e confirmado

#### Boleto
- **bank_slip_created**: Boleto gerado
- **bank_slip_delayed**: Boleto em atraso
- **authorized**: Boleto pago e confirmado

#### Cartão de Crédito
- **authorized**: Transação aprovada
- **refused**: Transação recusada
- **card_exchanged**: Cartão atualizado

## Métodos de Pagamento

### payment_method
- **credit_card**: Cartão de crédito
- **pix**: PIX (Brasil)
- **bank_slip**: Boleto bancário

## Estrutura de Dados Detalhada

### Order
```json
{
  "id": 797057,
  "hash": "TOC8C0E11002NKR132S",
  "transaction_hash": "TPC1D86F1002MAF0JRF",
  "paid_amount": 3990,
  "installments": 1,
  "order_date": "2024-02-10 19:19:14"
}
```

**Campos:**
- `id`: ID único do pedido
- `hash`: Hash do pedido
- `transaction_hash`: Hash da transação
- `paid_amount`: Valor em centavos
- `installments`: Número de parcelas
- `order_date`: Data do pedido

### Customer
```json
{
  "name": "Julia Lazaro Barone",
  "email": "julia.lbarone@gmail.com",
  "email_confirmation": "julia.lbarone@gmail.com",
  "cpf": "13123404790",
  "cnpj": null,
  "type": "person",
  "is_foreign": false,
  "phone": {
    "ddi": "+55",
    "ddd": "21",
    "number": "982100352"
  },
  "address": {
    "street": "Avenida Brigadeiro Faria Lima",
    "street_number": "1811",
    "complement": null,
    "neighborhood": "Jardim Paulistano",
    "city": "São Paulo",
    "state": "SP",
    "zip_code": "01451001",
    "country": "Brasil",
    "reference": null,
    "is_mock": 1
  }
}
```

### Item
```json
{
  "product_name": "Comunidade da Arte",
  "product_id": 23292,
  "offer_name": "Assinatura Mensal",
  "offer_id": 32038,
  "offer_code": "O84ABA07F",
  "quantity": 1,
  "amount": 3990,
  "days_of_access": 30,
  "trial_days": 0,
  "refund_deadline": 7,
  "members_portal_id": 6004,
  "members_classroom_id": 11446,
  "coupon_id": null,
  "coupon_name": null
}
```

**Campos:**
- `product_name`: Nome do produto
- `product_id`: ID do produto
- `offer_name`: Nome da oferta
- `offer_id`: ID da oferta
- `offer_code`: Código da oferta
- `quantity`: Quantidade
- `amount`: Valor em centavos
- `days_of_access`: Dias de acesso
- `trial_days`: Dias de teste
- `refund_deadline`: Prazo para reembolso
- `members_portal_id`: ID do portal de membros
- `members_classroom_id`: ID da sala de aula
- `coupon_id`: ID do cupom
- `coupon_name`: Nome do cupom

### Subscriptions
```json
[
  {
    "id": 121783,
    "interval": 1,
    "successful_charges": 1,
    "failed_charges": 0,
    "max_charges": null,
    "next_charge": "2024-03-10 00:00:00",
    "canceled_at": null,
    "change_card_url": "https://dash.ticto.com.br/change-card/1234?orderCode=TOC139213AA123&email=teste@ticto.com.br"
  }
]
```

**Campos:**
- `id`: ID da assinatura
- `interval`: Intervalo entre cobranças (em meses)
- `successful_charges`: Cobranças bem-sucedidas
- `failed_charges`: Cobranças falhadas
- `max_charges`: Máximo de cobranças (null = ilimitado)
- `next_charge`: Próxima data de cobrança
- `canceled_at`: Data de cancelamento
- `change_card_url`: URL para alterar cartão

### Producer
```json
{
  "id": 516779,
  "name": "Comunidade da Arte",
  "email": "lucasrneves11@gmail.com",
  "phone": "5533333333333",
  "document": "49204590000163",
  "amount": 3462,
  "cms": "34.62"
}
```

**Campos:**
- `id`: ID do produtor
- `name`: Nome do produtor
- `email`: Email do produtor
- `phone`: Telefone do produtor
- `document`: Documento do produtor
- `amount`: Valor recebido em centavos
- `cms`: Valor recebido em reais (string)

## Eventos Especiais

### Carrinho Abandonado
```json
{
  "status": "abandoned_cart",
  "status_date": "2024-02-10 19:19:17",
  "checkout_url": "https://checkout.ticto.app/O84ABA07F",
  "customer": {
    "name": "Cliente",
    "email": "cliente@email.com"
  },
  "item": {
    "product_name": "Produto",
    "offer_code": "O84ABA07F"
  }
}
```

### Cartão Atualizado
```json
{
  "status": "card_exchanged",
  "transaction": {
    "hash": "TPC12D9623006AII26RVR",
    "cards": [
      {
        "first_digits": "515894",
        "holder": "Anna G C Santana",
        "brand": "master",
        "last_digits": "8156"
      }
    ]
  }
}
```

### Reclamado
```json
{
  "status": "claimed",
  "order": {
    "paid_amount": 35880
  }
}
```

## Observações Importantes

1. **Valores**: Todos os valores monetários vêm em centavos
2. **Datas**: Formato "YYYY-MM-DD HH:MM:SS"
3. **IDs**: IDs de assinatura são inteiros, IDs de transação são strings
4. **Status**: Normalizar conforme mapeamento em `docs/mapeamento_dados_universal.md`
5. **Webhook Type**: Todos os webhooks são do tipo "transaction"
6. **Version**: Atualmente usando versão "2.0"

## URLs de Referência

- **Documentação Oficial**: https://webhook.ticto.dev/docs/v2
- **Carrinho Abandonado**: https://webhook.ticto.dev/docs/abandoned_cart_v2 