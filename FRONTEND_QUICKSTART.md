# 🚀 Frontend Quick Start Guide

## What You Have

A complete, production-ready React frontend for the MyAuto subscription platform with:
- ✅ Modern landing page with features & pricing
- ✅ OAuth2 registration (Google & Facebook)
- ✅ Payment page with subscription plans
- ✅ Type-safe TypeScript setup
- ✅ Tailwind CSS styling
- ✅ Mobile responsive design
- ✅ Error handling & loading states

---

## 5-Minute Setup

### 1. Install Dependencies
```bash
cd frontend
npm install
```

### 2. Create `.env.local`
```bash
cp .env.example .env.local
```

Edit `.env.local`:
```env
VITE_GOOGLE_CLIENT_ID=placeholder_for_now
VITE_FACEBOOK_APP_ID=placeholder_for_now
VITE_API_URL=http://localhost:8000/api
```

### 3. Start Development Server
```bash
npm run dev
```

### 4. Open in Browser
```
http://localhost:3000
```

---

## 📄 Pages

### Landing Page
**URL**: `/`
- Service overview
- 6 key features
- 3 pricing plans
- Call-to-action

### Registration Page
**URL**: `/register`
- Google OAuth button
- Facebook OAuth button
- Email signup form
- Security info

### Payment Page
**URL**: `/subscription`
- Plan selection
- Billing details form
- Order summary
- Flitt payment gateway

---

## 🔐 Enable OAuth (Required for Full Functionality)

### Google OAuth

1. Go to https://console.cloud.google.com/
2. Create new project → "MyAuto"
3. Enable Google+ API
4. Create OAuth credentials (Web application)
5. Add origins:
   - `http://localhost:3000`
   - `https://yourdomain.io`
6. Copy Client ID → paste in `.env.local`

```env
VITE_GOOGLE_CLIENT_ID=your_client_id_here
```

### Facebook OAuth

1. Go to https://developers.facebook.com/
2. Create new app → Consumer
3. Add "Facebook Login" product
4. Configure redirect URIs:
   - `http://localhost:3000/register`
   - `https://yourdomain.io/register`
5. Copy App ID → paste in `.env.local`

```env
VITE_FACEBOOK_APP_ID=your_app_id_here
```

---

## 📦 Available Scripts

```bash
# Development
npm run dev              # Start dev server

# Production
npm run build           # Build for production
npm run preview         # Preview production build

# Linting
npm run lint            # Check code quality
```

---

## 🎨 Customization

### Change Colors
Edit `tailwind.config.js`:
```javascript
theme: {
  extend: {
    colors: {
      primary: {
        500: '#0ea5e9',  // Change this
        600: '#0284c7',  // And this
      }
    }
  }
}
```

### Update Branding
Edit `src/components/Header.tsx`:
- Change logo text
- Update company name
- Modify colors

### Add New Pages
1. Create component in `src/pages/`
2. Add route in `src/App.tsx`:
```typescript
<Route path="/your-page" element={<YourPage />} />
```

---

## 🔗 Connect to Backend

Edit `.env.local`:
```env
# Local development
VITE_API_URL=http://localhost:8000/api

# Production
VITE_API_URL=https://api.yourdomain.io
```

Backend should implement these endpoints:

```
POST   /auth/google-callback       → returns { access_token, user }
POST   /auth/facebook-callback     → returns { access_token, user }
GET    /auth/me                    → returns { user }
GET    /subscriptions/plans        → returns { plans: [...] }
POST   /subscriptions              → returns { subscription }
POST   /payments/initiate          → returns { redirect_url }
```

---

## 🌐 Deploy to Vercel (Free)

