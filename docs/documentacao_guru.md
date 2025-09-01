# Documentação Guru - Webhooks e API

## Visão Geral

O Guru é uma plataforma de pagamentos internacional que oferece múltiplos métodos de pagamento e gestão de assinaturas. Esta documentação cobre os webhooks e estrutura de dados da API.

## Tipos de Webhook

### 1. Webhook de Transações (transaction)
Recebido quando há uma transação financeira (pagamento, cancelamento, reembolso, etc.).

### 2. Webhook de Assinaturas (subscription)
Recebido quando há mudança no status de uma assinatura.

## Estrutura do Webhook

### Campos Principais

```json
{
  "webhook_type": "transaction",
  "id": "9081534a-7512-4dab-9172-218c1dc1f263",
  "status": "approved",
  "api_token": "mLjcGjzKGnXme5b7gbuKMggL34Ecdt5NHGihxfWr",
  "checkout_url": "https://clkdmg.site/subscribe/9059bdb6-0ca4-4253-b405-482df6393537",
  "contact": {
    "id": "906d1e37-de6a-4f4d-8271-91ecd0d65ec6",
    "name": "Nome Contato",
    "email": "email@email.com",
    "doc": "01234567890",
    "phone_number": "1234567980",
    "phone_local_code": "55",
    "address": "Rua Terra Rica",
    "address_number": "123",
    "address_comp": "",
    "address_district": "Centro",
    "address_city": "Pinhais",
    "address_state": "PR",
    "address_country": "BR",
    "address_zip_code": "83324090",
    "company_name": "",
    "lead": {
      "first_tracking": {
        "name": "TEstes",
        "type": "form",
        "publisher": "",
        "tracked_at": "2020-02-18T15:50:11Z"
      },
      "last_tracking": {
        "name": "Teste Tracking Plano",
        "type": "lead",
        "publisher": "Adwords",
        "tracked_at": "2020-04-02T16:03:08Z"
      }
    }
  },
  "payment": {
    "total": 500,
    "net": 500,
    "gross": 500,
    "currency": "BRL",
    "method": "credit_card",
    "discount_value": 0,
    "affiliate_value": 0,
    "marketplace_value": 0,
    "can_try_again": 1,
    "refund_reason": "",
    "refuse_reason": "Transação capturada com sucesso",
    "acquirer": {
      "name": "",
      "code": "",
      "message": "",
      "nsu": "",
      "tid": ""
    },
    "credit_card": {
      "id": "card_WLmNYk1fmKUOwBwX",
      "brand": "visa",
      "first_digits": "400000",
      "last_digits": "0010"
    },
    "installments": {
      "qty": 1,
      "value": 500,
      "interest": 0
    },
    "tax": {
      "rate": 0,
      "value": 0
    },
    "processing_times": {
      "started_at": "2024-08-19T15:37:16.673Z",
      "finished_at": "2024-08-19T15:37:17.442Z",
      "delay_in_seconds": 0
    }
  },
  "product": {
    "id": "1587151083",
    "name": "Assinatura Mundipagg",
    "type": "plan",
    "unit_value": 500,
    "total_value": 500,
    "qty": 1,
    "internal_id": "906d1e37-de6a-4f4d-8271-91ecd0d65e32",
    "marketplace_id": "1587151083",
    "marketplace_name": "mundipagg",
    "image_url": "",
    "offer": {
      "id": "offer_id",
      "name": "Nome da Oferta"
    },
    "producer": {
      "name": "Produtor Mundipagg",
      "marketplace_id": "01234567890",
      "contact_email": ""
    }
  },
  "subscription": {
    "id": "sub_BOAEj2WTKoclmg4X",
    "subscription_code": "sub_7F3X50uu4VxTGenj",
    "name": "Assinatura Mundipagg",
    "last_status": "active",
    "last_status_at": "2020-05-07T11:35:57Z",
    "started_at": "2020-05-07T12:54:28Z",
    "canceled_at": null,
    "charged_every_days": 30,
    "charged_times": 1,
    "can_cancel": 1,
    "trial_days": 0,
    "trial_started_at": null,
    "trial_finished_at": null,
    "internal_id": "9ccde88d-3739-48fe-8e32-d69398b8c0e7"
  },
  "dates": {
    "created_at": "2023-09-19T09:19:04Z",
    "ordered_at": "2020-05-07T11:33:45Z",
    "confirmed_at": "2020-05-07T11:35:57Z",
    "updated_at": "2023-11-14T14:08:18Z",
    "canceled_at": null,
    "expires_at": null,
    "unavailable_until": "2020-06-06T11:35:57Z",
    "warranty_until": "2020-06-06T11:35:57Z"
  },
  "invoice": {
    "id": "in_qbaJBvDB3IzVf2PTG",
    "status": "paid",
    "type": "cycle",
    "value": 100,
    "charge_at": "2021-04-12",
    "created_at": "2021-04-12T16:33:29Z",
    "period_start": "2021-04-12",
    "period_end": "2021-04-13",
    "cycle": 1,
    "discount_value": 0,
    "increment_value": 0,
    "tax_value": 0,
    "tries": 0,
    "try": 0
  },
  "type": "producer",
  "infrastructure": {
    "ip": "127.0.0.1",
    "host": "https://clkdmg.site",
    "country": "BR",
    "region": null,
    "city": null,
    "city_lat_long": null,
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
  },
  "source": {
    "source": "",
    "checkout_source": "",
    "utm_source": "",
    "utm_medium": "",
    "utm_campaign": "",
    "utm_content": "",
    "utm_term": "",
    "pptc": []
  },
  "extras": {
    "accepted_terms_url": 1,
    "accepted_privacy_policy_url": 1
  },
  "affiliations": [
    {
      "id": "99f598ca-1d90-4afb-b306-70cc52b56f2f",
      "name": "John Doe",
      "contact_email": "john.doe@email.com",
      "affiliates_group_name": "group test",
      "marketplace_id": "YR5TFRMH",
      "currency": "BRL",
      "value": 334.39,
      "net_value": 315.07,
      "fee": 19.32
    }
  ],
  "contracts": [],
  "ecommerces": [],
  "shipment": {
    "carrier": "Correios",
    "service": "SEDEX",
    "tracking": "ME20000BGL2BR",
    "value": 105.68,
    "delivery_time": 15,
    "status": []
  },
  "shipping": {
    "name": "Standard",
    "value": 0
  },
  "items": [
    {
      "id": "1587151083",
      "name": "Assinatura Mundipagg",
      "type": "plan",
      "unit_value": 500,
      "total_value": 500,
      "qty": 1,
      "internal_id": "906d1e37-de6a-4f4d-8271-91ecd0d65e32",
      "marketplace_id": "1587151083",
      "marketplace_name": "mundipagg",
      "image_url": "",
      "offer": {
        "id": "offer_id",
        "name": "Nome da Oferta"
      },
      "producer": {
        "name": "Produtor Mundipagg",
        "marketplace_id": "01234567890",
        "contact_email": ""
      }
    }
  ],
  "last_transaction": []
}
```

