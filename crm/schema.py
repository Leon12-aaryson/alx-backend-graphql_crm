import graphene
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField
from django.db import transaction
from django.core.exceptions import ValidationError
import re
from .models import Customer, Product, Order, OrderItem
from .filters import CustomerFilter, ProductFilter, OrderFilter


# Type Definitions
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains'],
            'email': ['exact', 'icontains'],
            'phone': ['exact', 'icontains'],
            'created_at': ['exact', 'gte', 'lte'],
        }


class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'name': ['exact', 'icontains'],
            'price': ['exact', 'gte', 'lte'],
            'stock': ['exact', 'gte', 'lte'],
        }


class OrderItemType(DjangoObjectType):
    class Meta:
        model = OrderItem
        interfaces = (graphene.relay.Node,)


class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        interfaces = (graphene.relay.Node,)
        filter_fields = {
            'total_amount': ['exact', 'gte', 'lte'],
            'order_date': ['exact', 'gte', 'lte'],
        }


# Input Types
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Response Types
class CreateCustomerResponse(graphene.ObjectType):
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    errors = graphene.List(graphene.String)


class BulkCreateCustomersResponse(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)


class CreateProductResponse(graphene.ObjectType):
    product = graphene.Field(ProductType)
    errors = graphene.List(graphene.String)


class CreateOrderResponse(graphene.ObjectType):
    order = graphene.Field(OrderType)
    errors = graphene.List(graphene.String)


class UpdateLowStockProductsResponse(graphene.ObjectType):
    updated_products = graphene.List(ProductType)
    success_message = graphene.String()
    errors = graphene.List(graphene.String)


# Mutations
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    Output = CreateCustomerResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate email uniqueness
        if Customer.objects.filter(email=input.email).exists():
            errors.append("Email already exists")
            return CreateCustomerResponse(customer=None, message="", errors=errors)
        
        # Validate phone format if provided
        if input.phone:
            phone_pattern = r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'
            if not re.match(phone_pattern, input.phone):
                errors.append("Invalid phone number format")
                return CreateCustomerResponse(customer=None, message="", errors=errors)
        
        try:
            customer = Customer.objects.create(
                name=input.name,
                email=input.email,
                phone=input.phone or ""
            )
            return CreateCustomerResponse(
                customer=customer,
                message="Customer created successfully",
                errors=[]
            )
        except Exception as e:
            errors.append(str(e))
            return CreateCustomerResponse(customer=None, message="", errors=errors)


class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    Output = BulkCreateCustomersResponse

    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for customer_input in input:
                try:
                    # Validate email uniqueness
                    if Customer.objects.filter(email=customer_input.email).exists():
                        errors.append(f"Email {customer_input.email} already exists")
                        continue
                    
                    # Validate phone format if provided
                    if customer_input.phone:
                        phone_pattern = r'^(\+\d{1,3}[- ]?)?\(?\d{3}\)?[- ]?\d{3}[- ]?\d{4}$'
                        if not re.match(phone_pattern, customer_input.phone):
                            errors.append(f"Invalid phone format for {customer_input.email}")
                            continue
                    
                    customer = Customer.objects.create(
                        name=customer_input.name,
                        email=customer_input.email,
                        phone=customer_input.phone or ""
                    )
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Error creating {customer_input.email}: {str(e)}")
        
        return BulkCreateCustomersResponse(customers=customers, errors=errors)


class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    Output = CreateProductResponse

    def mutate(self, info, input):
        errors = []
        
        # Validate price is positive
        if input.price <= 0:
            errors.append("Price must be positive")
            return CreateProductResponse(product=None, errors=errors)
        
        # Validate stock is non-negative
        if input.stock and input.stock < 0:
            errors.append("Stock cannot be negative")
            return CreateProductResponse(product=None, errors=errors)
        
        try:
            from decimal import Decimal
            product = Product.objects.create(
                name=input.name,
                price=Decimal(str(input.price)),
                stock=input.stock or 0
            )
            return CreateProductResponse(product=product, errors=[])
        except Exception as e:
            errors.append(str(e))
            return CreateProductResponse(product=None, errors=errors)


class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    Output = CreateOrderResponse

    def mutate(self, info, input):
        errors = []
        
        try:
            # Validate customer exists
            customer = Customer.objects.get(id=input.customer_id)
        except Customer.DoesNotExist:
            errors.append("Invalid customer ID")
            return CreateOrderResponse(order=None, errors=errors)
        
        # Validate at least one product
        if not input.product_ids:
            errors.append("At least one product must be selected")
            return CreateOrderResponse(order=None, errors=errors)
        
        # Validate products exist
        products = []
        for product_id in input.product_ids:
            try:
                product = Product.objects.get(id=product_id)
                products.append(product)
            except Product.DoesNotExist:
                errors.append(f"Invalid product ID: {product_id}")
                return CreateOrderResponse(order=None, errors=errors)
        
        try:
            with transaction.atomic():
                # Create order
                order = Order.objects.create(
                    customer=customer,
                    total_amount=0  # Will be calculated below
                )
                
                # Create order items and calculate total
                total_amount = 0
                for product in products:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        quantity=1,
                        price=product.price
                    )
                    total_amount += product.price
                
                # Update order total
                order.total_amount = total_amount
                order.save()
                
                return CreateOrderResponse(order=order, errors=[])
        except Exception as e:
            errors.append(str(e))
            return CreateOrderResponse(order=None, errors=errors)


class UpdateLowStockProducts(graphene.Mutation):
    """
    Mutation to update low stock products (stock < 10) by incrementing their stock by 10
    """
    
    class Arguments:
        pass  # No arguments needed
    
    Output = UpdateLowStockProductsResponse
    
    def mutate(self, info):
        errors = []
        updated_products = []
        
        try:
            # Find products with stock < 10
            low_stock_products = Product.objects.filter(stock__lt=10)
            
            # Update each product's stock
            for product in low_stock_products:
                product.stock += 10
                product.save()
                updated_products.append(product)
            
            success_message = f"Updated {len(updated_products)} low stock products"
            
            return UpdateLowStockProductsResponse(
                updated_products=updated_products,
                success_message=success_message,
                errors=[]
            )
            
        except Exception as e:
            errors.append(str(e))
            return UpdateLowStockProductsResponse(
                updated_products=[],
                success_message="",
                errors=errors
            )


class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()
    update_low_stock_products = UpdateLowStockProducts.Field()


# Query Class
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello, GraphQL!")
    
    # Customer queries
    all_customers = graphene.List(CustomerType)
    customer = graphene.Field(CustomerType, id=graphene.ID(required=True))
    
    # Product queries
    all_products = graphene.List(ProductType)
    product = graphene.Field(ProductType, id=graphene.ID(required=True))
    
    # Order queries
    all_orders = graphene.List(OrderType)
    order = graphene.Field(OrderType, id=graphene.ID(required=True))
    
    def resolve_all_customers(self, info, **kwargs):
        return Customer.objects.all()
    
    def resolve_all_products(self, info, **kwargs):
        return Product.objects.all()
    
    def resolve_all_orders(self, info, **kwargs):
        return Order.objects.all()
    
    def resolve_customer(self, info, id):
        try:
            return Customer.objects.get(id=id)
        except Customer.DoesNotExist:
            return None
    
    def resolve_product(self, info, id):
        try:
            return Product.objects.get(id=id)
        except Product.DoesNotExist:
            return None
    
    def resolve_order(self, info, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            return None
