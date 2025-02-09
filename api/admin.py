from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import User, Category, Product, Order, OrderItem, Cart, Payment, ShippingAddress, Review, Wishlist

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Cart)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(Review)
admin.site.register(Wishlist)