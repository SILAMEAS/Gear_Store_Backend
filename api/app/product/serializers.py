from rest_framework import serializers


from api.models import Category, Product,Wishlist,ProductThumbnail
class ProductThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductThumbnail
        fields = ["id", "image"]  # Returning image URL only
# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=False, allow_null=True)  # Allow image to be optional
    name = serializers.CharField(required=True)  # Required during creation
    description = serializers.CharField(required=True)  # Required during creation
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)  # Required during creation
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accepts category ID
    avg_rating = serializers.SerializerMethodField(method_name="get_rating")
    thumbnails = ProductThumbnailSerializer(many=True, read_only=True)  # Nested thumbnails
    isWishlist = serializers.SerializerMethodField(method_name="get_is_in_wishlist")
    categoryName = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ["id", "name", "description", "image", "price", "colors", "sizes", "avg_rating", "category", "stock","thumbnails","isWishlist","categoryName","created_at","updated_at"]

    def get_categoryName(self, obj):
        return obj.category.name if obj.category else None
    def get_rating(self, obj):
        reviews = obj.reviews.all()
        return round(sum(review.rating for review in reviews) / reviews.count(), 1) if reviews.exists() else 0.0

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)

        if request and request.user and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()
        if request and request.user and request.user.is_anonymous:
            return "is_anonymous"

        return False
    def validate(self, attrs):
        # Check if the request is for creation or update
        if self.context['request'].method == 'POST':
            # In creation (POST), require all fields
            for field in ['image', 'name', 'description', 'price', 'category']:
                if field not in attrs:
                    raise serializers.ValidationError({field: f'This field is required.'})
        # If it's an update (PATCH), no extra validation needed
        return attrs

    def update(self, instance, validated_data):
        if "image" not in validated_data or validated_data["image"] is None:
            validated_data["image"] = instance.image  # Keep the old image
        return super().update(instance, validated_data)
