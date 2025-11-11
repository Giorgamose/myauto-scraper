# MyAuto Platform - Architecture Diagrams

## 🏗️ Overall System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                                  │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │              React Frontend (Vercel)                         │   │
│  │  yourdomain.io                                              │   │
│  │                                                              │   │
│  │  ┌─────────────────┐  ┌──────────────┐  ┌──────────────┐  │   │
│  │  │ Landing Page    │  │ Register     │  │ Payment      │  │   │
│  │  │                 │  │ Page         │  │ Page         │  │   │
│  │  └─────────────────┘  └──────────────┘  └──────────────┘  │   │
│  │           ↓                  ↓                  ↓           │   │
│  │  ┌──────────────────────────────────────────────────────┐  │   │
│  │  │         React Router + Auth Context                  │  │   │
│  │  └──────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                   HTTPS/REST API Calls
                               │
┌──────────────────────────────┼───────────────────────────────────────┐
│                        API LAYER                                      │
│                                                                       │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │           FastAPI Backend (Railway)                         │   │
│  │  api.yourdomain.io                                          │   │
│  │                                                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │   │
│  │  │ Auth Service │  │ Payment      │  │ Subscription │     │   │
│  │  │              │  │ Service      │  │ Service      │     │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘     │   │
│  │        ↓                  ↓                  ↓              │   │
│  │  OAuth2 Google/FB    Flitt Gateway    PostgreSQL Database  │   │
│  └──────────────────────────────────────────────────────────────┘  │
│                              ↓                                       │
└──────────────────────────────┼───────────────────────────────────────┘
                               │
                        External Services
                               │
           ┌───────────────────┼───────────────────┐
           ↓                   ↓                   ↓
      ┌─────────┐         ┌──────────┐      ┌──────────────┐
      │ Google  │         │ Facebook │      │ Flitt        │
      │ OAuth   │         │ OAuth    │      │ Payments     │
      │ Provider│         │ Provider │      │ Gateway      │
      └─────────┘         └──────────┘      └──────────────┘
           ↓                   ↓                   ↓
      ┌──────────────────────────────────────────────┐
      │      PostgreSQL Database (Supabase)         │
      │  users | subscriptions | payments | criteria│
      └──────────────────────────────────────────────┘
                               │
           ┌───────────────────┼───────────────────┐
           ↓                   ↓                   ↓
      ┌──────────┐      ┌──────────────┐  ┌──────────┐
      │ Telegram │      │ Email Service│  │ SMS Notif│
      │ Bot      │      │              │  │          │
      └──────────┘      └──────────────┘  └──────────┘
```

---

## 🔄 User Authentication Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTHENTICATION FLOW                           │
└─────────────────────────────────────────────────────────────────┘

        ┌─────────────────┐
        │ User on Landing │
        │     Page        │
        └────────┬────────┘
                 │
                 │ Click "Sign In with Google"
                 ↓
        ┌────────────────────┐
        │  Frontend detects  │
        │  click, opens      │
        │ Google OAuth dialog│
        └────────┬───────────┘
                 │
                 │ User logs in with Google
                 ↓
        ┌────────────────────┐
        │  Google returns    │
        │  auth token        │
        └────────┬───────────┘
                 │
                 │ Frontend sends token to
                 │ /auth/google-callback
                 ↓
        ┌────────────────────┐
        │  Backend validates │
        │  token with Google │
        └────────┬───────────┘
                 │
                 │ Token valid?
        ┌────────┴────────┐
        │ (YES)           │
        ↓                 ↓ (NO)
    ┌────────┐        ┌────────┐
    │ Create │        │ Return │
    │ User   │        │ Error  │
    │ Record │        └────────┘
    └───┬────┘
        │
        │ Generate JWT
        ↓
    ┌────────────────────┐
    │ Return to Frontend: │
    │ { access_token,    │
    │   user }           │
    └────────┬───────────┘
             │
             │ Save token to localStorage
             │ Set user in Context
             ↓
    ┌────────────────────┐
    │  User authenticated│
    │ Redirect to        │
    │ /subscription page │
    └────────────────────┘
```

---

## 💳 Payment Flow

