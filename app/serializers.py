from rest_framework import serializers
from .models import User, Product, ProductLog, Transaction
from django.core.mail import send_mail


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterUserSerializer(serializers.ModelSerializer):
    class Meta:
        model  = User
        fields = ('username', 'last_name', 'password', 'email', 'phone', 'address')

    def create(self, validated_data):
        user = User.objects.create(
            username = validated_data['username'],
            last_name = validated_data['last_name'],
            email = validated_data['email'],
            phone = validated_data['phone'],
            address = validated_data['address']
        )
        user.set_password(validated_data['password'])
        user.save()
        send_mail(
            subject=f"Hurmatli {user.username}",
            message='Siz POS systemasiga register boldingiz!',
            from_email='samixonjoraxanov2010@gmail.com',
            recipient_list=[user.email],
            fail_silently=False,
            )
        return user

class ProductSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Product
        fields = ('id', 'name', 'description', 'price', 'quantity', 'owner')

class ProductLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductLog
        fields = ('user', 'product', 'action', 'timestamp')
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else 'Deleted Product'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ('product', 'quantity', 'seller', 'sold_at')
        read_only_fields = ('sold_at',)