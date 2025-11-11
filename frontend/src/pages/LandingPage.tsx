import React from 'react'
import { Link } from 'react-router-dom'
import {
  Zap,
  TrendingUp,
  Bell,
  Shield,
  Smartphone,
  Gift,
  ArrowRight,
  Check
} from 'lucide-react'

export const LandingPage: React.FC = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-20 pb-32 px-4 sm:px-6 lg:px-8 bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-50">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-2 gap-12 items-center">
            <div className="animate-slideUp">
              <h1 className="text-5xl sm:text-6xl font-bold text-gray-900 mb-6 leading-tight">
                Find Your Perfect <span className="gradient-text">Vehicle</span> in Seconds
              </h1>
              <p className="text-xl text-gray-600 mb-8">
                Get instant notifications on the best vehicle listings matching your criteria. Smart search, real-time alerts, and exclusive deals delivered directly to you.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link to="/register" className="btn-primary text-center">
                  Start Free Trial
                  <ArrowRight size={20} className="inline ml-2" />
                </Link>
                <button className="btn-secondary text-center">
                  Watch Demo
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-6">
                ✓ No credit card required • ✓ 7-day free trial • ✓ Cancel anytime
              </p>
            </div>

            <div className="relative">
              <div className="bg-gradient-to-br from-blue-400 to-cyan-400 rounded-3xl p-1">
                <div className="bg-white rounded-3xl p-8">
                  <div className="space-y-4">
                    <div className="h-12 bg-gray-200 rounded-lg animate-pulse"></div>
                    <div className="space-y-2">
                      <div className="h-4 bg-gray-200 rounded w-5/6 animate-pulse"></div>
                      <div className="h-4 bg-gray-200 rounded w-4/6 animate-pulse"></div>
                    </div>
                    <div className="pt-4 space-y-2">
                      <div className="h-3 bg-gray-100 rounded w-full animate-pulse"></div>
                      <div className="h-3 bg-gray-100 rounded w-5/6 animate-pulse"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Why Choose MyAuto?
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to find the perfect vehicle
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Feature 1 */}
            <div className="card group">
              <div className="w-14 h-14 bg-blue-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-blue-600 transition">
                <Bell size={28} className="text-blue-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Real-Time Alerts</h3>
              <p className="text-gray-600">
                Get instant notifications the moment a vehicle matching your criteria is listed. Never miss a great deal again.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card group">
              <div className="w-14 h-14 bg-cyan-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-cyan-600 transition">
                <Zap size={28} className="text-cyan-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Smart Filtering</h3>
              <p className="text-gray-600">
                Advanced filters for brand, model, price, year, and more. Customize your search exactly how you want it.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card group">
              <div className="w-14 h-14 bg-green-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-green-600 transition">
                <TrendingUp size={28} className="text-green-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Market Insights</h3>
              <p className="text-gray-600">
                Get detailed market trends, price analytics, and recommendations to make informed decisions.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card group">
              <div className="w-14 h-14 bg-purple-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-purple-600 transition">
                <Smartphone size={28} className="text-purple-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Telegram Integration</h3>
              <p className="text-gray-600">
                Receive listings directly on Telegram. Stay updated wherever you are with zero effort.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card group">
              <div className="w-14 h-14 bg-red-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-red-600 transition">
                <Shield size={28} className="text-red-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Secure & Private</h3>
              <p className="text-gray-600">
                Your data is encrypted and protected. We never share your information with third parties.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card group">
              <div className="w-14 h-14 bg-amber-100 rounded-lg flex items-center justify-center mb-4 group-hover:bg-amber-600 transition">
                <Gift size={28} className="text-amber-600 group-hover:text-white transition" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Premium Support</h3>
              <p className="text-gray-600">
                Get priority support from our team. We're here to help you find your perfect vehicle.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Pricing Preview Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600">
              Choose the plan that works best for you
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Starter Plan */}
            <div className="card border-2 border-gray-200">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Starter</h3>
              <p className="text-gray-600 mb-6">Perfect for casual buyers</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">₾99</span>
                <span className="text-gray-600">/month</span>
              </div>
              <button className="w-full btn-secondary mb-6">Get Started</button>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">5 Search Criteria</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Daily Notifications</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Email Support</span>
                </div>
              </div>
            </div>

            {/* Professional Plan - Featured */}
            <div className="card border-2 border-blue-600 relative transform md:scale-105">
              <div className="absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 rounded-bl-lg rounded-tr-lg text-sm font-semibold">
                Most Popular
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2 mt-4">Professional</h3>
              <p className="text-gray-600 mb-6">Best for serious buyers</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">₾299</span>
                <span className="text-gray-600">/month</span>
              </div>
              <button className="w-full btn-primary mb-6">Start Free Trial</button>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">25 Search Criteria</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Real-Time Alerts</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Telegram Integration</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Priority Support</span>
                </div>
              </div>
            </div>

            {/* Enterprise Plan */}
            <div className="card border-2 border-gray-200">
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Enterprise</h3>
              <p className="text-gray-600 mb-6">For professional dealers</p>
              <div className="mb-6">
                <span className="text-4xl font-bold text-gray-900">₾999</span>
                <span className="text-gray-600">/month</span>
              </div>
              <button className="w-full btn-secondary mb-6">Contact Sales</button>
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Unlimited Criteria</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">Multi-Channel Delivery</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">API Access</span>
                </div>
                <div className="flex items-center gap-2">
                  <Check size={20} className="text-green-600" />
                  <span className="text-gray-700">24/7 Dedicated Support</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-blue-600 to-cyan-500">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl font-bold text-white mb-6">
            Ready to find your perfect vehicle?
          </h2>
          <p className="text-xl text-blue-100 mb-8">
            Join thousands of satisfied customers. Start your free trial today.
          </p>
          <Link to="/register" className="inline-block bg-white text-blue-600 font-bold py-4 px-8 rounded-lg hover:bg-gray-100 transition shadow-lg">
            Sign Up Now
            <ArrowRight size={20} className="inline ml-2" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-gray-300 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto grid md:grid-cols-4 gap-8 mb-8">
          <div>
            <h4 className="text-white font-bold mb-4">Product</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition">Features</a></li>
              <li><a href="#" className="hover:text-white transition">Pricing</a></li>
              <li><a href="#" className="hover:text-white transition">Security</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Company</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition">About</a></li>
              <li><a href="#" className="hover:text-white transition">Blog</a></li>
              <li><a href="#" className="hover:text-white transition">Contact</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Legal</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition">Privacy</a></li>
              <li><a href="#" className="hover:text-white transition">Terms</a></li>
              <li><a href="#" className="hover:text-white transition">Cookies</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-4">Follow Us</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="#" className="hover:text-white transition">Facebook</a></li>
              <li><a href="#" className="hover:text-white transition">Twitter</a></li>
              <li><a href="#" className="hover:text-white transition">Instagram</a></li>
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 pt-8 text-center text-sm">
          <p>&copy; 2024 MyAuto. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