## Status de Transações

### payment.method
- **applepay**: Apple Pay
- **baloto**: Baloto (Colômbia)
- **bank_transfer**: Transferência bancária
- **billet**: Boleto bancário
- **credit_card**: Cartão de crédito
- **cryptocurrency**: Criptomoeda
- **efecty**: Efecty (Colômbia)
- **free**: Gratuito
- **google_pay**: Google Pay
- **ideal**: iDEAL (Holanda)
- **mbway**: MB WAY (Portugal)
- **multibanco**: Multibanco (Portugal)
- **multicaja**: Multicaja (Chile)
- **nupay**: NuPay
- **other**: Outros métodos
- **oxxo**: OXXO (México)
- **pagoefectivo**: PagoEfectivo (Peru)
- **paypal**: PayPal
- **personal_credit**: Crédito pessoal
- **pix**: PIX (Brasil)
- **samsung_pay**: Samsung Pay
- **safetypay**: SafetyPay
- **sencillito**: Sencillito (Chile)
- **servipag**: Servipag (Chile)
- **sepa**: SEPA (Europa)
- **spei**: SPEI (México)
- **wallet**: Carteira digital
- **webpay**: WebPay (Chile)

### status (Transações)
- **approved**: Transação aprovada
- **waiting_payment**: Aguardando pagamento
- **canceled**: Transação cancelada
- **abandoned**: Transação abandonada
- **refunded**: Transação reembolsada
- **paid**: Pagamento realizado

## Status de Assinaturas

### last_status (Assinaturas)
- **active**: Assinatura ativa
- **canceled**: Assinatura cancelada
- **expired**: Assinatura expirada
- **inactive**: Assinatura inativa
- **pastdue**: Assinatura em atraso
- **started**: Assinatura iniciada
- **trial**: Período de teste
- **trial canceled**: Teste cancelado

## Estrutura de Dados Detalhada

### Contact
```json
{
  "id": "906d1e37-de6a-4f4d-8271-91ecd0d65ec6",
  "name": "Nome Contato",
  "email": "email@email.com",
  "doc": "01234567890",
  "phone_number": "1234567980",
  "phone_local_code": "55",
  "address": "Rua Terra Rica",
  "address_number": "123",
  "address_comp": "",
  "address_district": "Centro",
  "address_city": "Pinhais",
  "address_state": "PR",
  "address_country": "BR",
  "address_zip_code": "83324090",
  "company_name": ""
}
```