### 1. Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/myauto-frontend.git
git push -u origin main
```

### 2. Deploy on Vercel
1. Go to https://vercel.com/
2. Click "New Project"
3. Import your GitHub repository
4. Select `frontend` as root directory
5. Add environment variables:
   ```
   VITE_GOOGLE_CLIENT_ID=your_value
   VITE_FACEBOOK_APP_ID=your_value
   VITE_API_URL=https://api.yourdomain.io
   ```
6. Click "Deploy"

### 3. Custom Domain
1. In Vercel dashboard → Settings → Domains
2. Add your `.io` domain
3. Update DNS records (Vercel shows instructions)
4. Wait for propagation (5-48 hours)

---

## 📱 Mobile Testing

### iOS
```bash
npm run dev
# Visit http://your-local-ip:3000 from iPhone
```

### Android
Same as iOS

### Chrome DevTools
Press `F12` → Toggle device toolbar (Ctrl+Shift+M)

---

## 🐛 Troubleshooting

### Issue: OAuth buttons not working
**Solution**:
- Verify Client ID is correct
- Check redirect URIs match your domain
- Clear browser cookies
- Check browser console for errors

### Issue: API connection fails
**Solution**:
- Make sure backend is running on port 8000
- Check `VITE_API_URL` is correct
- Verify CORS is enabled on backend
- Check Network tab in DevTools

### Issue: Build fails
**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📊 Project Structure Summary

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LandingPage.tsx       # Home
│   │   ├── RegisterPage.tsx      # OAuth signup
│   │   └── PaymentPage.tsx       # Subscription
│   ├── components/
│   │   └── Header.tsx             # Navigation
│   ├── context/
│   │   └── AuthContext.tsx        # Auth state
│   ├── services/
│   │   └── api.ts                 # API calls
│   ├── types/
│   │   └── index.ts               # TypeScript types
│   ├── App.tsx                    # Routing
│   ├── main.tsx                   # Entry
│   └── index.css                  # Styles
├── index.html                     # HTML template
├── package.json                   # Dependencies
├── tailwind.config.js             # Styling config
├── vite.config.ts                 # Build config
└── tsconfig.json                  # TypeScript config
```

---

## ✅ Verification Checklist

- [ ] Dependencies installed (`npm install`)
- [ ] `.env.local` created with API URL
- [ ] Dev server running (`npm run dev`)
- [ ] Landing page loads at http://localhost:3000
- [ ] OAuth buttons appear (even if not functional yet)
- [ ] Payment page loads when clicking "Sign Up"
- [ ] No errors in browser console
- [ ] Mobile view works (F12 → toggle device)

---

## 🚀 Next Steps

1. **Get OAuth Credentials** (5 min)
   - Google OAuth from Google Cloud
   - Facebook App ID from Facebook Developers

2. **Build Backend** (refer to BACKEND_SETUP.md)
   - FastAPI + PostgreSQL
   - Auth endpoints
   - Subscription management

3. **Integrate Flitt** (Payment)
   - Get Flitt API keys
   - Implement payment endpoint

4. **Deploy to Vercel** (5 min)
   - GitHub integration
   - Set environment variables
   - Custom domain

5. **Build Telegram Bot** (refer to BOT_SETUP.md)
   - QR code generation
   - Listing delivery

---

## 📚 Important Files to Read

1. **[FRONTEND_SETUP.md](./FRONTEND_SETUP.md)** - Detailed setup & OAuth guide
2. **[FRONTEND_SUMMARY.md](./FRONTEND_SUMMARY.md)** - Complete feature overview
3. **[frontend/README.md](./frontend/README.md)** - Project documentation

---

## 💬 Quick Help

**Q: How do I change the landing page content?**
A: Edit `src/pages/LandingPage.tsx`

**Q: How do I add a new page?**
A: Create file in `src/pages/`, add route in `App.tsx`

**Q: How do I connect to my backend?**
A: Update `VITE_API_URL` in `.env.local` and implement endpoints

**Q: Can I deploy without OAuth?**
A: Yes, but OAuth buttons won't work. Users can still use email signup.

**Q: Is it free to deploy?**
A: Yes! Vercel offers 100GB/month bandwidth for free.

---

## 🎉 You're All Set!

Your modern React frontend is ready to go. Start the dev server and begin building your backend!

```bash
npm run dev
```

Happy coding! 🚀
