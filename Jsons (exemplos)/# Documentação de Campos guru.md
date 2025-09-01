# Documentação de Campos

| Campo                                      | Tipo               | Obrigatório | Descrição                                       |
|-------------------------------------------|--------------------|-------------|-------------------------------------------------|
| affiliations.*.affiliates_group_namecurr  | String             | Sim         | Nome do grupo da afiliação                     |
| affiliations.*.contact_email              | String             | Não         | Email da afiliação                             |
| affiliations.*.currency                   | String             | Não         | Moeda da afiliação                             |
| affiliations.*.fee                        | Float              | Não         | Taxa da afiliação                              |
| affiliations.*.id                         | String             | Não         | ID da afiliação                                |
| affiliations.*.marketplace_id             | String             | Não         | ID do marketplace da afiliação                |
| affiliations.*.name                       | String             | Não         | Nome da afiliação                              |
| affiliations.*.net_value                  | Float              | Não         | Valor líquido da comissão                      |
| affiliations.*.value                      | Float              | Não         | Valor da comissão                              |
| api_token                                 | Char(40)           | Sim         | Chave de API do Guru                           |
| checkout_url                              | String             | Não         | URL do Checkout do Guru                        |
| contact.id                                | String(191)        | Não         | ID                                             |
| contact.name                              | String(191)        | Não         | Nome                                           |
| contact.email                             | String(191)        | Não         | E-mail                                         |
| contact.doc                               | String(191)        | Não         | Documento                                      |
| contact.phone_number                      | String(191)        | Não         | Telefone                                       |
| contact.phone_local_code                  | String(191)        | Não         | Indicativo do telefone                         |
| contact.address                           | String(191)        | Não         | Endereço                                       |
| contact.address_number                    | String(191)        | Não         | Número                                         |
| contact.address_comp                      | String(191)        | Não         | Complemento                                    |
| contact.address_district                  | String(191)        | Não         | Bairro                                         |
| contact.address_city                      | String(191)        | Não         | Cidade                                         |
| contact.address_state                     | String(191)        | Não         | Estado                                         |
| contact.address_country                   | String(191)        | Não         | País                                           |
| contact.address_zip_code                  | String(191)        | Não         | Código Postal                                  |
| contact.lead.first_tracking.name          | String(191)        | Não         | Nome do primeiro rastreio do lead             |
| contact.lead.first_tracking.type          | TrackingType       | Não         | Tipo do primeiro rastreio do lead             |
| contact.lead.first_tracking.publisher     | Publisher          | Não         | Anunciante do primeiro rastreio do lead       |
| contact.lead.first_tracking.tracked_at    | YYYY-MM-DDTHH:MM:SSZ | Não       | Data do primeiro rastreio do lead             |
| contact.lead.last_tracking.name           | String(191)        | Não         | Nome do último rastreio do lead               |
| contact.lead.last_tracking.type           | TrackingType       | Não         | Tipo do último rastreio do lead               |
| contact.lead.last_tracking.publisher      | Publisher          | Não         | Anunciante do último rastreio do lead         |
| contact.lead.last_tracking.tracked_at     | YYYY-MM-DDTHH:MM:SSZ | Não       | Data do último rastreio do lead               |
| contracts                                 | Array              | Sim         | Contratos                                     |
| dates.canceled_at                         | YYYY-MM-DDTHH:MM:SSZ | Não       | Data do Cancelamento                          |
| dates.confirmed_at                        | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de Aprovação                             |
| dates.created_at                          | YYYY-MM-DDTHH:MM:SSZ | Sim       | Data de Criação                               |
| dates.expires_at                          | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de Expiração                             |
| dates.ordered_at                          | YYYY-MM-DDTHH:MM:SSZ | Sim       | Data do Pedido                                |
| dates.unavailable_until                   | YYYY-MM-DDTHH:MM:SSZ | Não       | Indisponível até                              |
| dates.updated_at                          | YYYY-MM-DDTHH:MM:SSZ | Sim       | Data de Atualização                           |
| dates.warranty_until                      | YYYY-MM-DDTHH:MM:SSZ | Não       | Garantia até                                  |
| ecommerces.kapsula.pedido                 | Integer            | Não         | Número do Pedido Kapsula                      |
| ecommerces.magento.quote_id               | Integer            | Não         | Número da Cotação Magento                     |
| ecommerces.magento.order_id               | Integer            | Não         | Número do Pedido Magento                      |
| ecommerces.shopify.order_id               | Integer            | Não         | Número do Pedido Shopify                      |
| ecommerces.shopify.transaction_id         | Integer            | Não         | Número da Transação Shopify                   |
| ecommerces.woocommerce.id                | Integer             | Não         | Número do Pedido Woocommerce                  |
| extras.accepted_terms_url                 | Integer            | Sim         | Indica que o comprador aceitou os termos      |
| extras.accepted_privacy_policy_url        | Integer            | Sim         | Indica que o comprador aceitou a política     |
| id                                        | String(191)        | Sim         | ID da Transação                               |
| infrastructure.user_agent                 | String(191)        | Não         | User Agent do comprador                       |
| infrastructure.ip                         | String(191)        | Não         | IP do comprador                               |
| infrastructure.country                    | String(191)        | Não         | País do comprador                              |
| infrastructure.region                     | String             | Não         | Região do comprador                            |
| infrastructure.city                       | String(191)        | Não         | Cidade do comprador                            |
| infrastructure.city_lat_long             | String(191)        | Não         | Coordenadas do comprador                       |
| infrastructure.city_lat_long             | String             | Não         | Host do comprador                              |
| invoice.charge_at                         | YYYY-MM-DD         | Não         | Data de pagamento                              |
| invoice.created_at                        | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de criação do invoice                     |
| invoice.cycle                             | Integer            | Não         | Número de ciclo                                |
| invoice.discount_value                    | Float              | Não         | Desconto do invoice                            |
| invoice.id                                | String(20)         | Não         | ID do invoice                                  |
| invoice.increment_value                   | Float              | Não         | Incremento do invoice                          |
| invoice.period_end                        | YYYY-MM-DD         | Não         | Fim do período                                 |
| invoice.period_start                      | YYYY-MM-DD         | Não         | Início do período                              |
| invoice.status                            | InvoiceStatus      | Não         | Status do invoice                              |
| invoice.tax_value                         | Float              | Não         | Taxa do invoice                                |
| invoice.tries                             | Integer            | Não         | Total de tentativas                            |
| invoice.try                               | Integer            | Não         | Número da tentativa                            |
| invoice.type                              | InvoiceType        | Não         | Tipo do invoice                                |
| invoice.value                             | Float              | Não         | Valor do invoice                               |
| items.*.id                                | String             | Sim         | ID do item                                     |
| items.*.image_url                         | String             | Sim         | URL da imagem                                  |
| items.*.internal_id                       | String             | Sim         | ID interno do item                             |
| items.*.marketplace_id                    | String             | Sim         | ID do marketplace                              |
| items.*.marketplace_name                  | String             | Sim         | Nome do marketplace                            |
| items.*.name                              | String             | Sim         | Nome do item                                   |
| items.*.offer.id                          | String             | Sim         | ID da oferta                                   |
| items.*.offer.name                        | String             | Sim         | Nome da oferta                                 |
| items.*.producer.contact_email            | String             | Não         | E-mail do produtor                             |
| items.*.producer.marketplace_id           | String             | Sim         | ID do marketplace do produtor                 |
| items.*.producer.name                     | String             | Sim         | Nome do produtor                               |
| items.*.qty                               | Integer            | Sim         | Quantidade                                     |
| items.*.total_value                       | Float              | Sim         | Valor total do item                            |
| items.*.type                              | String             | Sim         | Tipo do item                                   |
| items.*.unit_value                        | Float              | Sim         | Valor unitário do item                         |
| last_transaction.id                       | String(191)        | Não         | ID da transação anterior (1 Click Buy)        |
| last_transaction.url                      | String(191)        | Não         | URL da transação anterior (1 Click Buy)       |
| payment.affiliate_value                   | Float              | Sim         | Valor Afiliados                                |
| payment.acquirer.code                     | String             | Sim         | Código do adquirente                           |
| payment.acquirer.message                  | String             | Sim         | Mensagem do adquirente                        |
| payment.acquirer.name                     | String             | Sim         | Nome do adquirente                             |
| payment.acquirer.nsu                      | String             | Sim         | NSU do adquirente                              |
| payment.acquirer.tid                      | String             | Sim         | TID do adquirente                              |
| payment.can_try_again                     | Integer (0/1)      | Sim         | Indica se pode tentar novamente               |
| payment.coupon.id                         | String             | Não         | ID do cupom                                   |
| payment.coupon.coupon_code                | String             | Não         | Código do cupom                               |
| payment.coupon.incidence_type             | String             | Não         | Tipo de incidência do cupom                   |
| payment.coupon.incidence_field            | String             | Não         | Incidência do cupom                           |
| payment.coupon.incidence_value            | Float              | Não         | Valor do cupom                                |
| payment.coupon.last_sent_at               | Integer            | Não         | Unix timestamp                                |
| payment.coupon.final_value                | Float              | Não         | Valor final do cupom                          |
| payment.currency                          | String(191)        | Sim         | Moeda (ISO 4217)                              |
| payment.discount_value                    | Float              | Sim         | Desconto                                      |
| payment.gross                             | Float              | Sim         | Valor bruto                                   |
| payment.instalments.value                 | Float              | Não         | Valor das parcelas                            |
| payment.instalments.qty                   | Integer            | Não         | Quantidade de parcelas                        |
| payment.installments.interest             | Float              | Não         | Juros do parcelamento                         |
| payment.marketplace_id                    | String(191)        | Sim         | Código da Venda no Processador de Pagamento    |
| payment.marketplace_name                  | String(191)        | Sim         | Processador de Pagamento                       |
| payment.marketplace_value                 | Float              | Sim         | Valor do Processador de Pagamento              |
| payment.method                            | PaymentMethod      | Sim         | Método de Pagamento                            |
| payment.net                               | Float              | Sim         | Valor Líquido                                  |
| payment.processing_times.started_at       | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de início do processamento               |
| payment.processing_times.finished_at      | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de final do processamento                |
| payment.processing_times.delay_in_seconds | Integer            | Não         | Atraso (em segundos)                          |
| payment.refund_reason                     | String             | Não         | Razão de reembolso                            |
| payment.refuse_reason                     | String(191)        | Não         | Mensagem do processador de pagamento          |
| payment.tax.value                         | Float              | Não         | Valor da Taxa                                  |
| payment.tax.rate                          | Float              | Não         | Porcentagem da Taxa                            |
| payment.total                             | Float              | Sim         | Valor Total                                    |
| payment.billet.line                       | String(191)        | Não         | Linha Digitável do Boleto                     |
| payment.billet.url                        | String(191)        | Não         | URL do Boleto                                  |
| payment.billet.expiration_date            | String(191)        | Não         | Data de Expiração do Boleto                   |
| payment.creditcard.brand                  | String(191)        | Não         | Bandeira do cartão                             |
| payment.creditcard.expiration_month       | String             | Não         | Mês de expiração do cartão                    |
| payment.creditcard.expiration_year        | String             | Não         | Ano de expiração do cartão                    |
| payment.creditcard.first_digits           | Integer            | Não         | Bin do cartão                                  |
| payment.creditcard.id                     | String             | Não         | ID do cartão                                   |
| payment.creditcard.last_digits            | Integer            | Não         | Últimos 4 dígitos do cartão                   |
| payment.pix.qrcode.signature              | String(191)        | Não         | Código QRCode do Pix                           |
| payment.pix.qrcode.url                    | String(191)        | Não         | URL QRCode do Pix                              |
| payment.pix.expiration_date               | String(191)        | Não         | Data de Expiração do Pix                       |
| payment.spei.url                          | String(191)        | Não         | URL do pagamento SPEI                         |
| payment.spei.account                      | String(191)        | Não         | Código da Conta SPEI                           |
| payment.spei.reference                    | String(191)        | Não         | Código da Referência SPEI                      |
| payment.spei.expiration_date              | String(191)        | Não         | Data de Expiração do SPEI                      |
| payment.oxxo.url                          | String(191)        | Não         | URL do pagamento OXXO                         |
| payment.oxxo.barcode                      | String(191)        | Não         | Código de barras OXXO                          |
| payment.oxxo.expiration_date              | String(191)        | Não         | Data de Expiração do OXXO                      |
| product.id                                | String(191)        | Sim         | ID do produto                                  |
| product.image_url                         | String(191)        | Não         | Imagem do produto                              |
| product.internal_id                       | String             | Sim         | ID interno do produto                          |
| product.marketplace_id                    | String             | Sim         | ID do marketplace                              |
| product.marketplace_name                  | String(191)        | Sim         | Nome do marketplace do produto                |
| product.name                              | String(191)        | Sim         | Nome do produto                                |
| product.offer.id                          | String             | Sim         | ID da oferta                                   |
| product.offer.name                        | String             | Sim         | Nome da oferta                                 |
| product.producer.marketplace_id           | String(191)        | Sim         | ID do marketplace do produtor                 |
| product.producer.name                     | String(191)        | Sim         | Nome do produtor                               |
| product.producer.contact_email            | String(191)        | Não         | Email do produtor                              |
| product.qty                               | Integer            | Sim         | Quantidade do produto                          |
| product.total_value                       | Float              | Sim         | Valor total do produto                         |
| product.type                              | String(191)        | Sim         | Tipo do produto (plan/product)                |
| product.unit_value                        | Float              | Sim         | Valor unitário do produto                      |
| shipment.carrier                          | String(191)        | Não         | Nome da transportadora                         |
| shipment.service                          | String(191)        | Não         | Serviço da transportadora                      |
| shipment.tracking                         | String(191)        | Não         | Código de rastreamento                         |
| shipment.value                            | Float              | Não         | Valor da transportadora                        |
| shipment.status                           | Array              | Não         | Estados do envio                               |
| shipment.delivery_time                    | Integer            | Não         | Tempo de entrega                               |
| shipping.name                             | String             | Sim         | Nome do frete                                  |
| shipping.value                            | Float              | Sim         | Valor do frete                                 |
| source.source                             | String(191)        | Não         | Origem da venda                                |
| source.checkout_source                    | String(191)        | Não         | Origem da venda                                |
| source.utm_source                         | String(191)        | Não         | Origem da venda                                |
| source.utm_campaign                       | String(191)        | Não         | Origem da venda                                |
| source.utm_medium                         | String(191)        | Não         | Origem da venda                                |
| source.utm_content                        | String(191)        | Não         | Origem da venda                                |
| source.utm_term                           | String(191)        | Não         | Origem da venda                                |
| source.pptc.tracking_name                 | String(191)        | Não         | Nome do rastreamento                           |
| source.pptc.tracking_type                 | TrackingType       | Não         | Tipo do rastreamento                           |
| source.pptc.tracking_publisher            | Publisher          | Não         | Anunciante do rastreamento                     |
| source.pptc.user_name                     | String(191)        | Não         | Nome do usuário                                |
| source.pptc.checkout_name                 | String(191)        | Não         | Nome do checkout                               |
| source.pptc.utm_campaign                  | String(191)        | Não         | UTM_CAMPAIGN do rastreamento                   |
| source.pptc.utm_medium                    | String(191)        | Não         | UTM_MEDIUM do rastreamento                     |
| source.pptc.utm_content                   | String(191)        | Não         | UTM_CONTENT do rastreamento                    |
| source.pptc.utm_term                      | String(191)        | Não         | UTM_TERM do rastreamento                       |
| status                                    | TransactionStatus  | Sim         | Status da venda                                |
| subscription.can_cancel                   | Integer (0/1)      | Não         | Indica se a assinatura pode ser cancelada      |
| subscription.canceled_at                  | YYYY-MM-DDTHH:MM:SSZ | Não       | Data de cancelamento do plano                 |
| subscription.charged_every_days           | Integer            | Não         | Quantidade de dias entre cobranças            |
| subscription.charged_times                | Integer            | Não         | Quantidade de cobranças                       |
| subscription.id                           | String(191)        | Não         | Código do plano                                |
| subscription.internal_id                  | String             | Não         | ID interno da assinatura                      |
| subscription.last_status                  | SubscriptionStatus | Não         | Status do plano                                |
| subscription.last_status_at               | YYYY-MM-DDTHH:MM:SSZ | Não       | Data da última atualização de status          |
| subscription.name                         | String(191)        | Não         | Nome do plano                                  |
| subscription.started_at                   | YYYY-MM-DDTHH:MM:SSZ | Não       | Data da primeira cobrança                     |
| subscription.subscription_code            | String             | Não         | Código da assinatura                          |
| subscription.trial_days                   | Integer            | Não         | Dias de trial                                  |
| subscription.trial_finished_at           | YYYY-MM-DD         | Não         | Fim do trial                                   |
| subscription.trial_started_at            | YYYY-MM-DD         | Não         | Início do trial                                |
| type                                      | Types              | Sim         | Tipo da venda                                  |
| webhook_type                              | String             | Sim         | Tipo do webhook (transaction)                 |