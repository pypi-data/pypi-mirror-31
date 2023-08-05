#!/usr/bin/env python

from park.api.api import API

class Transaction(API):
    def transaction(self, id):
        return self.get('api/transactions/get', { "id" : id })

    def transactions(self, parameters={}):
        return self.get('api/transactions', parameters)

    def unconfirmedTransaction(self, id):
        return self.get('api/transactions/unconfirmed/get', { "id" : id })

    def unconfirmedTransactions(self, parameters={}):
        return self.get('api/transactions/unconfirmed', parameters)

    def create(self, recipientId, amount, vendorField, secret, secondSecret=None):
        transaction = self.client.transactionBuilder().create(
            recipientId, amount, vendorField, secret, secondSecret
        )

        return self.client.transport().createTransaction(transaction)
