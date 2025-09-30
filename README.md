# Maria Havens POS - Frontend System

A comprehensive Hotel & Restaurant Point of Sale system built with Next.js, TypeScript, and TailwindCSS.

## Features

- **Multi-Role Authentication**: Admin, Manager, Receptionist, Waiter, Kitchen Staff, Cashier, Guest
- **Dashboard**: Real-time KPIs, sales charts, and analytics
- **Order Management**: Create, edit, track orders (dine-in, takeaway, room service)
- **Table Management**: View availability, assign waiters, reservations
- **Menu Management**: Categories, add/edit items, search and filters
- **Receipts & Payments**: Generate, print, M-Pesa integration-ready
- **Inventory**: Stock tracking, low-stock alerts, waste tracking
- **Reports**: Sales reports, staff performance, CSV/PDF export
- **Hotel Features**: Guest check-in/out, room service orders, service requests
- **Notifications**: Real-time notifications for orders, service requests, and alerts
- **Guest Portal**: Dedicated dashboard for guests to order food and request services
- **PWA Support**: Install as mobile/desktop app

## Tech Stack

- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: TailwindCSS v4
- **State Management**: Zustand
- **Charts**: Recharts
- **Icons**: Lucide React
- **Printing**: react-to-print

## Getting Started

### Installation

