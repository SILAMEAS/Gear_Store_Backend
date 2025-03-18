from rest_framework import serializers
# ===== Serializer for Dashboard Response ===== #
class DashboardSummarySerializer(serializers.Serializer):
    cards = serializers.ListField(
        child=serializers.DictField()
    )
    top_selling_products = serializers.ListField(
        child=serializers.DictField()
    )
    recent_orders_data = serializers.ListField(
        child=serializers.DictField()
    )
    sales_chart = serializers.ListField(
        child=serializers.DictField()
    )