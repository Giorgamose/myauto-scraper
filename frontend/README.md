# MyAuto Subscription Frontend

A modern React 18 + TypeScript web application for vehicle subscription and listing service with OAuth2 authentication and payment integration.

## 🚀 Features

- **Modern UI**: Built with React 18 and Tailwind CSS
- **OAuth2 Authentication**: Google and Facebook sign-in
- **Responsive Design**: Mobile-first approach for all devices
- **Payment Integration**: Flitt payment gateway support
- **Type-Safe**: Full TypeScript support
- **Fast Build**: Vite for development and production

## 📋 Pages

1. **Landing Page** - Service overview, features, and pricing
2. **Registration Page** - OAuth2-based user registration
3. **Payment Page** - Subscription selection and payment processing

## 🔧 Setup & Installation

### Prerequisites

- Node.js 16+
- npm or yarn

### Installation

1. Clone the repository:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment variables:
```bash
cp .env.example .env.local
```

4. Fill in your OAuth credentials in `.env.local`:
```
VITE_GOOGLE_CLIENT_ID=your_client_id
VITE_FACEBOOK_APP_ID=your_app_id
VITE_API_URL=http://localhost:8000/api
```

5. Start development server:
```bash
npm run dev
```

The app will be available at `http://localhost:3000`

## 🔐 OAuth2 Configuration

### Google OAuth Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Google+ API
4. Create OAuth 2.0 Credentials (Web application)
5. Add authorized redirect URIs:
   - `http://localhost:3000`
   - `https://yourdomain.io`
6. Copy the Client ID to `.env.local`

### Facebook OAuth Setup

1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Create a new app
3. Add "Facebook Login" product
4. Configure OAuth Redirect URIs:
   - `http://localhost:3000`
   - `https://yourdomain.io`
5. Copy the App ID to `.env.local`

## 📂 Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── Header.tsx              # Navigation header
│   ├── context/
│   │   └── AuthContext.tsx         # Authentication state management
│   ├── pages/
│   │   ├── LandingPage.tsx         # Home page
│   │   ├── RegisterPage.tsx        # OAuth registration
│   │   └── PaymentPage.tsx         # Subscription & payment
│   ├── services/
│   │   └── api.ts                  # API client and service methods
│   ├── types/
│   │   └── index.ts                # TypeScript interfaces
│   ├── App.tsx                     # Main app component
│   ├── main.tsx                    # Entry point
│   └── index.css                   # Global styles
├── index.html                      # HTML template
├── package.json                    # Dependencies
├── tailwind.config.js              # Tailwind configuration
├── tsconfig.json                   # TypeScript configuration
└── vite.config.ts                  # Vite configuration
```

## 🎨 Design System

### Colors
- **Primary**: Blue (#0ea5e9)
- **Secondary**: Cyan (#06b6d4)
- **Gradient**: Blue to Cyan

### Components
- **Cards**: `card` class for consistent styling
- **Buttons**: `btn-primary`, `btn-secondary`, `btn-oauth`
- **Text**: `gradient-text` for accent text

## 🔗 API Integration

The frontend communicates with the backend API at `VITE_API_URL`:

### Authentication Endpoints
```
POST /auth/google-callback       # Google OAuth callback
POST /auth/facebook-callback     # Facebook OAuth callback
GET  /auth/me                    # Get current user
```

### Subscription Endpoints
```
GET  /subscriptions/plans        # Get available plans
POST /subscriptions              # Create new subscription
GET  /subscriptions/{user_id}    # Get user subscription
```

### Payment Endpoints
```
POST /payments/initiate          # Start payment process
GET  /payments/status/{order_id} # Check payment status
POST /payments/complete/{order_id}
