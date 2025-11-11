import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { GoogleLogin, GoogleOAuthProvider } from '@react-oauth/google'
import FacebookLogin from 'react-facebook-login/dist/facebook-login-render-props'
import { AlertCircle, CheckCircle } from 'lucide-react'
import { useAuth } from '../context/AuthContext'

export const RegisterPage: React.FC = () => {
  const { loginWithGoogle, loginWithFacebook, isLoading, error } = useAuth()
  const navigate = useNavigate()
  const [successMessage, setSuccessMessage] = useState('')

  const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''
  const FACEBOOK_APP_ID = import.meta.env.VITE_FACEBOOK_APP_ID || ''

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      await loginWithGoogle(credentialResponse.credential)
      setSuccessMessage('Google login successful!')
      setTimeout(() => navigate('/subscription'), 1500)
    } catch (err) {
      console.error('Google login failed:', err)
    }
  }

  const handleFacebookSuccess = async (response: any) => {
    try {
      await loginWithFacebook(response.accessToken)
      setSuccessMessage('Facebook login successful!')
      setTimeout(() => navigate('/subscription'), 1500)
    } catch (err) {
      console.error('Facebook login failed:', err)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 bg-gradient-to-br from-blue-50 via-white to-cyan-50">
      <div className="w-full max-w-md">
        {/* Card Container */}
        <div className="card">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome to MyAuto
            </h1>
            <p className="text-gray-600">
              Sign up to start finding your perfect vehicle
            </p>
          </div>

          {/* Error Alert */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
              <AlertCircle size={20} className="text-red-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-red-800">Error</h3>
                <p className="text-sm text-red-700">{error}</p>
              </div>
            </div>
          )}

          {/* Success Alert */}
          {successMessage && (
            <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
              <CheckCircle size={20} className="text-green-600 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="font-semibold text-green-800">Success</h3>
                <p className="text-sm text-green-700">{successMessage}</p>
              </div>
            </div>
          )}

          {/* Google Sign In */}
          <div className="mb-4">
            {GOOGLE_CLIENT_ID ? (
              <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
                <div className="w-full flex justify-center">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => console.error('Google login failed')}
                    text="signin_with"
                  />
                </div>
              </GoogleOAuthProvider>
            ) : (
              <button
                disabled
                className="w-full py-3 px-4 bg-gray-100 text-gray-400 rounded-lg font-semibold cursor-not-allowed"
              >
                Google Sign In (Not configured)
              </button>
            )}
          </div>

          {/* Facebook Sign In */}
          <div className="mb-6">
            {FACEBOOK_APP_ID ? (
              <FacebookLogin
                appId={FACEBOOK_APP_ID}
                autoLoad={false}
                fields="name,email,picture"
                callback={handleFacebookSuccess}
                render={(renderProps) => (
                  <button
                    onClick={renderProps.onClick}
                    disabled={isLoading || renderProps.isProcessing}
                    className="btn-oauth disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
                    </svg>
                    Sign in with Facebook
                  </button>
                )}
              />
            ) : (
              <button
                disabled
                className="w-full py-3 px-4 bg-gray-100 text-gray-400 rounded-lg font-semibold cursor-not-allowed"
              >
                Facebook Sign In (Not configured)
              </button>
            )}
          </div>

          {/* Divider */}
          <div className="relative mb-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">Or continue with email</span>
            </div>
          </div>

          {/* Email Sign Up Form */}
          <form className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-semibold text-gray-700 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                placeholder="you@example.com"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-semibold text-gray-700 mb-2">
                Password
              </label>
              <input
                id="password"
                type="password"
                placeholder="••••••••"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition"
              />
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed transition"
            >
              {isLoading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          {/* Terms & Privacy */}
          <p className="text-xs text-gray-600 text-center mt-6">
            By signing up, you agree to our{' '}
            <a href="#" className="text-blue-600 hover:underline">
              Terms of Service
            </a>{' '}
            and{' '}
            <a href="#" className="text-blue-600 hover:underline">
              Privacy Policy
            </a>
          </p>

          {/* Login Link */}
          <p className="text-center text-gray-600 mt-6">
            Already have an account?{' '}
            <a href="#" className="text-blue-600 font-semibold hover:underline">
              Sign In
            </a>
          </p>
        </div>

        {/* Security Info */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="font-semibold text-blue-900 mb-2">🔒 We take your privacy seriously</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>✓ Bank-level SSL encryption</li>
            <li>✓ Your data is never shared</li>
            <li>✓ GDPR & CCPA compliant</li>
          </ul>
        </div>
      </div>
    </div>
  )
}
