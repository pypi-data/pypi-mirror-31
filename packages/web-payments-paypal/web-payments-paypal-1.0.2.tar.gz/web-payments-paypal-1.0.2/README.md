web-payments-paypal
===================

Status
------
PaypalProvider works
PaypalCardProvider may make issues, test first (I have no credit card)

Usage
-----

add ProviderVariant to PAYMENT_VARIANTS_API or to list_providers:

``` python

# normal
ProviderVariant('web_payments_paypal.PaypalProvider', {
    "client_id": "<clientid>",
    "secret": "<secret>",
    "endpoint": 'https://api.sandbox.paypal.com'
    "capture": True
  },
  {}
)

# with credit card
ProviderVariant('web_payments_paypal.PaypalCardProvider', {
    "client_id": "<clientid>",
    "secret": "<secret>",
    "endpoint": 'https://api.sandbox.paypal.com'
    "capture": True
  },
  {}
)

```
