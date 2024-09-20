from django.contrib import admin

from stocks_app.models import *


class TransactionAdmin(admin.ModelAdmin):
    # Exclude 'transaction_price' from the form
    exclude = ('transaction_price',)

    # Override the save_model method to calculate and save 'transaction_price'
    def save_model(self, request, obj, form, change):
        # Get the stock price
        stock = Stock.objects.get(id=obj.ticker.id)
        # Calculate the transaction price
        obj.transaction_price = stock.price * obj.transaction_volume
        # Save the transaction with the updated price
        super().save_model(request, obj, form, change)


# Register the model with the custom admin
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(User)
admin.site.register(Stock)
