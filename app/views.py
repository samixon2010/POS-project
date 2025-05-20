from rest_framework.generics import GenericAPIView, RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from app.models import Product, User
from .serializers import RegisterUserSerializer, UserLoginSerializer, ProductLogSerializer, ProductSerializer, TransactionSerializer
from rest_framework.response import Response
from .models import ProductLog, Transaction
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

# Create your views here.

# Authrntications

class RegisterUser(GenericAPIView):
    serializer_class = RegisterUserSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            email = serializer.validated_data['email']
            if User.objects.filter(username=username).exists():
                return Response({"msg": "This username already exists!!!"}, status=status.HTTP_400_BAD_REQUEST)
            elif User.objects.filter(email=email).exists():
                return Response({"msg":"Thsi email is already exists!!!"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            return Response({"msg": f"This user ({username}) registered!!!"}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginUser(GenericAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username = serializer.validated_data['username'],
                password = serializer.validated_data['password']
            )
            if user is not None:
                refresh = RefreshToken.for_user(user)
                return Response({'access':str(refresh.access_token), 'refresh':str(refresh)})
            return Response({'msg':'You forgot to enter username or password'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# Crud methods on product

class ProductCreateView(ListCreateAPIView):
    serializer_class  = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)
    

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(owner=request.user)
        ProductLog.objects.create(user=request.user, product=product, action='create')
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UpdateDelateProductView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Product.objects.filter(owner=self.request.user)

    def perform_update(self, serializer):
        product = serializer.save()
        ProductLog.objects.create(
            user=self.request.user,
            product=product,
            action='update'
        )

    def perform_destroy(self, instance):
        ProductLog.objects.create(
            user=self.request.user,
            product=instance,
            action='delete'
        )
        instance.delete()


# Transactions


class TranssactionView(ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(seller=self.request.user)

    
    def perform_create(self, serializer):

        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']

        if quantity > product.quantity:
            raise ValidationError({"detail": "Siz o'ylaganchalik mahsulot yo'q!"})

        product.quantity -= quantity
        product.save()

        transaction = serializer.save(seller=self.request.user)
        ProductLog.objects.create(
            user=self.request.user,
            product=transaction.product,
            action = 'sale'
        )
    
class UpdateDeleteTransactionView(RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes  = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(seller=self.request.user)


    def perform_update(self, serializer):
        transaction = serializer.save()
        ProductLog.objects.create(
            user=self.request.user,
            product=transaction.product,
            action = 'update'
        )
    def perform_destroy(self, instance):
        ProductLog.objects.create(
            user=self.request.user,
            product=instance.product,
            action = 'delete'
        )
        instance.delete()


# Log

class ProductLogListView(ListAPIView):
    serializer_class = ProductLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ProductLog.objects.filter(user=self.request.user)