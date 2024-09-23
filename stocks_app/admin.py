from django.contrib import admin

from stocks_app.models import *


class TransactionAdmin(admin.ModelAdmin):
    exclude = ('transaction_price',)

    def save_model(self, request, obj, form, change):
        stock = Stock.objects.get(id=obj.ticker.id)
        obj.transaction_price = stock.price * obj.transaction_volume
        super().save_model(request, obj, form, change)


# Register the model with the custom admin
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(users)
admin.site.register(Stock)