```
┌────────────────────────────────────────────────────────────────────┐
│                      PAYMENT FLOW                                   │
└────────────────────────────────────────────────────────────────────┘

User selects subscription plan
         │
         │ Clicks "Proceed to Payment"
         ↓
┌──────────────────────────┐
│ Payment Page Displays:   │
│ - Order Summary          │
│ - Plan Details           │
│ - Billing Form           │
└────────────┬─────────────┘
             │
             │ User fills form & clicks "Pay"
             ↓
┌──────────────────────────┐
│ Frontend validates form  │
└────────────┬─────────────┘
             │
             │ POST /subscriptions
             │   { user_id, plan_id }
             ↓
┌──────────────────────────┐
│ Backend creates          │
│ Subscription record      │
│ Returns subscription_id  │
└────────────┬─────────────┘
             │
             │ POST /payments/initiate
             │   { subscription_id,
             │     amount, currency }
             ↓
┌──────────────────────────────┐
│ Backend calls Flitt API:     │
│ Create Payment Order         │
│ Returns order_id & redirect  │
└────────────┬─────────────────┘
             │
             │ Frontend redirects to Flitt
             │ window.location.href = redirect_url
             ↓
┌──────────────────────────┐
│ Flitt Payment Gateway    │
│ User enters card details │
│ Completes payment        │
└────────────┬─────────────┘
             │
             │ Flitt sends webhook to backend
             │ POST /payments/webhook
             │   { order_id, status }
             ↓
┌──────────────────────────┐
│ Backend updates          │
│ Payment Status           │
│ Activates Subscription   │
└────────────┬─────────────┘
             │
             │ Generates Telegram QR Code
             ↓
┌──────────────────────────┐
│ Frontend receives        │
│ Payment Success response │
│ Shows QR code to user    │
└────────────┬─────────────┘
             │
             │ User scans QR with Telegram
             ↓
┌──────────────────────────┐
│ User joins Telegram      │
│ Bot starts sending       │
│ listings based on        │
│ search criteria          │
└────────────────────────┘
```

---

## 📊 Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                  FRONTEND DATA FLOW                              │
└─────────────────────────────────────────────────────────────────┘

App.tsx (Router)
    │
    ├─→ Header Component
    │       │
    │       ├─→ useAuth() hook
    │       └─→ Check if user logged in
    │
    ├─→ LandingPage
    │       │
    │       └─→ Static content (no API)
    │
    ├─→ RegisterPage
    │       │
    │       ├─→ useAuth() hook
    │       ├─→ Google/Facebook SDK
    │       └─→ POST /auth/{provider}-callback
    │
    └─→ PaymentPage
            │
            ├─→ useAuth() hook (get user)
            ├─→ useEffect: GET /subscriptions/plans
            ├─→ useEffect: GET /subscriptions/{user_id}
            └─→ Form submit:
                    1. POST /subscriptions
                    2. POST /payments/initiate
                    3. Redirect to Flitt


┌─────────────────────────────────────────────────────────────────┐
│                  BACKEND DATA FLOW                               │
└─────────────────────────────────────────────────────────────────┘

Incoming Request
    ↓
Authentication Middleware
    ├─→ Validate JWT token
    ├─→ Get user from token
    └─→ Attach to request
    ↓
Route Handler
    ├─→ Auth routes
    │   ├─→ POST /auth/google-callback
    │   │   1. Validate token with Google
    │   │   2. Check if user exists
    │   │   3. Create or update user
    │   │   4. Generate JWT
    │   │   5. Return user + token
    │   │
    │   └─→ POST /auth/facebook-callback
    │       (same as Google)
    │
    ├─→ Subscription routes
    │   ├─→ GET /subscriptions/plans
    │   │   Return list of plans
    │   │
    │   ├─→ POST /subscriptions
    │   │   1. Validate user
    │   │   2. Create subscription
    │   │   3. Save to database
    │   │   4. Return subscription
    │   │
    │   └─→ GET /subscriptions/{user_id}
    │       Query database, return user's subscriptions
    │
    └─→ Payment routes
        ├─→ POST /payments/initiate
        │   1. Get subscription
        │   2. Call Flitt API
        │   3. Return redirect URL
        │
        ├─→ GET /payments/status/{order_id}
        │   Query database, return payment status
        │
        └─→ POST /payments/webhook (from Flitt)
            1. Validate signature
            2. Update payment status
            3. If success: activate subscription
            4. Generate Telegram QR
            5. Send notifications