### Payment
```json
{
  "total": 500,
  "net": 500,
  "gross": 500,
  "currency": "BRL",
  "method": "credit_card",
  "discount_value": 0,
  "affiliate_value": 0,
  "marketplace_value": 0,
  "can_try_again": 1,
  "refund_reason": "",
  "refuse_reason": "Transação capturada com sucesso",
  "acquirer": {
    "name": "",
    "code": "",
    "message": "",
    "nsu": "",
    "tid": ""
  },
  "credit_card": {
    "id": "card_WLmNYk1fmKUOwBwX",
    "brand": "visa",
    "first_digits": "400000",
    "last_digits": "0010"
  },
  "installments": {
    "qty": 1,
    "value": 500,
    "interest": 0
  },
  "tax": {
    "rate": 0,
    "value": 0
  }
}
```

### Product
```json
{
  "id": "1587151083",
  "name": "Assinatura Mundipagg",
  "type": "plan",
  "unit_value": 500,
  "total_value": 500,
  "qty": 1,
  "internal_id": "906d1e37-de6a-4f4d-8271-91ecd0d65e32",
  "marketplace_id": "1587151083",
  "marketplace_name": "mundipagg",
  "image_url": "",
  "offer": {
    "id": "offer_id",
    "name": "Nome da Oferta"
  },
  "producer": {
    "name": "Produtor Mundipagg",
    "marketplace_id": "01234567890",
    "contact_email": ""
  }
}
```

### Subscription
```json
{
  "id": "sub_BOAEj2WTKoclmg4X",
  "subscription_code": "sub_7F3X50uu4VxTGenj",
  "name": "Assinatura Mundipagg",
  "last_status": "active",
  "last_status_at": "2020-05-07T11:35:57Z",
  "started_at": "2020-05-07T12:54:28Z",
  "canceled_at": null,
  "charged_every_days": 30,
  "charged_times": 1,
  "can_cancel": 1,
  "trial_days": 0,
  "trial_started_at": null,
  "trial_finished_at": null,
  "internal_id": "9ccde88d-3739-48fe-8e32-d69398b8c0e7"
}
```

### Dates
```json
{
  "created_at": "2023-09-19T09:19:04Z",
  "ordered_at": "2020-05-07T11:33:45Z",
  "confirmed_at": "2020-05-07T11:35:57Z",
  "updated_at": "2023-11-14T14:08:18Z",
  "canceled_at": null,
  "expires_at": null,
  "unavailable_until": "2020-06-06T11:35:57Z",
  "warranty_until": "2020-06-06T11:35:57Z"
}
```

## Webhook de Assinatura

