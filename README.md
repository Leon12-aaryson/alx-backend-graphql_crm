# ALX Backend GraphQL CRM

A comprehensive Customer Relationship Management (CRM) system built with Django and GraphQL, featuring advanced filtering, mutations, and robust error handling.

## Features

### 🚀 Core Functionality
- **GraphQL API** with full CRUD operations
- **Customer Management** with validation and bulk operations
- **Product Catalog** with inventory tracking
- **Order Management** with automatic total calculation
- **Advanced Filtering** using django-filter
- **Robust Error Handling** with user-friendly messages

### 🔧 Technical Features
- Django 5.2.5 backend
- GraphQL API using graphene-django
- Advanced filtering and search capabilities
- Transaction-based operations for data integrity
- Comprehensive validation and error handling
- RESTful GraphQL mutations and queries

## Installation

### Prerequisites
- Python 3.8+
- pip

### Setup
1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd alx-backend-graphql_crm
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Seed the database (optional)**
   ```bash
   python seed_db.py
   ```

6. **Start the development server**
   ```bash
   python manage.py runserver
   ```

## Usage

### GraphQL Endpoint
Access the GraphQL playground at: `http://localhost:8000/graphql`

### Basic Query Example
```graphql
query {
  hello
}
```

### Customer Operations

#### Create a Customer
```graphql
mutation {
  createCustomer(input: {
    name: "Alice",
    email: "alice@example.com",
    phone: "+1234567890"
  }) {
    customer {
      id
      name
      email
      phone
    }
    message
    errors
  }
}
```

#### Bulk Create Customers
```graphql
mutation {
  bulkCreateCustomers(input: [
    { name: "Bob", email: "bob@example.com", phone: "123-456-7890" },
    { name: "Carol", email: "carol@example.com" }
  ]) {
    customers {
      id
      name
      email
    }
    errors
  }
}
```

#### Query Customers with Filters
```graphql
query {
  allCustomers(filter: { 
    nameIcontains: "Ali", 
    createdAtGte: "2025-01-01" 
  }) {
    edges {
      node {
        id
        name
        email
        createdAt
      }
    }
  }
}
```

### Product Operations

#### Create a Product
```graphql
mutation {
  createProduct(input: {
    name: "Laptop",
    price: 999.99,
    stock: 10
  }) {
    product {
      id
      name
      price
      stock
    }
    errors
  }
}
```

#### Query Products with Filters
```graphql
query {
  allProducts(filter: { 
    priceGte: 100, 
    priceLte: 1000 
  }) {
    edges {
      node {
        id
        name
        price
        stock
      }
    }
  }
}
```

### Order Operations

#### Create an Order
```graphql
mutation {
  createOrder(input: {
    customerId: "1",
    productIds: ["1", "2"]
  }) {
    order {
      id
      customer {
        name
      }
      products {
        name
        price
      }
      totalAmount
      orderDate
    }
    errors
  }
}
```

#### Query Orders with Filters
```graphql
query {
  allOrders(filter: { 
    customerName: "Alice", 
    totalAmountGte: 500 
  }) {
    edges {
      node {
        id
        customer {
          name
        }
        totalAmount
        orderDate
      }
    }
  }
}
```

## API Reference

### Models

#### Customer
- `id`: Unique identifier
- `name`: Customer name (required)
- `email`: Email address (required, unique)
- `phone`: Phone number (optional)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Product
- `id`: Unique identifier
- `name`: Product name (required)
- `price`: Product price (required, positive)
- `stock`: Available stock (optional, non-negative)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

#### Order
- `id`: Unique identifier
- `customer`: Associated customer (required)
- `products`: Associated products (many-to-many)
- `total_amount`: Order total (auto-calculated)
- `order_date`: Order date (auto-set)
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Filters

#### Customer Filters
- `name`: Case-insensitive partial match
- `email`: Case-insensitive partial match
- `created_at__gte`: Created after date
- `created_at__lte`: Created before date
- `phone_pattern`: Phone number pattern match

#### Product Filters
- `name`: Case-insensitive partial match
- `price__gte`: Price greater than or equal
- `price__lte`: Price less than or equal
- `stock__gte`: Stock greater than or equal
- `stock__lte`: Stock less than or equal
- `low_stock`: Products with stock < 10

#### Order Filters
- `total_amount__gte`: Total amount greater than or equal
- `total_amount__lte`: Total amount less than or equal
- `order_date__gte`: Order date after
- `order_date__lte`: Order date before
- `customer_name`: Filter by customer name
- `product_name`: Filter by product name
- `product_id`: Filter by specific product ID

## Error Handling

The system provides comprehensive error handling with:
- **Validation Errors**: Input validation with clear error messages
- **Business Logic Errors**: Domain-specific error handling
- **Database Errors**: Transaction rollback and error reporting
- **User-Friendly Messages**: Clear, actionable error descriptions

## Development

### Project Structure
```
alx-backend-graphql_crm/
├── alx_backend_graphql_crm/     # Main project directory
│   ├── settings.py              # Django settings
│   ├── urls.py                  # URL configuration
│   └── schema.py                # Main GraphQL schema
├── crm/                         # CRM application
│   ├── models.py                # Database models
│   ├── schema.py                # GraphQL types and mutations
│   └── filters.py               # Custom filters
├── manage.py                    # Django management script
├── seed_db.py                   # Database seeding script
└── requirements.txt             # Python dependencies
```

### Adding New Features
1. **Models**: Define in `crm/models.py`
2. **GraphQL Types**: Add to `crm/schema.py`
3. **Filters**: Extend `crm/filters.py`
4. **Migrations**: Run `python manage.py makemigrations`

## Testing

### Manual Testing
1. Start the server: `python manage.py runserver`
2. Visit: `http://localhost:8000/graphql`
3. Use the GraphQL playground to test queries and mutations

### Sample Data
The `seed_db.py` script creates sample data for testing:
- 4 customers with different phone formats
- 5 products with various prices and stock levels
- 4 orders with different product combinations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is part of the ALX Backend Specialization curriculum.

## Support

For questions or issues, please refer to the ALX curriculum materials or create an issue in the repository.
