import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import { Header } from './components/Header'
import { LandingPage } from './pages/LandingPage'
import { RegisterPage } from './pages/RegisterPage'
import { PaymentPage } from './pages/PaymentPage'

function App() {
  return (
    <Router>
      <AuthProvider>
        <Header />
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/subscription" element={<PaymentPage />} />
          <Route path="*" element={<div className="min-h-screen flex items-center justify-center text-2xl font-bold text-gray-700">Page Not Found</div>} />
        </Routes>
      </AuthProvider>
    </Router>
  )
}

export default App
