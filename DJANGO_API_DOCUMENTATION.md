# Django Backend API Documentation for Maria Havens POS

This document provides comprehensive API endpoint specifications for integrating the Maria Havens POS frontend with a Django backend.

## Table of Contents
1. [Authentication](#authentication)
2. [Users](#users)
3. [Menu Items](#menu-items)
4. [Orders](#orders)
5. [Tables](#tables)
6. [Inventory](#inventory)
7. [Dashboard & Analytics](#dashboard--analytics)
8. [Guests](#guests)
9. [Service Requests](#service-requests)
10. [Payments](#payments)
11. [Receipts](#receipts)
12. [Reports](#reports)

---

## Base Configuration

**Base URL**: `http://your-django-server.com/api/`

**Authentication**: JWT Bearer Token
\`\`\`
Authorization: Bearer <your_jwt_token>
\`\`\`

**Environment Variable**: Set `NEXT_PUBLIC_API_URL` in your `.env.local` file:
\`\`\`
NEXT_PUBLIC_API_URL=http://your-django-server.com/api
\`\`\`

---

## Authentication

### POST /api/auth/login
Login user and receive JWT token.

**Request Body**:
\`\`\`json
{
  "email": "user@mariahavens.com",
  "password": "password123",
  "roomNumber": "101"  // Optional, required only for guest accounts
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "user": {
    "id": "1",
    "name": "John Admin",
    "email": "admin@mariahavens.com",
    "role": "admin",
    "phone": "+254712345678",
    "isActive": true,
    "createdAt": "2024-01-01T00:00:00Z",
    "roomNumber": null
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Error Response** (401 Unauthorized):
\`\`\`json
{
  "error": "Invalid credentials"
}
\`\`\`

### POST /api/auth/logout
Logout current user and invalidate token.

**Response** (200 OK):
\`\`\`json
{
  "message": "Logged out successfully"
}
\`\`\`

### GET /api/auth/me
Get current authenticated user details.

**Response** (200 OK):
\`\`\`json
{
  "id": "1",
  "name": "John Admin",
  "email": "admin@mariahavens.com",
  "role": "admin",
  "phone": "+254712345678",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
\`\`\`

### POST /api/auth/refresh
Refresh JWT token.

**Request Body**:
\`\`\`json
{
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
\`\`\`

---

## Users

### GET /api/users
Get all users (Admin/Manager only).

**Query Parameters**:
- `role` (optional): Filter by role (admin, manager, receptionist, waiter, kitchen, cashier, guest)
- `isActive` (optional): Filter by active status (true/false)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "1",
    "name": "John Admin",
    "email": "admin@mariahavens.com",
    "role": "admin",
    "phone": "+254712345678",
    "isActive": true,
    "createdAt": "2024-01-01T00:00:00Z"
  }
]
\`\`\`

### GET /api/users/:id
Get user by ID.

**Response** (200 OK):
\`\`\`json
{
  "id": "1",
  "name": "John Admin",
  "email": "admin@mariahavens.com",
  "role": "admin",
  "phone": "+254712345678",
  "isActive": true,
  "createdAt": "2024-01-01T00:00:00Z"
}
\`\`\`

### POST /api/users
Create new user (Admin only).

**Request Body**:
\`\`\`json
{
  "name": "New Staff",
  "email": "staff@mariahavens.com",
  "password": "password123",
  "role": "waiter",
  "phone": "+254712345678",
  "isActive": true
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "8",
  "name": "New Staff",
  "email": "staff@mariahavens.com",
  "role": "waiter",
  "phone": "+254712345678",
  "isActive": true,
  "createdAt": "2025-01-30T10:00:00Z"
}
\`\`\`

### PATCH /api/users/:id
Update user details.

**Request Body** (partial update):
\`\`\`json
{
  "name": "Updated Name",
  "phone": "+254700000000",
  "isActive": false
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "8",
  "name": "Updated Name",
  "email": "staff@mariahavens.com",
  "role": "waiter",
  "phone": "+254700000000",
  "isActive": false,
  "createdAt": "2025-01-30T10:00:00Z"
}
\`\`\`

### DELETE /api/users/:id
Delete user (Admin only).

**Response** (204 No Content)

### POST /api/users/:id/change-password
Change user password.

**Request Body**:
\`\`\`json
{
  "currentPassword": "oldpassword123",
  "newPassword": "newpassword123"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "message": "Password changed successfully"
}
\`\`\`

---

## Menu Items

### GET /api/menu
Get all menu items.

**Query Parameters**:
- `category` (optional): Filter by category
- `isAvailable` (optional): Filter by availability (true/false)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "m1",
    "name": "Ugali & Beef Stew",
    "description": "Traditional Kenyan meal with tender beef",
    "category": "Main Course",
    "price": 450,
    "image": "/images/ugali-beef.jpg",
    "isAvailable": true,
    "preparationTime": 20,
    "ingredients": ["Ugali", "Beef", "Tomatoes", "Onions"],
    "allergens": []
  }
]
\`\`\`

### GET /api/menu/:id
Get menu item by ID.

**Response** (200 OK):
\`\`\`json
{
  "id": "m1",
  "name": "Ugali & Beef Stew",
  "description": "Traditional Kenyan meal with tender beef",
  "category": "Main Course",
  "price": 450,
  "image": "/images/ugali-beef.jpg",
  "isAvailable": true,
  "preparationTime": 20,
  "ingredients": ["Ugali", "Beef", "Tomatoes", "Onions"],
  "allergens": []
}
\`\`\`

### POST /api/menu
Create new menu item (Admin/Manager/Kitchen only).

**Request Body**:
\`\`\`json
{
  "name": "New Dish",
  "description": "Delicious new dish",
  "category": "Main Course",
  "price": 500,
  "image": "/images/new-dish.jpg",
  "isAvailable": true,
  "preparationTime": 25,
  "ingredients": ["Ingredient 1", "Ingredient 2"],
  "allergens": ["Nuts"]
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "m20",
  "name": "New Dish",
  "description": "Delicious new dish",
  "category": "Main Course",
  "price": 500,
  "image": "/images/new-dish.jpg",
  "isAvailable": true,
  "preparationTime": 25,
  "ingredients": ["Ingredient 1", "Ingredient 2"],
  "allergens": ["Nuts"]
}
\`\`\`

### PATCH /api/menu/:id
Update menu item.

**Request Body** (partial update):
\`\`\`json
{
  "price": 550,
  "isAvailable": false
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "m20",
  "name": "New Dish",
  "description": "Delicious new dish",
  "category": "Main Course",
  "price": 550,
  "isAvailable": false,
  "preparationTime": 25
}
\`\`\`

### DELETE /api/menu/:id
Delete menu item (Admin/Manager only).

**Response** (204 No Content)

---

## Orders

### GET /api/orders
Get all orders.

**Query Parameters**:
- `status` (optional): Filter by status (pending, preparing, ready, served, completed, cancelled)
- `type` (optional): Filter by type (dine-in, takeaway, room-service)
- `waiterId` (optional): Filter by waiter ID
- `roomNumber` (optional): Filter by room number
- `startDate` (optional): Filter orders from date (ISO 8601)
- `endDate` (optional): Filter orders to date (ISO 8601)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "o1",
    "orderNumber": "ORD-001",
    "type": "dine-in",
    "tableId": "t2",
    "roomNumber": null,
    "customerId": null,
    "customerName": "Table 2",
    "items": [
      {
        "id": "oi1",
        "menuItemId": "m4",
        "menuItem": {
          "id": "m4",
          "name": "Chicken Tikka",
          "price": 650
        },
        "quantity": 2,
        "price": 650,
        "notes": "Extra spicy",
        "status": "preparing"
      }
    ],
    "subtotal": 1300,
    "tax": 130,
    "discount": 0,
    "total": 1430,
    "status": "preparing",
    "waiterId": "4",
    "waiter": {
      "id": "4",
      "name": "James Waiter"
    },
    "notes": "Customer prefers spicy",
    "createdAt": "2025-01-30T10:00:00Z",
    "updatedAt": "2025-01-30T10:15:00Z",
    "completedAt": null
  }
]
\`\`\`

### GET /api/orders/:id
Get order by ID.

**Response** (200 OK):
\`\`\`json
{
  "id": "o1",
  "orderNumber": "ORD-001",
  "type": "dine-in",
  "tableId": "t2",
  "customerName": "Table 2",
  "items": [...],
  "subtotal": 1300,
  "tax": 130,
  "discount": 0,
  "total": 1430,
  "status": "preparing",
  "waiterId": "4",
  "createdAt": "2025-01-30T10:00:00Z",
  "updatedAt": "2025-01-30T10:15:00Z"
}
\`\`\`

### POST /api/orders
Create new order.

**Request Body**:
\`\`\`json
{
  "type": "room-service",
  "roomNumber": "101",
  "customerName": "David Mwangi",
  "items": [
    {
      "menuItemId": "m1",
      "quantity": 2,
      "notes": "No onions"
    },
    {
      "menuItemId": "m5",
      "quantity": 1
    }
  ],
  "notes": "Deliver to room 101",
  "waiterId": "4"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "o10",
  "orderNumber": "ORD-010",
  "type": "room-service",
  "roomNumber": "101",
  "customerName": "David Mwangi",
  "items": [...],
  "subtotal": 1200,
  "tax": 120,
  "discount": 0,
  "total": 1320,
  "status": "pending",
  "waiterId": "4",
  "createdAt": "2025-01-30T11:00:00Z",
  "updatedAt": "2025-01-30T11:00:00Z"
}
\`\`\`

### PATCH /api/orders/:id
Update order (typically for status changes).

**Request Body**:
\`\`\`json
{
  "status": "preparing"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "o10",
  "orderNumber": "ORD-010",
  "status": "preparing",
  "updatedAt": "2025-01-30T11:05:00Z"
}
\`\`\`

---

## Tables

### GET /api/tables
Get all tables.

**Query Parameters**:
- `status` (optional): Filter by status (available, occupied, reserved, cleaning)
- `section` (optional): Filter by section

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "t1",
    "number": "1",
    "capacity": 4,
    "status": "available",
    "currentOrderId": null,
    "waiterId": null,
    "section": "Main Hall",
    "reservedBy": null,
    "reservedAt": null
  }
]
\`\`\`

### GET /api/tables/:id
Get table by ID.

**Response** (200 OK):
\`\`\`json
{
  "id": "t1",
  "number": "1",
  "capacity": 4,
  "status": "available",
  "currentOrderId": null,
  "waiterId": null,
  "section": "Main Hall"
}
\`\`\`

### PATCH /api/tables/:id
Update table status.

**Request Body**:
\`\`\`json
{
  "status": "occupied",
  "currentOrderId": "o1",
  "waiterId": "4"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "t1",
  "number": "1",
  "capacity": 4,
  "status": "occupied",
  "currentOrderId": "o1",
  "waiterId": "4"
}
\`\`\`

---

## Inventory

### GET /api/inventory
Get all inventory items.

**Query Parameters**:
- `category` (optional): Filter by category
- `lowStock` (optional): Get only low stock items (true/false)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "inv1",
    "name": "Tomatoes",
    "category": "Vegetables",
    "unit": "kg",
    "quantity": 50,
    "reorderLevel": 20,
    "unitPrice": 80,
    "supplier": "Fresh Farms Ltd",
    "lastRestocked": "2025-01-28T08:00:00Z",
    "expiryDate": "2025-02-05T00:00:00Z"
  }
]
\`\`\`

### GET /api/inventory/low-stock
Get items below reorder level.

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "inv5",
    "name": "Cooking Oil",
    "category": "Pantry",
    "unit": "liters",
    "quantity": 8,
    "reorderLevel": 15,
    "unitPrice": 350
  }
]
\`\`\`

### POST /api/inventory
Create new inventory item.

**Request Body**:
\`\`\`json
{
  "name": "New Item",
  "category": "Pantry",
  "unit": "kg",
  "quantity": 100,
  "reorderLevel": 30,
  "unitPrice": 150,
  "supplier": "Supplier Name"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "inv20",
  "name": "New Item",
  "category": "Pantry",
  "unit": "kg",
  "quantity": 100,
  "reorderLevel": 30,
  "unitPrice": 150,
  "supplier": "Supplier Name"
}
\`\`\`

### PATCH /api/inventory/:id
Update inventory item.

**Request Body**:
\`\`\`json
{
  "quantity": 120,
  "lastRestocked": "2025-01-30T10:00:00Z"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "inv20",
  "name": "New Item",
  "quantity": 120,
  "lastRestocked": "2025-01-30T10:00:00Z"
}
\`\`\`

### POST /api/inventory/waste
Track inventory waste.

**Request Body**:
\`\`\`json
{
  "itemId": "inv1",
  "quantity": 5,
  "reason": "Spoiled"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "message": "Waste tracked successfully",
  "item": {
    "id": "inv1",
    "name": "Tomatoes",
    "quantity": 45
  }
}
\`\`\`

---

## Dashboard & Analytics

### GET /api/dashboard/stats
Get dashboard statistics.

**Response** (200 OK):
\`\`\`json
{
  "todaySales": 45000,
  "todayOrders": 32,
  "activeOrders": 8,
  "availableTables": 12,
  "customersServed": 85,
  "averageOrderValue": 1406.25,
  "salesGrowth": 12.5,
  "ordersGrowth": 8.3
}
\`\`\`

### GET /api/dashboard/sales
Get sales data for charts.

**Query Parameters**:
- `days` (optional): Number of days (default: 7)

**Response** (200 OK):
\`\`\`json
[
  {
    "date": "2025-01-24",
    "sales": 38000,
    "orders": 28
  },
  {
    "date": "2025-01-25",
    "sales": 42000,
    "orders": 31
  }
]
\`\`\`

### GET /api/dashboard/category-sales
Get sales by category.

**Response** (200 OK):
\`\`\`json
[
  {
    "category": "Main Course",
    "sales": 125000,
    "orders": 85
  },
  {
    "category": "Beverages",
    "sales": 45000,
    "orders": 120
  }
]
\`\`\`

---

## Guests

### GET /api/guests
Get all guests.

**Query Parameters**:
- `status` (optional): Filter by status (checked-in, checked-out)
- `roomNumber` (optional): Filter by room number

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "g1",
    "name": "David Mwangi",
    "email": "david.mwangi@email.com",
    "phone": "+254712345678",
    "roomNumber": "101",
    "checkInDate": "2025-01-20T14:00:00Z",
    "checkOutDate": "2025-01-25T11:00:00Z",
    "status": "checked-in",
    "totalSpent": 45000
  }
]
\`\`\`

### GET /api/guests/:id
Get guest by ID.

**Response** (200 OK):
\`\`\`json
{
  "id": "g1",
  "name": "David Mwangi",
  "email": "david.mwangi@email.com",
  "phone": "+254712345678",
  "roomNumber": "101",
  "checkInDate": "2025-01-20T14:00:00Z",
  "checkOutDate": "2025-01-25T11:00:00Z",
  "status": "checked-in",
  "totalSpent": 45000
}
\`\`\`

### POST /api/guests/check-in
Check in a new guest.

**Request Body**:
\`\`\`json
{
  "name": "New Guest",
  "email": "guest@email.com",
  "phone": "+254700000000",
  "roomNumber": "205",
  "checkInDate": "2025-01-30T14:00:00Z",
  "checkOutDate": "2025-02-05T11:00:00Z"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "g10",
  "name": "New Guest",
  "email": "guest@email.com",
  "phone": "+254700000000",
  "roomNumber": "205",
  "checkInDate": "2025-01-30T14:00:00Z",
  "checkOutDate": "2025-02-05T11:00:00Z",
  "status": "checked-in",
  "totalSpent": 0
}
\`\`\`

### POST /api/guests/:id/check-out
Check out a guest.

**Response** (200 OK):
\`\`\`json
{
  "id": "g10",
  "name": "New Guest",
  "status": "checked-out",
  "totalSpent": 12500
}
\`\`\`

### PATCH /api/guests/:id
Update guest details.

**Request Body**:
\`\`\`json
{
  "phone": "+254711111111",
  "checkOutDate": "2025-02-06T11:00:00Z"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "g10",
  "name": "New Guest",
  "phone": "+254711111111",
  "checkOutDate": "2025-02-06T11:00:00Z"
}
\`\`\`

---

## Service Requests

### GET /api/service-requests
Get all service requests.

**Query Parameters**:
- `guestId` (optional): Filter by guest ID
- `status` (optional): Filter by status (pending, in-progress, completed, cancelled)
- `priority` (optional): Filter by priority (low, medium, high)
- `type` (optional): Filter by type (housekeeping, maintenance, room-service, concierge, other)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "sr1",
    "guestId": "g1",
    "guestName": "David Mwangi",
    "roomNumber": "101",
    "type": "housekeeping",
    "description": "Need fresh towels and room cleaning",
    "priority": "medium",
    "status": "pending",
    "createdAt": "2025-01-30T09:00:00Z",
    "completedAt": null,
    "assignedTo": null
  }
]
\`\`\`

### POST /api/service-requests
Create new service request.

**Request Body**:
\`\`\`json
{
  "guestId": "g1",
  "guestName": "David Mwangi",
  "roomNumber": "101",
  "type": "maintenance",
  "description": "AC not working properly",
  "priority": "high"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "sr10",
  "guestId": "g1",
  "guestName": "David Mwangi",
  "roomNumber": "101",
  "type": "maintenance",
  "description": "AC not working properly",
  "priority": "high",
  "status": "pending",
  "createdAt": "2025-01-30T11:00:00Z"
}
\`\`\`

### PATCH /api/service-requests/:id
Update service request.

**Request Body**:
\`\`\`json
{
  "status": "in-progress",
  "assignedTo": "staff-id-123"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "sr10",
  "status": "in-progress",
  "assignedTo": "staff-id-123"
}
\`\`\`

---

## Payments

### GET /api/payments
Get all payments.

**Query Parameters**:
- `orderId` (optional): Filter by order ID
- `status` (optional): Filter by status (pending, completed, refunded, failed)
- `method` (optional): Filter by method (cash, card, mpesa, bank-transfer)

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "p1",
    "orderId": "o1",
    "amount": 1430,
    "method": "mpesa",
    "status": "completed",
    "transactionId": "TXN123456",
    "mpesaCode": "QAB12CD3EF",
    "cashierId": "6",
    "cashier": {
      "id": "6",
      "name": "Lucy Cashier"
    },
    "createdAt": "2025-01-30T10:30:00Z"
  }
]
\`\`\`

### POST /api/payments
Process new payment.

**Request Body**:
\`\`\`json
{
  "orderId": "o10",
  "amount": 1320,
  "method": "card",
  "transactionId": "CARD789012",
  "cashierId": "6"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "p10",
  "orderId": "o10",
  "amount": 1320,
  "method": "card",
  "status": "completed",
  "transactionId": "CARD789012",
  "cashierId": "6",
  "createdAt": "2025-01-30T11:30:00Z"
}
\`\`\`

### POST /api/payments/:id/refund
Refund a payment.

**Request Body**:
\`\`\`json
{
  "reason": "Customer complaint - food quality"
}
\`\`\`

**Response** (200 OK):
\`\`\`json
{
  "id": "p10",
  "status": "refunded",
  "refundedAt": "2025-01-30T12:00:00Z",
  "refundReason": "Customer complaint - food quality"
}
\`\`\`

---

## Receipts

### GET /api/receipts
Get all receipts.

**Query Parameters**:
- `orderId` (optional): Filter by order ID
- `startDate` (optional): Filter from date
- `endDate` (optional): Filter to date

**Response** (200 OK):
\`\`\`json
[
  {
    "id": "r1",
    "receiptNumber": "RCP-001",
    "orderId": "o1",
    "order": {...},
    "payment": {...},
    "issuedBy": "6",
    "issuedAt": "2025-01-30T10:35:00Z",
    "printedAt": "2025-01-30T10:35:30Z"
  }
]
\`\`\`

### POST /api/receipts
Generate new receipt.

**Request Body**:
\`\`\`json
{
  "orderId": "o10",
  "paymentId": "p10",
  "issuedBy": "6"
}
\`\`\`

**Response** (201 Created):
\`\`\`json
{
  "id": "r10",
  "receiptNumber": "RCP-010",
  "orderId": "o10",
  "order": {...},
  "payment": {...},
  "issuedBy": "6",
  "issuedAt": "2025-01-30T11:35:00Z"
}
\`\`\`

---

## Reports

### GET /api/reports
Get comprehensive reports.

**Query Parameters**:
- `startDate` (required): Start date (ISO 8601)
- `endDate` (required): End date (ISO 8601)
- `type` (optional): Report type (sales, inventory, staff-performance)

**Response** (200 OK):
\`\`\`json
{
  "period": {
    "startDate": "2025-01-01",
    "endDate": "2025-01-30"
  },
  "sales": {
    "totalSales": 1250000,
    "totalOrders": 850,
    "averageOrderValue": 1470.59
  },
  "topSellingItems": [
    {
      "menuItemId": "m1",
      "name": "Ugali & Beef Stew",
      "quantitySold": 120,
      "revenue": 54000
    }
  ],
  "staffPerformance": [
    {
      "userId": "4",
      "name": "James Waiter",
      "ordersServed": 145,
      "totalSales": 215000
    }
  ]
}
\`\`\`

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
\`\`\`json
{
  "error": "Invalid request data",
  "details": {
    "field": "email",
    "message": "Invalid email format"
  }
}
\`\`\`

### 401 Unauthorized
\`\`\`json
{
  "error": "Authentication required"
}
\`\`\`

### 403 Forbidden
\`\`\`json
{
  "error": "Insufficient permissions"
}
\`\`\`

### 404 Not Found
\`\`\`json
{
  "error": "Resource not found"
}
\`\`\`

### 500 Internal Server Error
\`\`\`json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred"
}
\`\`\`

---

## Mock Data Locations

All mock data files are located in the `lib/mock-data/` directory. When integrating with Django, you can safely remove these files:

### Mock Data Files to Remove:
\`\`\`
lib/mock-data/
├── dashboard.ts          # Dashboard statistics and charts data
├── guests.ts            # Guest records
├── inventory.ts         # Inventory items
├── menu.ts              # Menu items
├── notifications.ts     # Notification samples
├── orders.ts            # Order records
├── reports.ts           # Report data
├── service-requests.ts  # Service request records
├── tables.ts            # Table configurations
├── terms-of-service.ts  # Terms of service content
└── users.ts             # User accounts and credentials
\`\`\`

### Steps to Remove Mock Data:
1. Delete the entire `lib/mock-data/` directory
2. Update `lib/api/data-service.ts` to use real API calls instead of mock data
3. Remove all mock data imports from `data-service.ts`
4. Uncomment the `apiCall` function implementations
5. Set the `NEXT_PUBLIC_API_URL` environment variable

---

## Integration Checklist

- [ ] Set up Django REST API with all endpoints
- [ ] Configure CORS to allow requests from Next.js frontend
- [ ] Implement JWT authentication in Django
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable
- [ ] Update `lib/api/data-service.ts` to use real API calls
- [ ] Remove `lib/mock-data/` directory
- [ ] Test all API endpoints
- [ ] Implement error handling and loading states
- [ ] Add request/response logging for debugging
- [ ] Set up production environment variables

---

## Notes

- All dates should be in ISO 8601 format
- All monetary values are in Kenyan Shillings (KES)
- Phone numbers should include country code (+254 for Kenya)
- File uploads (images) should use multipart/form-data
- Implement rate limiting on Django backend
- Use pagination for large datasets (add `page` and `limit` query parameters)
- Implement proper validation on both frontend and backend
- Use HTTPS in production
