from api.payments.providers.stripe_provider import StripePaymentProvider
from api.payments.providers.bkash_provider import BkashPaymentProvider
from api.payments.base import BasePaymentProvider
from api.payments.providers.ssl_provider import SSLCommerzPaymentProvider
from api.payments.providers.stripe_checkout_provider import StripeCheckoutProvider

class PaymentFactory:
    @staticmethod
    def get_provider(provider_name: str) -> BasePaymentProvider:
        if provider_name == 'stripe':
            return StripePaymentProvider()
        elif provider_name == 'stripe-checkout':
            return StripeCheckoutProvider()
        # elif provider_name == 'bkash':
        #     return BkashPaymentProvider()
        elif provider_name == 'bkash':
            return SSLCommerzPaymentProvider()
        else:
            raise ValueError(f"Unsupported payment provider: {provider_name}")
