# 👤 User Flows & Interactions

## 🎯 Happy Path Flow (Complete User Journey)

```
┌────────────────────────────────────────────────────────────────────┐
│                   COMPLETE USER JOURNEY                            │
└────────────────────────────────────────────────────────────────────┘

1. DISCOVERY
   ↓
   User visits yourdomain.io
   Landing Page loads
   - Sees service features
   - Reviews pricing plans
   - Reads benefits
   ↓
   User impressed, clicks "Sign Up Now"

2. REGISTRATION
   ↓
   Redirected to /register
   RegisterPage loads
   User has 3 options:

   ├─ Option A: Google OAuth
   │  ├─ Clicks "Sign in with Google"
   │  ├─ Google login dialog opens
   │  ├─ User logs in with Google
   │  ├─ Returns to app authenticated
   │  └─ Stored in context + localStorage
   │
   ├─ Option B: Facebook OAuth
   │  ├─ Clicks "Sign in with Facebook"
   │  ├─ Facebook login dialog opens
   │  ├─ User logs in with Facebook
   │  ├─ Returns to app authenticated
   │  └─ Stored in context + localStorage
   │
   └─ Option C: Email Signup
      ├─ Fills email & password
      ├─ Clicks "Create Account"
      ├─ Backend validates & creates user
      └─ Returns JWT token

3. SUBSCRIPTION SELECTION
   ↓
   Redirected to /subscription
   PaymentPage loads
   Displays 3 subscription plans:
   - Starter (₾99/month)
   - Professional (₾299/month)  ← Most popular
   - Enterprise (₾999/month)

   User examines plans:
   - Reads features
   - Compares pricing
   - Reads FAQs
   ↓
   User selects Professional plan
   Clicks "Select Plan"

4. PAYMENT DETAILS
   ↓
   PaymentPage shows "payment-details" step
   Order summary displays:
   - Plan name: Professional
   - Duration: 1 month
   - Amount: ₾299
   - Tax: ₾0
   - Total: ₾299
   ↓
   User fills billing form:
   - First Name
   - Last Name
   - Email (pre-filled)
   ↓
   User reads & checks terms:
   ☑ Auto-renewal terms
   ☑ Terms of Service
   ☑ Privacy Policy
   ↓
   User clicks "Proceed to Payment (₾299)"

5. PAYMENT PROCESSING
   ↓
   Frontend shows loading state
   Steps happen:
   1. Frontend: POST /subscriptions
      → Creates subscription record
   2. Frontend: POST /payments/initiate
      → Initiates Flitt payment
   3. Backend: Returns redirect_url
   4. Frontend: Redirects to Flitt gateway
   ↓
   User on Flitt payment page

6. FLITT PAYMENT GATEWAY
   ↓
   Flitt securely displays:
   - Order amount (₾299)
   - Payment method options
   ↓
   User enters card details:
   - Card number
   - Expiry date
   - CVV
   ↓
   User clicks "Pay ₾299"
   Flitt processes payment
   ↓
   Payment successful!

7. PAYMENT CONFIRMATION
   ↓
   Flitt sends webhook to backend
   Backend:
   - Validates webhook signature
   - Updates payment status: completed
   - Activates subscription
   - Generates Telegram QR code
   ↓
   Frontend notified of success
   Shows confirmation page
   - ✅ Payment successful
   - 📱 Telegram QR code
   - 📋 Subscription details

8. TELEGRAM SETUP
   ↓
   User scans QR code with Telegram
   Bot adds user to channel
   ↓
   Bot sends welcome message:
   "✅ Subscription activated!
    Your search criteria are active.
    Start receiving listings now!"

9. ACTIVE SUBSCRIPTION
   ↓
   User receives listings via Telegram:
   - Based on search criteria
   - Real-time notifications
   - Can manage via bot commands
   ↓
   User can:
   - /add criteria
   - /list criteria
   - /pause subscription
   - /resume subscription
   - /cancel subscription

10. FUTURE INTERACTIONS
    ↓
    User logs in again:
    - Click Register again
    - OAuth remembers them
    - Can view subscription status
    - Can upgrade/downgrade plan
    - Can manage search criteria
```

---

## 📄 Landing Page Flow

