from rest_framework import serializers
from api.models import Category, Product,Wishlist,ProductThumbnail
class ProductThumbnailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductThumbnail
        fields = ["id", "image"]  # Returning image URL only
# Product Serializer
class ProductSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(required=True)  # Required during creation
    name = serializers.CharField(required=True)  # Required during creation
    description = serializers.CharField(required=True)  # Required during creation
    price = serializers.DecimalField(required=True, max_digits=10, decimal_places=2)  # Required during creation
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())  # Accepts category ID
    rating = serializers.SerializerMethodField(method_name="get_rating")
    thumbnails = ProductThumbnailSerializer(many=True, read_only=True)  # Nested thumbnails
    isWishlist = serializers.SerializerMethodField(method_name="get_is_in_wishlist")
    class Meta:
        model = Product
        fields = ["id", "name", "description", "image", "price", "colors", "sizes", "rating", "category", "stock","thumbnails","isWishlist"]

    def get_rating(self, obj):
        reviews = obj.reviews.all()
        return round(sum(review.rating for review in reviews) / reviews.count(), 1) if reviews.exists() else 0.0

    def get_is_in_wishlist(self, obj):
        request = self.context.get('request', None)

        # Debugging prints
        print("Request Object:", request)
        if request:
            print("User:", request.user)
            print("Is Authenticated:", request.user.is_authenticated)

        if request and request.user and request.user.is_authenticated:
            return Wishlist.objects.filter(user=request.user, product=obj).exists()

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
        # Update fields based on what is provided in validated_data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
