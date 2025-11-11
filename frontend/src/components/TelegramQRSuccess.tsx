import React from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCircle } from 'lucide-react'

interface TelegramQRSuccessProps {
  userName?: string
  subscriptionPlan?: string
}

export const TelegramQRSuccess: React.FC<TelegramQRSuccessProps> = ({
  userName = 'User',
  subscriptionPlan = 'Professional'
}) => {
  const navigate = useNavigate()

  return (
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
          Welcome to MyAuto, {userName}! Your {subscriptionPlan} subscription is now active.
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
              {/* QR Code Placeholder - Replace with actual QR using qrcode.react */}
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
              {[
                {
                  step: 1,
                  title: 'Scan the QR Code',
                  description: 'Open Telegram and scan the QR code to the left using your camera'
                },
                {
                  step: 2,
                  title: 'Join the Channel',
                  description: 'Click "Join Channel" to subscribe to @myauto_listings'
                },
                {
                  step: 3,
                  title: 'Add Search Criteria',
                  description: 'Go to your dashboard and add vehicle search criteria (brand, model, price range, etc.)'
                },
                {
                  step: 4,
                  title: 'Start Receiving Listings',
                  description: 'Receive real-time vehicle listings matching your criteria directly on Telegram'
                }
              ].map((item, index) => (
                <div key={item.step} className={`flex gap-4 ${index < 3 ? 'pb-4 border-b' : ''}`}>
                  <div className="flex-shrink-0">
                    <div className="flex items-center justify-center h-10 w-10 rounded-full bg-blue-600 text-white font-bold">
                      {item.step}
                    </div>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{item.title}</h3>
                    <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                  </div>
                </div>
              ))}
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
          {[
            {
              command: '/add_criteria',
              color: 'blue',
              description: 'Add new vehicle search criteria (brand, model, price, year, etc.)'
            },
            {
              command: '/my_criteria',
              color: 'green',
              description: 'View all your active search criteria'
            },
            {
              command: '/pause',
              color: 'orange',
              description: 'Temporarily pause receiving listings'
            },
            {
              command: '/resume',
              color: 'purple',
              description: 'Resume receiving listings'
            },
            {
              command: '/subscription_status',
              color: 'red',
              description: 'Check your current subscription details and renewal date'
            },
            {
              command: '/help',
              color: 'indigo',
              description: 'Get a list of all available commands'
            }
          ].map((item) => (
            <div key={item.command} className={`bg-gray-50 rounded-lg p-4 border-l-4 border-${item.color}-600`}>
              <code className={`text-sm font-mono bg-gray-200 px-3 py-1 rounded text-${item.color}-600`}>
                {item.command}
              </code>
              <p className="text-sm text-gray-700 mt-2">{item.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* What to Expect Section */}
      <div className="grid md:grid-cols-3 gap-6 mb-8">
        {[
          {
            icon: '🔔',
            title: 'Real-Time Alerts',
            description: 'Receive instant notifications when new vehicles matching your criteria are listed'
          },
          {
            icon: '✅',
            title: 'Detailed Info',
            description: 'Each listing includes photos, price, mileage, year, and direct seller contact'
          },
          {
            icon: '⚙️',
            title: 'Full Control',
            description: 'Manage criteria, pause/resume notifications, and view subscription status anytime'
          }
        ].map((item) => (
          <div key={item.title} className="card">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-xl">
                {item.icon}
              </div>
              <h3 className="font-bold text-gray-900">{item.title}</h3>
            </div>
            <p className="text-sm text-gray-600">{item.description}</p>
          </div>
        ))}
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
  )
}
