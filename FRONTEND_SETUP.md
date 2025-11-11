# Frontend Setup & Deployment Guide

## 📦 Quick Start

### Local Development

```bash
cd frontend
npm install
npm run dev
```

Visit `http://localhost:3000`

---

## 🔐 OAuth Configuration (Required)

### 1. Google OAuth

#### Step 1: Create Google Cloud Project
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a Project" → "New Project"
3. Name it "MyAuto Subscription"
4. Click "Create"

#### Step 2: Enable Google+ API
1. Search for "Google+ API"
2. Click "Enable"

#### Step 3: Create OAuth Credentials
1. Go to "Credentials" in left sidebar
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure consent screen first:
   - User Type: External
   - App name: MyAuto
   - User support email: your-email@example.com
   - Add yourself as a test user
4. Application Type: Web application
5. Add Authorized JavaScript origins:
   - `http://localhost:3000`
   - `http://localhost:3000:3000`
   - `https://yourdomain.io`
6. Add Authorized redirect URIs:
   - `http://localhost:3000/register`
   - `https://yourdomain.io/register`
7. Copy the Client ID

#### Step 4: Add to Frontend
Create `.env.local`:
```
VITE_GOOGLE_CLIENT_ID=your_copied_client_id_here
```

---

### 2. Facebook OAuth

#### Step 1: Create Facebook App
1. Go to [Facebook Developers](https://developers.facebook.com/)
2. Click "My Apps" → "Create App"
3. App Type: Consumer
4. App Name: MyAuto
5. App Contact Email: your-email@example.com
6. Create App

#### Step 2: Add Facebook Login Product
1. In App Dashboard, click "+ Add Product"
2. Find "Facebook Login" and click "Set Up"
3. Choose "Web"

#### Step 3: Configure OAuth Redirect URLs
1. Go to Settings → Basic → Copy App ID
2. Go to Facebook Login → Settings
3. Add Valid OAuth Redirect URIs:
   ```
   http://localhost:3000/register
   https://yourdomain.io/register
   ```

#### Step 4: Configure App Domains
1. In Settings → Basic
2. Add App Domains:
   ```
   localhost:3000
   yourdomain.io
   ```

#### Step 5: Add to Frontend
Add to `.env.local`:
```
VITE_FACEBOOK_APP_ID=your_copied_app_id_here
```

---

## 🌐 Backend API Configuration

Add to `.env.local`:
```
VITE_API_URL=http://localhost:8000/api    # For local development
# or
VITE_API_URL=https://api.yourdomain.io     # For production
```

---

## 🚀 Production Deployment

### Option 1: Vercel (Recommended - Free)

#### Prerequisites
- GitHub account
- Vercel account

#### Deployment Steps

1. **Push to GitHub**
```bash
cd frontend
git init
git add .
git commit -m "Initial frontend commit"
git remote add origin https://github.com/yourusername/myauto-frontend.git
git branch -M main
git push -u origin main
```

2. **Connect to Vercel**
   - Go to [Vercel](https://vercel.com/)
   - Sign in with GitHub
   - Click "New Project"
   - Import your repository
   - Framework: Vite
   - Root Directory: `frontend`

3. **Set Environment Variables**
   - In Vercel Dashboard → Settings → Environment Variables
   - Add:
     ```
     VITE_GOOGLE_CLIENT_ID=your_value
     VITE_FACEBOOK_APP_ID=your_value
     VITE_API_URL=https://api.yourdomain.io
     ```

4. **Deploy**
   - Click "Deploy"
   - Wait for build to complete

#### Custom Domain Setup

1. Go to Project Settings → Domains
2. Add Domain:
   - Enter `yourdomain.io`
3. Vercel will show DNS records to update

#### Update DNS Records

In your domain registrar (Namecheap, Porkbun, etc.):

1. Go to DNS Settings
2. Update/Add records based on Vercel's instructions:
   ```
   Type: CNAME
   Name: @
   Value: cname.vercel.com

   Type: A
   Name: @
   Value: 76.76.19.132
   ```

3. Wait for DNS propagation (5-48 hours)

---

### Option 2: Netlify (Free)

1. Push code to GitHub (same as above)
2. Go to [Netlify](https://netlify.com/)
3. Click "New site from Git"
4. Select your repository
5. Build Command: `npm run build`
6. Publish Directory: `dist`
7. Add Environment Variables (same as Vercel)
8. Deploy
9. Add custom domain in Domain Settings

---

### Option 3: GitHub Pages (Free, Static Only)

Not recommended for OAuth apps. Use Vercel or Netlify instead.

---

## 📊 Environment Variables Summary

### Development
```env
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_FACEBOOK_APP_ID=your_facebook_app_id
VITE_API_URL=http://localhost:8000/api
```

### Production
```env
VITE_GOOGLE_CLIENT_ID=your_google_client_id
VITE_FACEBOOK_APP_ID=your_facebook_app_id
VITE_API_URL=https://api.yourdomain.io
```

---

## 🧪 Testing

### Local Testing
```bash
npm run dev
```

### Build Testing
```bash
npm run build
npm run preview
```

Visit `http://localhost:4173` to preview production build.

---

## 🔍 Troubleshooting

### OAuth not working?
- [ ] Check Client ID is correct in .env.local
- [ ] Verify redirect URIs match your domain
- [ ] Clear browser cache and cookies
- [ ] Check browser console for errors

### API connection fails?
- [ ] Verify backend is running
- [ ] Check VITE_API_URL is correct
- [ ] Check CORS is enabled on backend
- [ ] Verify backend port (default 8000)

### Build fails?
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

---

## 📝 Important Notes

1. **Never commit `.env.local`** - Add to `.gitignore`
2. **Use different OAuth credentials** for dev and production
3. **Update OAuth redirect URIs** when deploying to new domain
4. **Monitor API rate limits** for OAuth providers
5. **HTTPS only** for production (Vercel provides free SSL)

---

## 🎯 Next Steps

1. Set up backend API (see BACKEND_SETUP.md)
2. Configure Flitt payment integration
3. Set up Telegram bot integration
4. Deploy to production

---

## 📞 Support

For OAuth issues, check official docs:
- [Google OAuth](https://developers.google.com/identity/protocols/oauth2)
- [Facebook Login](https://developers.facebook.com/docs/facebook-login)