```
┌─────────────────────────────────────────┐
│         LANDING PAGE (/​)                 │
└─────────────────────────────────────────┘

User visits yourdomain.io
    │
    ├─→ Page loads (no authentication required)
    ├─→ Shows Hero section
    │   ├─→ Headline
    │   ├─→ Description
    │   └─→ CTA buttons
    │       ├─→ "Start Free Trial" → Go to /register
    │       └─→ "Watch Demo" → Modal/popup
    │
    ├─→ User scrolls down
    │   ├─→ Features Section (6 cards)
    │   ├─→ Pricing Section (3 plans)
    │   ├─→ CTA Section (another sign up button)
    │   └─→ Footer (links)
    │
    └─→ User chooses action:
        ├─→ Click "Sign Up" → Redirect to /register
        ├─→ Click pricing → Scroll to pricing section
        └─→ Click footer links → External/internal pages

Page Interactions
├─→ No data fetching (static content)
├─→ No authentication required
├─→ Mobile responsive
├─→ Smooth scrolling
└─→ Hover effects on cards & buttons
```

---

## 👤 Registration Page Flow

```
┌────────────────────────────────────┐
│    REGISTRATION PAGE (/register)    │
└────────────────────────────────────┘

User arrives at page
    │
    ├─→ Page loads
    │   ├─→ Check if user already logged in
    │   │   ├─→ If yes: Redirect to /subscription
    │   │   └─→ If no: Show registration form
    │   ├─→ Load OAuth SDK (Google & Facebook)
    │   └─→ Disable buttons if SDK not loaded
    │
    └─→ User sees 3 options:

OPTION A: Google OAuth
├─→ User clicks "Sign in with Google"
├─→ Google SDK opens login dialog
├─→ User enters Google credentials
├─→ User grants permission to app
├─→ Google returns credential token
├─→ Frontend sends token to backend
├─→ Backend validates & creates user
├─→ Backend returns JWT + user data
├─→ Frontend saves token to localStorage
├─→ Frontend saves user to Context
├─→ Frontend redirects to /subscription
└─→ Component unmounts

OPTION B: Facebook OAuth
├─→ User clicks "Sign in with Facebook"
├─→ Facebook SDK opens login dialog
├─→ User enters Facebook credentials
├─→ User grants permission to app
├─→ Facebook returns access token
├─→ Frontend sends token to backend
├─→ Backend validates & creates user
├─→ Backend returns JWT + user data
├─→ Frontend saves token to localStorage
├─→ Frontend saves user to Context
├─→ Frontend redirects to /subscription
└─→ Component unmounts

OPTION C: Email & Password
├─→ User fills "Email Address" field
├─→ User fills "Password" field
├─→ User clicks "Create Account"
├─→ Frontend validates inputs
├─→ Frontend sends to backend
├─→ Backend creates user account
├─→ Backend hashes password
├─→ Backend returns JWT + user data
├─→ Frontend saves token to localStorage
├─→ Frontend saves user to Context
├─→ Frontend redirects to /subscription
└─→ Component unmounts

Error Handling
├─→ If OAuth fails:
│   ├─→ Show error alert
│   ├─→ Display error message
│   └─→ Keep form open for retry
│
└─→ If email signup fails:
    ├─→ Show error alert
    ├─→ Display validation errors
    └─→ Keep form open for retry

Security Info
└─→ Always shown:
    ├─→ SSL encryption badge
    ├─→ Data privacy info
    └─→ GDPR compliance note
```

---

## 💳 Payment Page Flow

