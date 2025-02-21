from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, Count, Q, F
from datetime import datetime
from rest_framework import status

from api.app.category.models import Category
from api.app.order.models import OrderItem,Order
from api.app.payment.models import Payment
from api.app.product.models import Product
from api.app.user.models import User

@extend_schema(tags=["Dashboard"])
class DashboardSummaryView(APIView):
    def get(self, request):
        # Get optional date filters
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")

        # Convert string dates to datetime objects
        if start_date:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        if end_date:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")

        # Filter only delivered orders
        date_filter = Q(status="delivered")
        if start_date and end_date:
            date_filter &= Q(created_at__range=[start_date, end_date])
        elif start_date:
            date_filter &= Q(created_at__gte=start_date)
        elif end_date:
            date_filter &= Q(created_at__lte=end_date)

        delivered_orders = Order.objects.filter(date_filter)

        # Total Sales
        total_sales = OrderItem.objects.filter(order__in=delivered_orders).aggregate(
            total_sales=Sum(F("product__price") * F("quantity"))
        )["total_sales"] or 0

        # Total Orders
        total_orders = delivered_orders.count()

        # Total Customers
        total_customers = User.objects.filter(orders__in=delivered_orders).distinct().count()

        # Total Payment Received
        total_payment = Payment.objects.filter(order__in=delivered_orders, status="completed").aggregate(
            total_payment=Sum("amount")
        )["total_payment"] or 0

        # Total Products
        total_products = Product.objects.count()

        # Total Categories
        total_categories = Category.objects.count()

        # Top Selling Products
        top_selling_products = OrderItem.objects.filter(order__in=delivered_orders) \
                                   .values("product__id", "product__name", "product__image") \
                                   .annotate(
            total_quantity_sold=Sum("quantity"),
            revenue=Sum(F("product__price") * F("quantity"))
        ) \
                                   .order_by("-total_quantity_sold")[:5]

        # Transforming the queryset to match the desired response format
        top_selling_products_response = [
            {
                "id": product["product__id"],
                "name": product["product__name"],
                "sold": product["total_quantity_sold"],
                "revenue": product["revenue"],
                "image": product["product__image"],
            }
            for product in top_selling_products
        ]

        # Recent Orders Data
        recent_orders_data = Order.objects.filter(date_filter).order_by("-created_at")[:5].prefetch_related('items')
        recent_orders_response = [
            {
                "id": order.id,
                "customer": order.user.username,
                "product": ", ".join([item.product.name for item in order.items.all()]),  # Join product names
                "date": order.created_at.strftime("%Y-%m-%d"),
                "amount": sum(item.total_price for item in order.items.all()),  # Calculate total amount
                "status": order.status,
            }
            for order in recent_orders_data
        ]

        # Sales Chart Data
        sales_chart = []
        for month in range(1, 13):  # 1 to 12 for Jan to Dec
            monthly_sales = OrderItem.objects.filter(
                order__in=delivered_orders,
                order__created_at__month=month
            ).aggregate(monthly_sales=Sum(F("product__price") * F("quantity")))["monthly_sales"] or 0
            sales_chart.append({
                "date": datetime(2000, month, 1).strftime("%b"),  # Get month abbreviation
                "amount": monthly_sales
            })

        return Response({
            "cards": [
                {
                    "id":"total_sales",
                    "title": "Total Sales",
                    "value": total_sales,
                },
                {
                    "id": "total_orders",
                    "title": "Total Orders",
                    "value": total_orders,
                },
                {
                    "id": "total_customers",
                    "title": "Total Customers",
                    "value": total_customers,
                },
                {
                    "id": "total_payment",
                    "title": "Total Payment",
                    "value": total_payment,
                },
                {
                    "id": "total_products",
                    "title": "Total Products",
                    "value": total_products,
                },
                {
                    "id": "total_categories",
                    "title": "Total Categories",
                    "value": total_categories,
                }
            ],
            "top_selling_products": top_selling_products_response,  # Updated response format
            "recent_orders_data": recent_orders_response,  # Updated recent orders format
            "sales_chart": sales_chart  # New sales chart data
        }, status=status.HTTP_200_OK)