### Estrutura Específica
```json
{
  "webhook_type": "subscription",
  "id": "sub_CKbiQnjYRGL6l5bK",
  "subscription_code": "sub_CKbiQnjYRGL6l5bK",
  "name": "Comu Academy",
  "last_status": "active",
  "cancel_at_cycle_end": 0,
  "cancel_reason": "",
  "cancelled_by": {
    "date": "",
    "email": "",
    "name": ""
  },
  "charged_every_days": 365,
  "charged_times": 1,
  "trial_days": 0,
  "trial_started_at": null,
  "trial_finished_at": null,
  "current_invoice": {
    "id": "9f292d8f-3ff5-4f74-855b-4775b86f49d8",
    "status": "waiting_payment",
    "value": 358.8,
    "charge_at": "2025-06-15",
    "created_at": 1749992068,
    "cycle": 1,
    "period_start": "2025-06-15",
    "period_end": "2026-06-15",
    "type": "cycle",
    "discount_value": 0,
    "increment_value": 0,
    "tax_value": 0,
    "tries": 0,
    "try": 0,
    "payment_url": "https://go.comudaarte.com/pay/9f292d8f-3ff5-4f74-855b-4775b86f49d8/invoice",
    "subscription_id": "9f292d8f-3dcd-4ca1-bae6-de7f33269d1a",
    "updated_at": 1749992068
  },
  "dates": {
    "started_at": "2025-06-15T12:54:28Z",
    "last_status_at": "2025-06-15T12:54:28Z",
    "canceled_at": null,
    "cycle_start_date": "2025-06-15",
    "cycle_end_date": "2026-06-15",
    "next_cycle_at": "2026-06-16"
  },
  "subscriber": {
    "id": "9f292ccc-4477-4a30-b999-38a1eba2b6b1",
    "name": "Isabela Veiga Oliveira",
    "email": "dartveiga22@gmail.com",
    "doc": "00604695101",
    "phone_local_code": "55",
    "phone_number": "62981886368",
    "address": "",
    "address_city": "",
    "address_comp": "",
    "address_country": "BR",
    "address_district": "",
    "address_number": "",
    "address_state": "",
    "address_zip_code": ""
  },
  "product": {
    "id": "9e6c7a03-acdf-45af-abc5-0e0ba41d54eb",
    "name": "Comu Academy",
    "marketplace_id": "1741887379",
    "marketplace_name": "pagarme2",
    "offer": {
      "id": "9e942d92-da6b-40b2-ba26-d58829850a5d",
      "name": "Comunidade da Arte - Anual (S/Juros)",
      "value": 358.8,
      "cash_discount": 0,
      "units_per_sale": 1,
      "plan": {
        "provider": "guru",
        "interval": 1,
        "interval_type": "year",
        "cycles": 0,
        "trial_days": 0,
        "split_cycles": 0,
        "discount": {
          "cycles": 0,
          "value": 0
        },
        "increment": {
          "cycles": 0,
          "value": 0
        }
      }
    },
    "producer": {
      "name": "Comunidade Da Arte",
      "marketplace_id": "1741781464",
      "contact_email": ""
    }
  },
  "next_product": {
    "id": "9e6c7a03-acdf-45af-abc5-0e0ba41d54eb",
    "name": "Comu Academy",
    "marketplace_id": "1741887379",
    "marketplace_name": "pagarme2",
    "offer": {
      "id": "9e942d92-da6b-40b2-ba26-d58829850a5d",
      "name": "Comunidade da Arte - Anual (S/Juros)",
      "value": 358.8,
      "cash_discount": 0,
      "units_per_sale": 1,
      "plan": {
        "provider": "guru",
        "interval": 1,
        "interval_type": "year",
        "cycles": 0,
        "trial_days": 0,
        "split_cycles": 0,
        "discount": {
          "cycles": 0,
          "value": 0
        },
        "increment": {
          "cycles": 0,
          "value": 0
        }
      }
    }
  },
  "next_cycle_value": 358.8,
  "next_cycle_installments": 12,
  "payment_method": "credit_card",
  "provider": "guru",
  "credit_card": {
    "id": "3d45c615-912e-4b2a-a57c-2aec0e0913e5",
    "bin": "230650",
    "brand": "mastercard",
    "holder_name": "Isabela V Oliveira",
    "last_four": "0049",
    "expiration_month": "12",
    "expiration_year": "2031",
    "created_at": "2025-06-15T12:54:28Z",
    "updated_at": "2025-06-15T12:54:28Z",
    "renewed": 0,
    "marketplace": {
      "pagarme2": {
        "customer": {
          "id": "cus_dm3rDZniJi3DZoA0"
        },
        "payment": {
          "id": "card_39DJa31tNMiVAGOk"
        }
      }
    }
  },
  "last_transaction": {
    "id": "9f292c82-426f-402a-9761-d9e4982b8c7d",
    "url": "https://digitalmanager.guru/admin/transactions/pagarme2/ch_nO4AWrOU9U7yq1Z9"
  }
}
```

## Eventos Especiais

### Order Bump
```json
{
  "is_order_bump": 1,
  "is_reissue": 0,
  "last_transaction": {
    "id": "9f4b9cdd-cfcf-4544-9504-baba9190d23a",
    "url": "https://digitalmanager.guru/admin/transactions/pagarme2/ch_1W4nx6Xmi2irV5ME"
  }
}
```

### Cancelamento de Assinatura
```json
{
  "cancel_at_cycle_end": 1,
  "cancel_reason": "Encontrei outra alternativa",
  "cancelled_by": {
    "date": "2025-06-17T00:49:08Z",
    "email": "dartveiga22@gmail.com",
    "name": "Isabela Veiga Oliveira"
  }
}
```

## Observações Importantes

1. **Valores**: Todos os valores monetários vêm em reais (float)
2. **Datas**: Formato ISO 8601 "YYYY-MM-DDTHH:MM:SSZ"
3. **IDs**: IDs são strings UUID
4. **Status**: Normalizar conforme mapeamento em `docs/mapeamento_dados_universal.md`
5. **Webhook Type**: "transaction" ou "subscription"
6. **Order Bump**: Identificado pelo campo `is_order_bump: 1`
7. **Cancelamento**: Identificado por `cancel_at_cycle_end: 1` ou `cancel_reason`

## URLs de Referência

- **Documentação Oficial**: https://digitalmanager.guru/docs
- **Webhook Documentation**: https://digitalmanager.guru/docs/webhooks 