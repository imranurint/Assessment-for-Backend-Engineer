from abc import ABC, abstractmethod

class BasePaymentProvider(ABC):
    @abstractmethod
    def create_payment(self, order):
        """
        Initiate a payment for the order.
        Returns a dictionary with necessary data for the client (e.g., client_secret, redirect_url).
        """
        pass

    @abstractmethod
    def confirm_payment(self, payment_id, **kwargs):
        """
        Confirm or execute the payment after client interaction.
        """
        pass

    @abstractmethod
    def query_payment(self, payment_id):
        """
        Check the status of a payment transaction.
        """
        pass
    
    @abstractmethod
    def handle_webhook(self, request):
        """
        Handle provider-specific webhooks.
        """
        pass
