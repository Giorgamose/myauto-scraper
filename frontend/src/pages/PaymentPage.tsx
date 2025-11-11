import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Check, AlertCircle, CheckCircle, Loader } from 'lucide-react'
import { useAuth } from '../context/AuthContext'
import { subscriptionService, paymentService } from '../services/api'
import { SubscriptionPlan } from '../types'

export const PaymentPage: React.FC = () => {
  const navigate = useNavigate()
  const { user, isLoading: authLoading } = useAuth()
  const [plans, setPlans] = useState<SubscriptionPlan[]>([])
  const [selectedPlan, setSelectedPlan] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isProcessing, setIsProcessing] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [successMessage, setSuccessMessage] = useState<string | null>(null)
  const [paymentStep, setPaymentStep] = useState<'plan-selection' | 'payment-details' | 'processing' | 'success'>('plan-selection')

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/register')
    }
  }, [user, authLoading, navigate])

  // Load plans
  useEffect(() => {
    const loadPlans = async () => {
      try {
        setIsLoading(true)
        const data = await subscriptionService.getPlans()
        setPlans(data)
        // Pre-select the Professional plan
        if (data.length > 1) {
          setSelectedPlan(data[1].id)
        }
      } catch (err) {
        setError('Failed to load subscription plans')
        console.error(err)
      } finally {
        setIsLoading(false)
      }
    }

    loadPlans()
  }, [])

  const handlePlanSelect = (planId: string) => {
    setSelectedPlan(planId)
    setPaymentStep('payment-details')
  }

  const handlePaymentSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()

    if (!selectedPlan || !user) {
      setError('Please select a plan')
      return
    }

    try {
      setIsProcessing(true)
      setPaymentStep('processing')
      setError(null)

      // Create subscription
      const subscription = await subscriptionService.createSubscription(selectedPlan)

      // Get selected plan details
      const plan = plans.find(p => p.id === selectedPlan)
      if (!plan) throw new Error('Plan not found')

      // Initiate payment via Flitt
      const paymentResponse = await paymentService.initiatePayment(
        subscription.id,
        plan.price,
        plan.currency
      )

      // Redirect to Flitt payment gateway
      setSuccessMessage('Redirecting to payment gateway...')
      setTimeout(() => {
        window.location.href = paymentResponse.redirect_url
      }, 1500)
    } catch (err: any) {
      setPaymentStep('payment-details')
      setError(err.response?.data?.detail || 'Payment initiation failed')
      console.error(err)
    } finally {
      setIsProcessing(false)
    }
  }

  if (authLoading || isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <Loader className="w-12 h-12 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading subscription plans...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-cyan-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Choose Your Plan
          </h1>
          <p className="text-xl text-gray-600">
            Select the perfect subscription for your needs
          </p>
        </div>

        {/* Plan Selection Step */}
        {paymentStep === 'plan-selection' && (
          <div className="grid md:grid-cols-3 gap-8 mb-8">
            {plans.map((plan) => (
              <div
                key={plan.id}
                onClick={() => handlePlanSelect(plan.id)}
                className={`card cursor-pointer border-2 transition-all ${
                  selectedPlan === plan.id
                    ? 'border-blue-600 ring-2 ring-blue-200'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <div className="mb-6">
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-4">{plan.description}</p>
                  <div>
                    <span className="text-4xl font-bold text-gray-900">₾{plan.price}</span>
                    <span className="text-gray-600">/month</span>
                  </div>
                </div>

                <button className="w-full btn-primary mb-6">
                  Select Plan
                </button>

                <div className="space-y-3">
                  {plan.features.map((feature, idx) => (
                    <div key={idx} className="flex items-center gap-2">
                      <Check size={20} className="text-green-600 flex-shrink-0" />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Payment Details Step */}
        {paymentStep === 'payment-details' && (
          <div className="max-w-2xl mx-auto">
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
                <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
                <div>
                  <h3 className="font-semibold text-red-800">Error</h3>
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              </div>
            )}

            <div className="card mb-8">
              {/* Order Summary */}
              <div className="mb-8 pb-8 border-b">
                <h2 className="text-2xl font-bold text-gray-900 mb-6">Order Summary</h2>

                {plans
                  .filter(p => p.id === selectedPlan)
                  .map(plan => (
                    <div key={plan.id} className="space-y-4">
                      <div className="flex justify-between items-center">
                        <div>
                          <p className="text-lg font-semibold text-gray-900">{plan.name} Plan</p>
                          <p className="text-sm text-gray-600">{plan.duration_months} months</p>
                        </div>
                        <p className="text-2xl font-bold text-blue-600">₾{plan.price}</p>
                      </div>
                    </div>
                  ))}

                <div className="mt-6 pt-6 border-t">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700">Subtotal</span>
                    <span className="text-gray-900 font-semibold">
                      ₾{plans.find(p => p.id === selectedPlan)?.price}
                    </span>
                  </div>
                  <div className="flex justify-between items-center mb-4">
                    <span className="text-gray-700">Tax (0%)</span>
                    <span className="text-gray-900 font-semibold">₾0</span>
                  </div>
                  <div className="flex justify-between items-center text-lg">
                    <span className="font-bold text-gray-900">Total</span>
                    <span className="text-2xl font-bold text-blue-600">
                      ₾{plans.find(p => p.id === selectedPlan)?.price}
                    </span>
                  </div>
                </div>
              </div>

              {/* Payment Form */}
              <form onSubmit={handlePaymentSubmit} className="space-y-6">
                <div>
                  <h3 className="text-lg font-bold text-gray-900 mb-4">Payment Method</h3>
                  <div className="border-2 border-blue-600 rounded-lg p-4 bg-blue-50">
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-blue-600 rounded-lg flex items-center justify-center">
                        <svg className="w-6 h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                          <path d="M12 1C6.48 1 2 5.48 2 11s4.48 10 10 10 10-4.48 10-10S17.52 1 12 1zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 9 15.5 9 14 9.67 14 10.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 9 8.5 9 7 9.67 7 10.5 7.67 12 8.5 12zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900">Flitt Payment Gateway</p>
                        <p className="text-sm text-gray-600">Secure payment processing</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Billing Address */}
                <div className="grid md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      First Name
                    </label>
                    <input
                      type="text"
                      defaultValue={user?.name.split(' ')[0] || ''}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Last Name
                    </label>
                    <input
                      type="text"
                      defaultValue={user?.name.split(' ').slice(1).join(' ') || ''}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-gray-700 mb-2">
                    Email
                  </label>
                  <input
                    type="email"
                    defaultValue={user?.email}
                    disabled
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg bg-gray-100 text-gray-600"
                  />
                </div>

                {/* Terms & Auto-Renewal */}
                <div className="space-y-3">
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="w-5 h-5 mt-0.5" />
                    <span className="text-sm text-gray-700">
                      I agree to the automatic renewal of my subscription. I can cancel anytime.
                    </span>
                  </label>
                  <label className="flex items-start gap-3 cursor-pointer">
                    <input type="checkbox" defaultChecked className="w-5 h-5 mt-0.5" />
                    <span className="text-sm text-gray-700">
                      I agree to the{' '}
                      <a href="#" className="text-blue-600 hover:underline">
                        Terms of Service
                      </a>{' '}
                      and{' '}
                      <a href="#" className="text-blue-600 hover:underline">
                        Privacy Policy
                      </a>
                    </span>
                  </label>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-4 pt-6">
                  <button
                    type="button"
                    onClick={() => setPaymentStep('plan-selection')}
                    className="flex-1 btn-secondary"
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={isProcessing}
                    className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isProcessing ? 'Processing...' : `Proceed to Payment (₾${plans.find(p => p.id === selectedPlan)?.price})`}
                  </button>
                </div>
              </form>
            </div>

            {/* Security Info */}
            <div className="card bg-blue-50 border-2 border-blue-200">
              <h3 className="font-semibold text-blue-900 mb-3">🔒 Secure Payment</h3>
              <ul className="text-sm text-blue-800 space-y-2">
                <li>✓ Your payment information is encrypted with SSL</li>
                <li>✓ We never store your full card details</li>
                <li>✓ Processed securely through Flitt Payment Gateway</li>
              </ul>
            </div>
          </div>
        )}

        {/* Processing Step */}
        {paymentStep === 'processing' && (
          <div className="max-w-2xl mx-auto">
            <div className="card text-center">
              <div className="mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
                  <Loader className="w-8 h-8 text-blue-600 animate-spin" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Payment</h2>
              <p className="text-gray-600 mb-4">Please wait while we process your payment...</p>
              {successMessage && (
                <p className="text-green-600 font-semibold">{successMessage}</p>
              )}
            </div>
          </div>
        )}

        {/* Success Step - Telegram QR Code & Instructions */}
        {paymentStep === 'success' && (
          <div className="max-w-4xl mx-auto">
            {/* Success Header */}
            <div className="text-center mb-12">
              <div className="w-20 h-20 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <CheckCircle className="w-12 h-12 text-white" />
              </div>
              <h1 className="text-4xl font-bold text-gray-900 mb-2">
                Payment Successful! 🎉
              </h1>
              <p className="text-lg text-gray-600">
                Your subscription is now active. Join our Telegram channel to start receiving vehicle listings.
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-8 mb-8">
              {/* Left: QR Code Section */}
              <div className="card bg-gradient-to-br from-blue-50 to-cyan-50">
                <div className="text-center mb-6">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">Step 1: Scan QR Code</h2>
                  <p className="text-gray-600">Use your phone's camera or Telegram app</p>
                </div>

                {/* QR Code Display */}
                <div className="bg-white p-6 rounded-lg border-4 border-blue-600 mb-6 flex justify-center">
                  <div className="w-64 h-64 bg-gray-100 rounded-lg flex items-center justify-center">
                    {/* QR Code Placeholder - will be replaced with actual QR */}
                    <div className="text-center">
                      <svg className="w-48 h-48 text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M19 13h-6v6h6v-6zm4-12h-3V2h-2v2h-4V2h-2v2H8V2H6v2H3c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V3c0-1.1-.9-2-2-2zm0 16H3V6h16v11z" />
                      </svg>
                      <p className="text-sm text-gray-500 mt-2">QR Code</p>
                      <p className="text-xs text-gray-400">t.me/myauto_listings</p>
                    </div>
                  </div>
                </div>

                <p className="text-sm text-gray-600 text-center">
                  <strong>Channel ID:</strong> @myauto_listings
                </p>
              </div>

              {/* Right: Instructions Section */}
              <div className="space-y-6">
                {/* Instructions Steps */}
                <div className="card">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6">How to Get Started</h2>

                  <div className="space-y-4">
                    {/* Step 1 */}
                    <div className="flex gap-4 pb-4 border-b">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                          1
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">Scan the QR Code</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Open Telegram and scan the QR code to the left using your camera
                        </p>
                      </div>
                    </div>

                    {/* Step 2 */}
                    <div className="flex gap-4 pb-4 border-b">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                          2
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">Join the Channel</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Click "Join Channel" to subscribe to @myauto_listings
                        </p>
                      </div>
                    </div>

                    {/* Step 3 */}
                    <div className="flex gap-4 pb-4 border-b">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                          3
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">Add Search Criteria</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Go to your dashboard and add vehicle search criteria (brand, model, price range, etc.)
                        </p>
                      </div>
                    </div>

                    {/* Step 4 */}
                    <div className="flex gap-4">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                          4
                        </div>
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900">Start Receiving Listings</h3>
                        <p className="text-sm text-gray-600 mt-1">
                          Receive real-time vehicle listings matching your criteria directly on Telegram
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Quick Link */}
                <a
                  href="https://t.me/myauto_listings"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn-primary w-full text-center block"
                >
                  Open Telegram Channel
                </a>
              </div>
            </div>

            {/* Bot Commands Section */}
            <div className="card mb-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Bot Commands</h2>

              <p className="text-gray-600 mb-6">
                Manage your subscription and search criteria using these bot commands:
              </p>

              <div className="grid md:grid-cols-2 gap-6">
                {/* Command 1 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-blue-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-blue-600">
                    /add_criteria
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    Add new vehicle search criteria (brand, model, price, year, etc.)
                  </p>
                </div>

                {/* Command 2 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-green-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-green-600">
                    /my_criteria
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    View all your active search criteria
                  </p>
                </div>

                {/* Command 3 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-orange-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-orange-600">
                    /pause
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    Temporarily pause receiving listings
                  </p>
                </div>

                {/* Command 4 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-purple-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-purple-600">
                    /resume
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    Resume receiving listings
                  </p>
                </div>

                {/* Command 5 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-red-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-red-600">
                    /subscription_status
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    Check your current subscription details and renewal date
                  </p>
                </div>

                {/* Command 6 */}
                <div className="bg-gray-50 rounded-lg p-4 border-l-4 border-indigo-600">
                  <code className="text-sm font-mono bg-gray-200 px-3 py-1 rounded text-indigo-600">
                    /help
                  </code>
                  <p className="text-sm text-gray-700 mt-2">
                    Get a list of all available commands
                  </p>
                </div>
              </div>
            </div>

            {/* What to Expect Section */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9c.83 0 1.5-.67 1.5-1.5S16.33 9 15.5 9 14 9.67 14 10.5s.67 1.5 1.5 1.5zm-7 0c.83 0 1.5-.67 1.5-1.5S9.33 9 8.5 9 7 9.67 7 10.5 7.67 12 8.5 12zm3.5 6.5c2.33 0 4.31-1.46 5.11-3.5H6.89c.8 2.04 2.78 3.5 5.11 3.5z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-gray-900">Real-Time Alerts</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Receive instant notifications when new vehicles matching your criteria are listed
                </p>
              </div>

              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-green-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-gray-900">Detailed Info</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Each listing includes photos, price, mileage, year, and direct seller contact
                </p>
              </div>

              <div className="card">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
                    <svg className="w-6 h-6 text-purple-600" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 8c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm0 2c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2zm0 6c-1.1 0-2 .9-2 2s.9 2 2 2 2-.9 2-2-.9-2-2-2z" />
                    </svg>
                  </div>
                  <h3 className="font-bold text-gray-900">Full Control</h3>
                </div>
                <p className="text-sm text-gray-600">
                  Manage criteria, pause/resume notifications, and view subscription status anytime
                </p>
              </div>
            </div>

            {/* Support Section */}
            <div className="card bg-amber-50 border-2 border-amber-200 mb-8">
              <h3 className="font-bold text-amber-900 mb-3">❓ Need Help?</h3>
              <p className="text-sm text-amber-800 mb-4">
                If you have any questions or need assistance, feel free to reach out to our support team:
              </p>
              <div className="space-y-2">
                <p className="text-sm">
                  <strong>Email:</strong>{' '}
                  <a href="mailto:support@myauto.io" className="text-amber-700 hover:underline">
                    support@myauto.io
                  </a>
                </p>
                <p className="text-sm">
                  <strong>Telegram:</strong>{' '}
                  <a href="https://t.me/myauto_support" target="_blank" rel="noopener noreferrer" className="text-amber-700 hover:underline">
                    @myauto_support
                  </a>
                </p>
                <p className="text-sm">
                  <strong>Response Time:</strong> Usually within 1 hour
                </p>
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="https://t.me/myauto_listings"
                target="_blank"
                rel="noopener noreferrer"
                className="btn-primary text-center"
              >
                📱 Open Telegram Channel Now
              </a>
              <button
                onClick={() => navigate('/dashboard')}
                className="btn-secondary text-center"
              >
                📊 Go to Dashboard
              </button>
            </div>

            {/* Next Steps Info */}
            <div className="mt-8 p-6 bg-blue-50 border-l-4 border-blue-600 rounded-lg">
              <h4 className="font-bold text-blue-900 mb-2">✅ What's Next?</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Join the Telegram channel using the QR code above</li>
                <li>✓ Visit your dashboard to add vehicle search criteria</li>
                <li>✓ Start receiving listings matching your preferences</li>
                <li>✓ Use bot commands to manage your subscription</li>
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