Database Operations
    ↓
Return Response to Frontend
```

---

## 🔐 Security Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                    SECURITY LAYERS                                │
└──────────────────────────────────────────────────────────────────┘

Frontend Security
├─→ Environment variables (no secrets in code)
├─→ OAuth tokens stored in localStorage
├─→ Secure HTTPS connections
├─→ Input validation on forms
├─→ XSS protection (React sanitizes)
└─→ CSRF tokens (if using forms)

Backend Security
├─→ JWT token validation
├─→ Rate limiting on API routes
├─→ SQL injection prevention (ORM)
├─→ Password hashing (bcrypt)
├─→ CORS configuration
├─→ Request logging
├─→ Error handling (no sensitive data)
└─→ Database encryption

Payment Security
├─→ PCI-DSS compliance (Flitt)
├─→ No card data stored locally
├─→ Webhook signature validation
├─→ SSL/TLS encryption
└─→ OAuth security (no direct credentials)

OAuth Security
├─→ Authorization code flow
├─→ State parameter validation
├─→ Token expiration handling
├─→ Refresh token rotation
└─→ Scope limitation

Database Security
├─→ Encrypted connections
├─→ Access control lists
├─→ Regular backups
├─→ Encryption at rest
└─→ User data isolation
```

---

## 🌐 Deployment Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                DEPLOYMENT ARCHITECTURE                            │
└──────────────────────────────────────────────────────────────────┘

User's Device
    │ (Browser)
    │
    ├─→ HTTPS (SSL/TLS)
    │
    ↓
┌─────────────────────────────────────────────┐
│         Vercel Edge Network                 │
│  (Frontend Hosting)                         │
│  yourdomain.io                              │
│                                             │
│  - Static files (HTML, CSS, JS)            │
│  - CDN distributed globally                │
│  - Auto-scales for traffic                 │
│  - Free: 100GB/month bandwidth             │
└──────────────┬──────────────────────────────┘
               │
        HTTPS/REST API
               │
               ↓
┌─────────────────────────────────────────────┐
│         Railway (Backend Hosting)            │
│  api.yourdomain.io                          │
│                                             │
│  - FastAPI application                     │
│  - PostgreSQL connection                   │
│  - Environment variables                   │
│  - Automatic deployments                   │
│  - Free: $5/month credit                   │
└──────────────┬──────────────────────────────┘
               │
        Database Connection
               │
               ↓
┌─────────────────────────────────────────────┐
│       Supabase (Database)                    │
│       PostgreSQL + Auth                      │
│                                             │
│  - All application data                    │
│  - User credentials (hashed)               │
│  - Subscriptions & payments                │
│  - Search criteria                         │
│  - Free: 500MB, 50k rows                   │
└──────────────┬──────────────────────────────┘
               │
     External Service Calls
               │
      ┌────────┼────────┐
      ↓        ↓        ↓
   Google   Facebook  Flitt
   OAuth    OAuth    Payments
```

---

## 📱 Mobile Responsive Design

```
┌────────────────────────────────────────────────────────────────┐
│          RESPONSIVE BREAKPOINTS                                 │
└────────────────────────────────────────────────────────────────┘

Mobile (< 640px)
├─→ Stack layout (vertical)
├─→ Full-width elements
├─→ Hamburger menu
└─→ Touch-friendly buttons

Tablet (640px - 1024px)
├─→ 2-column layout
├─→ Optimized spacing
└─→ Visible menu

Desktop (> 1024px)
├─→ Multi-column layout
├─→ Full features visible
├─→ Hover effects
└─→ Side navigation