```
┌──────────────────────────────────┐
│   PAYMENT PAGE (/subscription)    │
└──────────────────────────────────┘

Page Load
├─→ Check if user authenticated
│   ├─→ If no: Redirect to /register
│   └─→ If yes: Continue
├─→ Set paymentStep = 'plan-selection'
├─→ Fetch subscription plans from API
└─→ Display loading skeleton

STEP 1: Plan Selection
├─→ Display 3 plan cards:
│   ├─→ Starter (₾99)
│   │   ├─→ 5 features
│   │   └─→ "Get Started" button
│   │
│   ├─→ Professional (₾299) [Most Popular]
│   │   ├─→ 4 features
│   │   └─→ "Start Free Trial" button
│   │
│   └─→ Enterprise (₾999)
│       ├─→ 4 features
│       └─→ "Contact Sales" button
│
├─→ User examines plans
└─→ User clicks plan → Select plan & go to step 2

STEP 2: Payment Details
├─→ Set paymentStep = 'payment-details'
├─→ Display order summary:
│   ├─→ Plan name
│   ├─→ Duration
│   ├─→ Subtotal
│   ├─→ Tax
│   └─→ Total
│
├─→ Display Flitt payment gateway badge
├─→ Show billing form:
│   ├─→ First name (pre-filled)
│   ├─→ Last name (pre-filled)
│   ├─→ Email (disabled, pre-filled)
│   └─→ Auto-renewal checkbox
│
├─→ Show terms checkboxes:
│   ├─→ Auto-renewal agreement
│   └─→ Terms of Service & Privacy
│
├─→ Show buttons:
│   ├─→ "Back" button (go to step 1)
│   └─→ "Proceed to Payment (₾299)" button
│
├─→ User fills/reviews form
└─→ User clicks "Proceed to Payment"

STEP 3: Processing
├─→ Set paymentStep = 'processing'
├─→ Show loading spinner
├─→ Frontend actions:
│   ├─→ POST /subscriptions
│   │   └─→ Creates subscription record
│   │
│   ├─→ POST /payments/initiate
│   │   └─→ Creates Flitt payment order
│   │
│   └─→ Receive redirect_url
│
├─→ Show "Redirecting to payment gateway..."
└─→ Redirect to Flitt: window.location.href = redirect_url

FLITT GATEWAY (External)
├─→ User enters card details
├─→ User completes payment
└─→ Flitt sends confirmation webhook to backend

BACKEND Processing
├─→ Validates webhook signature
├─→ Updates payment status: completed
├─→ Activates subscription
├─→ Generates Telegram QR code
└─→ Sends confirmation email

STEP 4: Success (Optional)
├─→ Receive success webhook from backend
├─→ Set paymentStep = 'success'
├─→ Display success message:
│   ├─→ ✅ Payment successful
│   ├─→ 📱 Telegram QR code
│   └─→ 📋 Next steps
│
└─→ Show "Go to Dashboard" button

Error Handling
├─→ If subscription creation fails:
│   └─→ Show error, stay on step 2
│
├─→ If payment initiation fails:
│   └─→ Show error, stay on step 2
│
└─→ If user closes Flitt before payment:
    └─→ Payment incomplete, user redirected back

Back Button
├─→ From step 2: Return to step 1
└─→ Deselect plan & show plans again
```

---

## 🔐 Authentication State Flow

```
┌──────────────────────────────────────────┐
│      AUTH CONTEXT STATE MANAGEMENT        │
└──────────────────────────────────────────┘

Initial State
├─ user: null
├─ isLoading: false
├─ error: null
└─ token: not in state (stored in localStorage)

When User Logs In
├─→ Component calls: loginWithGoogle(token)
├─→ Context sets: isLoading = true
├─→ Backend validates & returns user
├─→ Context sets:
│   ├─ user = { id, email, name, picture, ... }
│   ├─ isLoading = false
│   ├─ error = null
│   └─ localStorage: JWT token saved
│
└─→ Components re-render with new user

Protected Components
├─→ Header checks useAuth().user
│   ├─→ If user: Show user menu + logout button
│   └─→ If no user: Show "Sign In" button
│
├─→ PaymentPage checks useAuth().user
│   ├─→ If user: Show payment form
│   └─→ If no user: Redirect to /register
│
└─→ Any page: const { user } = useAuth()

Token Management
├─→ On app load:
│   ├─→ Check localStorage for token
│   ├─→ If exists: Validate token
│   ├─→ If valid: Set user in context
│   └─→ If invalid: Clear localStorage
│
└─→ On API request:
    ├─→ Add Authorization header: Bearer {token}
    └─→ If 401: Clear user & redirect to /register

Logout
├─→ User clicks logout
├─→ Context.logout() called
├─→ Context clears:
│   ├─ user = null
│   ├─ error = null
│   └─ localStorage: token removed
│
└─→ Components re-render
    └─→ User redirected to /
```

---

## 🔄 Data Flow Diagram