\`\`\`bash
npm install
\`\`\`

### Development

\`\`\`bash
npm run dev
\`\`\`

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

\`\`\`bash
npm run build
npm start
\`\`\`

## Mock Data & Django Integration

The system currently uses mock data for demonstration. All data access is abstracted through the service layer in `lib/api/data-service.ts`.

### Mock Login Credentials

- **Admin**: admin@mariahavens.com / admin123
- **Manager**: manager@mariahavens.com / manager123
- **Receptionist**: reception@mariahavens.com / reception123
- **Waiter**: waiter1@mariahavens.com / waiter123
- **Kitchen**: kitchen@mariahavens.com / kitchen123
- **Cashier**: cashier@mariahavens.com / cashier123
- **Guest**: guest@mariahavens.com / guest123 (Room: 101)

### Mock Data Files Location

All mock data is stored in the `lib/mock-data/` directory. **Remove this entire directory when integrating with Django backend.**

\`\`\`
lib/mock-data/
├── dashboard.ts          # Dashboard statistics and charts data
├── guests.ts            # Guest records (check-in/out data)
├── inventory.ts         # Inventory items and stock levels
├── menu.ts              # Menu items with categories
├── notifications.ts     # Sample notifications
├── orders.ts            # Order records
├── reports.ts           # Report data
├── service-requests.ts  # Guest service requests
├── tables.ts            # Table configurations
├── terms-of-service.ts  # Terms of service content for guests
└── users.ts             # User accounts and credentials
\`\`\`

### Integrating with Django Backend

**Complete API documentation is available in `DJANGO_API_DOCUMENTATION.md`**

#### Quick Integration Steps:

1. **Set Environment Variable**:
   \`\`\`bash
   # In .env.local
   NEXT_PUBLIC_API_URL=https://your-django-api.com/api
   \`\`\`

2. **Remove Mock Data**:
   \`\`\`bash
   rm -rf lib/mock-data/
   \`\`\`

3. **Update Data Service** (`lib/api/data-service.ts`):
   - Uncomment the `fetch` implementation in the `apiCall` function
   - Remove all mock data imports
   - Remove mock data returns from service functions
   - Add JWT token handling

4. **Django API Requirements**:
   - JWT authentication
   - CORS enabled for your frontend domain
   - All endpoints documented in `DJANGO_API_DOCUMENTATION.md`

#### Key Django Endpoints:

\`\`\`
Authentication:
POST   /api/auth/login          # Login with email, password, roomNumber (for guests)
POST   /api/auth/logout
GET    /api/auth/me

Users & Staff:
GET    /api/users
POST   /api/users
PATCH  /api/users/:id
DELETE /api/users/:id

Menu:
GET    /api/menu
POST   /api/menu
PATCH  /api/menu/:id
DELETE /api/menu/:id

Orders:
GET    /api/orders              # Supports filtering by status, type, roomNumber
POST   /api/orders
PATCH  /api/orders/:id

Tables:
GET    /api/tables
PATCH  /api/tables/:id

Inventory:
GET    /api/inventory
GET    /api/inventory/low-stock
PATCH  /api/inventory/:id
POST   /api/inventory/waste

Guests:
GET    /api/guests
POST   /api/guests/check-in
POST   /api/guests/:id/check-out
PATCH  /api/guests/:id

Service Requests:
GET    /api/service-requests    # Filter by guestId, status, priority
POST   /api/service-requests
PATCH  /api/service-requests/:id

Dashboard:
GET    /api/dashboard/stats
GET    /api/dashboard/sales?days=7
GET    /api/dashboard/category-sales

Payments:
GET    /api/payments
POST   /api/payments
POST   /api/payments/:id/refund

Receipts:
GET    /api/receipts
POST   /api/receipts

Reports:
GET    /api/reports?startDate=...&endDate=...
\`\`\`

For complete request/response formats, authentication details, and error handling, see **`DJANGO_API_DOCUMENTATION.md`**.

## Project Structure

\`\`\`
├── app/                    # Next.js app directory
│   ├── dashboard/         # Staff dashboard
│   ├── guest-dashboard/   # Guest portal
│   ├── notifications/     # Notifications page
│   ├── orders/           # Order management
│   ├── tables/           # Table management
│   ├── menu/             # Menu management
│   ├── inventory/        # Inventory tracking
│   ├── guests/           # Guest management
│   ├── staff/            # Staff management
│   ├── receipts/         # Receipt generation
│   ├── payments/         # Payment processing
│   ├── reports/          # Analytics & reports
│   ├── settings/         # System settings
│   ├── layout.tsx        # Root layout with fonts
│   ├── page.tsx          # Landing/login page
│   └── globals.css       # Global styles with design tokens
├── components/
│   ├── auth/             # Authentication components
│   ├── dashboard/        # Dashboard widgets
│   ├── guest/            # Guest-specific components
│   ├── layout/           # Layout components (sidebar, header)
│   ├── orders/           # Order components
│   └── ui/               # shadcn/ui components
├── lib/
│   ├── types.ts          # TypeScript type definitions
│   ├── api/
│   │   └── data-service.ts  # Data access layer (API abstraction)
│   ├── mock-data/        # Mock data (REMOVE when integrating Django)
│   ├── store/            # Zustand stores
│   │   └── auth-store.ts
│   └── utils/            # Utility functions
│       └── format.ts
├── public/
│   └── manifest.json     # PWA manifest
├── DJANGO_API_DOCUMENTATION.md  # Complete API specs for Django
└── README.md
\`\`\`

## Design System

### Colors
- **Primary**: Cyan-800 (#164e63)
- **Secondary/Accent**: Orange (#f97316)
- **Neutrals**: White, Cyan-50, Slate-600

### Typography
- **Headings**: Work Sans (Bold)
- **Body**: Work Sans (Regular)

### Dark Mode
Full dark mode support with automatic theme switching.

## Guest Features

### Guest Login
Guests must provide their room number when logging in. The system validates the room number against checked-in guests.

### Guest Dashboard
- Place food orders (room service)
- Request services (housekeeping, maintenance, concierge)
- View order history
- Track service request status
- Accept terms of service on first login

### Service Requests
Guest service requests automatically appear in the receptionist/manager dashboard for immediate action.

## PWA Features

### Installation
The app can be installed on mobile and desktop devices:
- **Mobile**: Tap "Add to Home Screen" in your browser menu
- **Desktop**: Click the install icon in the address bar

### Offline Support
The service worker caches essential assets for offline functionality. Users can view cached data even without internet connection.

### Features
- Installable on all devices
- Offline data access
- Push notifications ready
- App-like experience

## Development Notes

### Adding New Features
1. Add types to `lib/types.ts`
2. Create mock data in `lib/mock-data/` (for development)
3. Add service functions to `lib/api/data-service.ts`
4. Build UI components
5. Add routes in `app/` directory

### Role-Based Access
Use the `ProtectedRoute` component to restrict access:
\`\`\`tsx
<ProtectedRoute allowedRoles={['admin', 'manager']}>
  <YourComponent />
</ProtectedRoute>
\`\`\`

### State Management
The app uses Zustand for global state. Auth state is persisted to localStorage automatically.

## Troubleshooting

### Environment Variables
If you see API errors, ensure `NEXT_PUBLIC_API_URL` is set in your environment variables in Project Settings (gear icon in top right).

### Guest Login Issues
- Ensure the guest has been checked in via the Guests page
- Verify the room number matches the guest record
- Check that the guest status is "checked-in"

### Service Requests Not Showing
Service requests appear in the dashboard for Admin, Manager, and Receptionist roles only.

### PWA Not Installing
- Ensure you're using HTTPS (required for PWA)
- Check that manifest.json is accessible
- Verify service worker is registered

### Mock Data Not Loading
Check browser console for errors. Mock data is loaded from `lib/mock-data/` directory.

## Backend Integration Checklist

- [ ] Set up Django REST API with JWT authentication
- [ ] Configure CORS for your frontend domain
- [ ] Implement all endpoints from `DJANGO_API_DOCUMENTATION.md`
- [ ] Set `NEXT_PUBLIC_API_URL` environment variable
- [ ] Update `lib/api/data-service.ts` to use real API calls
- [ ] Remove `lib/mock-data/` directory
- [ ] Test authentication flow
- [ ] Test all CRUD operations
- [ ] Implement error handling
- [ ] Set up production environment

## License

Proprietary - Maria Havens Hotel & Restaurant