All Views
├─→ Header responsive
├─→ Forms mobile-friendly
├─→ Images optimized
└─→ Touch targets 48px+
```

---

## 🔄 Component Hierarchy

```
App
├─→ AuthProvider (Context)
│   └─→ State: user, isLoading, error
│       Methods: loginWithGoogle, loginWithFacebook, logout
│
├─→ Header
│   ├─→ useAuth() → access user
│   └─→ Navigation links
│
└─→ Routes
    ├─→ / → LandingPage
    │   ├─→ Hero Section
    │   ├─→ Features Section
    │   ├─→ Pricing Section
    │   ├─→ CTA Section
    │   └─→ Footer
    │
    ├─→ /register → RegisterPage
    │   ├─→ Google OAuth Button
    │   ├─→ Facebook OAuth Button
    │   ├─→ Email Form
    │   ├─→ Error Alert
    │   └─→ Security Info
    │
    └─→ /subscription → PaymentPage
        ├─→ Plan Selection Cards
        ├─→ Order Summary
        ├─→ Billing Form
        ├─→ Payment Method Info
        └─→ Security Info
```

---

## 🔗 API Endpoint Map

```
Frontend Routes          API Endpoints              Backend Handler
─────────────────────────────────────────────────────────────────

/                       (No API calls)             Static content
                        GET /subscriptions/plans   Fetch plans

/register               POST /auth/google-callback OAuth handler
                        POST /auth/facebook-callback OAuth handler
                        GET /auth/me               Get current user

/subscription           GET /subscriptions/plans   Fetch plans
                        POST /subscriptions        Create subscription
                        GET /subscriptions/{id}    Get user subscription
                        POST /payments/initiate    Create payment order
                        GET /payments/status/{id}  Check payment status
```

---

## 📊 Database Schema Relationships

```
┌──────────────────────────────────────────────────────────────┐
│                  DATABASE SCHEMA                              │
└──────────────────────────────────────────────────────────────┘

users
├─ id (UUID, PK)
├─ email (VARCHAR)
├─ oauth_provider (ENUM: google, facebook)
├─ oauth_id (VARCHAR)
├─ name (VARCHAR)
├─ picture (VARCHAR)
├─ created_at (TIMESTAMP)
└─ updated_at (TIMESTAMP)
        │
        ├─→ subscriptions (1:N)
        ├─→ search_criteria (1:N)
        └─→ telegram_users (1:1)

subscriptions
├─ id (UUID, PK)
├─ user_id (UUID, FK)
├─ plan_id (UUID, FK)
├─ status (ENUM)
├─ start_date (TIMESTAMP)
├─ end_date (TIMESTAMP)
├─ auto_renew (BOOLEAN)
└─ created_at (TIMESTAMP)
        │
        └─→ payments (1:N)

plans
├─ id (UUID, PK)
├─ name (VARCHAR)
├─ price (DECIMAL)
├─ duration_months (INT)
└─ features (JSON/ARRAY)

payments
├─ id (UUID, PK)
├─ subscription_id (UUID, FK)
├─ user_id (UUID, FK)
├─ amount (DECIMAL)
├─ currency (VARCHAR)
├─ flitt_order_id (VARCHAR)
├─ status (ENUM)
└─ created_at (TIMESTAMP)

search_criteria
├─ id (UUID, PK)
├─ user_id (UUID, FK)
├─ filters (JSON)
├─ telegram_channel_id (VARCHAR)
├─ is_active (BOOLEAN)
└─ created_at (TIMESTAMP)

telegram_users
├─ id (UUID, PK)
├─ user_id (UUID, FK)
├─ telegram_user_id (INT)
├─ telegram_channel_id (VARCHAR)
└─ created_at (TIMESTAMP)
```

---

## 🚀 Deployment Pipeline

```
┌──────────────────────────────────────────────────────────────┐
│              CI/CD DEPLOYMENT FLOW                            │
└──────────────────────────────────────────────────────────────┘

Developer pushes code to GitHub
    ↓
GitHub detects new commit
    ↓
Frontend
├─→ Vercel webhook triggered
├─→ Build: npm run build
├─→ Test: Run linter
├─→ Deploy to Vercel CDN
└─→ Custom domain updated

Backend (Manual for now)
├─→ Developer triggers deployment
├─→ Railway pulls latest code
├─→ Build: pip install requirements
├─→ Run migrations
├─→ Deploy application
└─→ API updated at api.yourdomain.io

Database (Manual)
├─→ Supabase PostgreSQL
├─→ Automatic backups
└─→ Zero downtime migrations

Result
├─→ Frontend live at yourdomain.io
├─→ Backend API live at api.yourdomain.io
└─→ All services synced
```

---

**Last Updated**: November 2024
**Version**: 1.0
