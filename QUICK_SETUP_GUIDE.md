# ⚡ Quick Frontend Setup (localhost:3000)

## 🚀 Get Running in 2 Minutes

### Step 1: Navigate to Frontend Directory
```bash
cd frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

This will download all required packages (~500MB, takes 2-5 minutes)

### Step 3: Start Development Server
```bash
npm run dev
```

You should see:
```
  VITE v5.0.8  ready in 123 ms

  ➜  Local:   http://localhost:3000/
  ➜  press h to show help
```

### Step 4: Open Browser
```
http://localhost:3000
```

✅ **Done! Your frontend is running!**

---

## 🎯 What You'll See

### Landing Page
```
http://localhost:3000/
- Service features
- Pricing plans
- Sign up buttons
```

### Registration Page
```
http://localhost:3000/register
- Google OAuth button
- Facebook OAuth button
- Email signup form
```

### Payment Page
```
http://localhost:3000/subscription
- Plan selection
- Billing form
- Payment processing
```

---

## 🔧 Troubleshooting

### ❌ "npm: command not found"
**Solution**: Install Node.js from https://nodejs.org (LTS version)

### ❌ "Port 3000 already in use"
**Solution**:
```bash
# Kill the process using port 3000
# On Windows:
netstat -ano | findstr :3000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -i :3000
kill -9 <PID>
```

### ❌ "Module not found"
**Solution**:
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### ❌ "Address already in use"
**Solution**: The server is already running. Either:
- Stop it: Press `Ctrl + C` in the terminal
- Use a different port:
```bash
npm run dev -- --port 3001
```

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── LandingPage.tsx      # Home page
│   │   ├── RegisterPage.tsx     # OAuth signup
│   │   └── PaymentPage.tsx      # Payment page
│   ├── components/
│   │   ├── Header.tsx           # Navigation
│   │   └── TelegramQRSuccess.tsx # Success page
│   ├── App.tsx                  # Router
│   └── main.tsx                 # Entry point
├── package.json                 # Dependencies
└── tailwind.config.js           # Styling
```

---

## 🧪 Testing Pages

After running `npm run dev` and visiting http://localhost:3000:

### 1. Test Landing Page
- Visit `http://localhost:3000/`
- ✅ Should see hero section
- ✅ Should see features section
- ✅ Should see pricing section
- ✅ Should see footer

### 2. Test Registration Page
- Click "Sign Up Now" or visit `http://localhost:3000/register`
- ✅ Should see Google OAuth button
- ✅ Should see Facebook OAuth button
- ✅ Should see email signup form

### 3. Test Payment Page
- Visit `http://localhost:3000/subscription`
- ✅ Should see 3 subscription plans
- ✅ Should see plan selection cards
- (Note: OAuth buttons won't work without credentials)

### 4. Test Mobile Responsive
- Open DevTools: Press `F12`
- Toggle Device Toolbar: Press `Ctrl + Shift + M`
- ✅ Page should resize smoothly
- ✅ Menu should become hamburger on mobile

---

## 📝 Environment Variables (Optional)

Create `.env.local` in the `frontend` directory:

```env
# If you have OAuth credentials:
VITE_GOOGLE_CLIENT_ID=your_client_id
VITE_FACEBOOK_APP_ID=your_app_id

# Backend API (optional for now)
VITE_API_URL=http://localhost:8000/api
```

**Note**: Without these, OAuth buttons won't work (but pages will still display)

---

## 🛑 Stop the Server

To stop the development server:

**In Terminal:**
```bash
# Press Ctrl + C
^C
```

The server will stop and you'll see:
```
[VITE] server closed.
```

---

## ⚡ Next Steps

### After Confirming localhost:3000 Works:

1. **View all 3 pages** to confirm UI looks good
2. **Check mobile responsive** by toggling device view
3. **Get OAuth credentials** (see FRONTEND_SETUP.md)
4. **Add environment variables** to test OAuth
5. **Build for production** when ready

---

## 🎨 Features You Can Test

| Feature | Where | How |
|---------|-------|-----|
| Hero Section | Landing Page | Visual check |
| Features Cards | Landing Page | Hover effects |
| Pricing Plans | Landing Page | Click cards |
| Responsive Design | Any Page | Resize window |
| Navigation | Header | Click logo |
| Form Validation | Register/Payment | Try inputs |
| Smooth Scroll | Any Page | Scroll down |

---

## 📱 Browser Support

**Tested On:**
- ✅ Chrome/Chromium (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

**Minimum Requirements:**
- Modern browser (ES6 support)
- JavaScript enabled
- Cookies enabled

---

## 🔍 Common URLs

```
http://localhost:3000/              # Landing page
http://localhost:3000/register      # Registration
http://localhost:3000/subscription  # Payment
http://localhost:3000/dashboard     # Dashboard (redirect if not auth'd)
http://localhost:3000/anything-else # 404 page
```

---

## 💾 Save Your Work

Your code changes are automatically saved. To commit to Git:

```bash
git add .
git commit -m "Your message"
git push
```

---

## 🚀 Production Build

When you're ready to deploy:

```bash
# Create optimized build
npm run build

# Preview the build locally
npm run preview
```

The build will be in the `dist/` folder.

---

## ✅ Quick Checklist

- [ ] Navigated to `frontend` directory
- [ ] Ran `npm install` (completed)
- [ ] Running `npm run dev`
- [ ] Opened http://localhost:3000
- [ ] Tested landing page
- [ ] Tested registration page
- [ ] Tested payment page
- [ ] Tested mobile view (F12)
- [ ] No console errors
- [ ] All pages load correctly

---

## 📞 Help?

If something doesn't work:

1. **Check terminal for errors** - Read the error message carefully
2. **Check console** - Press F12 → Console tab
3. **Restart server** - Press Ctrl+C, then `npm run dev` again
4. **Clear cache** - Delete `node_modules` and `.vite` folder, run `npm install`
5. **Check Node version** - Run `node --version` (should be 16+)

---

## 🎉 You're Ready!

Once you see "Local: http://localhost:3000/" in your terminal, your frontend is running!

Open your browser to **http://localhost:3000** and start exploring! 🚀

---

**Last Updated**: November 2024
**Time to Setup**: 2-5 minutes
**Status**: Ready to use