```
┌────────────────────────────────────────────┐
│         COMPONENT DATA FLOW                 │
└────────────────────────────────────────────┘

App Component
├─→ BrowserRouter (enables routing)
├─→ AuthProvider (authentication context)
└─→ Routes (defines all pages)

Header Component
├─→ useAuth() hook
│   └─→ Reads: user, logout function
├─→ useNavigate() hook
│   └─→ For navigation
└─→ Renders:
    ├─→ User menu (if logged in)
    └─→ Sign in button (if not logged in)

LandingPage Component
├─→ No hooks (static content)
├─→ useNavigate() for buttons
└─→ Renders:
    ├─→ Hero section
    ├─→ Features section
    ├─→ Pricing section
    └─→ CTA section

RegisterPage Component
├─→ useAuth() hook
│   ├─→ Reads: isLoading, error
│   └─→ Calls: loginWithGoogle(), loginWithFacebook()
├─→ useNavigate() for redirect
├─→ useState() for UI state (successMessage)
└─→ Renders:
    ├─→ Google OAuth button
    ├─→ Facebook OAuth button
    ├─→ Email form
    └─→ Error/success messages

PaymentPage Component
├─→ useAuth() hook
│   └─→ Reads: user (check authentication)
├─→ useNavigate() for redirect
├─→ useState() for:
│   ├─ plans[]
│   ├─ selectedPlan
│   ├─ paymentStep
│   └─ isProcessing
├─→ useEffect() for:
│   ├─ Redirect if not authenticated
│   └─ Load subscription plans
└─→ Renders:
    ├─→ Plan selection cards
    ├─→ Payment form
    └─→ Processing/success states

API Service Layer (api.ts)
├─→ subscriptionService
│   ├─ getPlans()
│   ├─ getUserSubscription()
│   └─ createSubscription()
│
└─→ paymentService
    ├─ initiatePayment()
    ├─ checkPaymentStatus()
    └─ completePayment()

Data Flow
User Action
    ↓
Component Handler
    ↓
API Service Call
    ↓
Backend API
    ↓
Return Response
    ↓
Update State (useState)
    ↓
Update Context (AuthContext)
    ↓
Components Re-render
    ↓
DOM Updated
```

---

## 🚨 Error Handling Flow

```
┌─────────────────────────────────────┐
│      ERROR HANDLING FLOW             │
└─────────────────────────────────────┘

User Action
    ↓
Try-Catch Block
├─→ If success: Update state
└─→ If error: Catch error

Error Caught
├─→ Extract error message
│   ├─→ err.response?.data?.detail (backend)
│   ├─→ err.message (generic)
│   └─→ "Unknown error" (fallback)
│
├─→ Update state:
│   └─ error = message
│
├─→ Display to user:
│   ├─→ Error alert box
│   ├─→ Error message text
│   └─→ Error icon
│
└─→ Keep form open for retry

Common Errors:
├─→ Network error
│   └─→ "Network connection failed"
├─→ 401 Unauthorized
│   └─→ Redirect to /register
├─→ 400 Bad Request
│   └─→ Display validation errors
├─→ 500 Server Error
│   └─→ "Server error, please try again"
└─→ OAuth error
    └─→ "Google login failed"

User Can:
├─→ Read error message
├─→ Click "Back" to retry
├─→ Correct input and resubmit
└─→ Contact support if persistent
```

---

## 📱 Mobile User Flow

```
┌─────────────────────────────────────┐
│      MOBILE USER JOURNEY             │
└─────────────────────────────────────┘

User opens yourdomain.io on phone
    │
    ├─→ Landing page loads (mobile optimized)
    ├─→ Header shows hamburger menu
    ├─→ Hero section full width
    ├─→ Features in single column
    ├─→ Pricing in single column
    │
    ├─→ Clicks "Sign Up Now" button
    └─→ Navigates to /register (mobile optimized)

Register page (mobile)
├─→ Full-width card layout
├─→ Large touch-friendly buttons
├─→ Google button spans full width
├─→ Facebook button spans full width
├─→ Form fields full width
└─→ Error messages visible

Payment page (mobile)
├─→ Plan cards stack vertically
├─→ Large touch-friendly buttons
├─→ Form fields full width
├─→ Order summary clear
├─→ Bottom action buttons (Back/Pay)
└─→ No horizontal scrolling

Responsiveness
├─→ Breakpoints:
│   ├─ Mobile: < 640px
│   ├─ Tablet: 640px - 1024px
│   └─ Desktop: > 1024px
│
├─→ Touch targets: 48px+ minimum
├─→ Font sizes readable without zoom
├─→ Buttons easily tappable
└─→ No hover states (but not broken)
```

---

**Last Updated**: November 2024
**Version**: 1.0
