import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { LogOut, Menu, X } from 'lucide-react'

export const Header: React.FC = () => {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [isMenuOpen, setIsMenuOpen] = React.useState(false)

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  return (
    <header className="sticky top-0 z-50 bg-white shadow-md">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="flex items-center gap-2">
            <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-cyan-500 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-lg">MA</span>
            </div>
            <span className="gradient-text font-bold text-xl hidden sm:inline">MyAuto</span>
          </Link>

          {/* Desktop Menu */}
          <div className="hidden md:flex items-center gap-8">
            <Link to="/" className="text-gray-700 hover:text-blue-600 transition">
              Home
            </Link>
            {user && (
              <Link to="/dashboard" className="text-gray-700 hover:text-blue-600 transition">
                Dashboard
              </Link>
            )}
          </div>

          {/* User Section */}
          <div className="flex items-center gap-4">
            {user ? (
              <>
                <div className="hidden sm:flex items-center gap-3">
                  {user.picture && (
                    <img src={user.picture} alt={user.name} className="w-8 h-8 rounded-full" />
                  )}
                  <span className="text-sm font-medium text-gray-700">{user.name}</span>
                </div>
                <button
                  onClick={handleLogout}
                  className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition"
                >
                  <LogOut size={20} />
                </button>
              </>
            ) : (
              <Link to="/register" className="btn-primary hidden sm:block">
                Sign In
              </Link>
            )}

            {/* Mobile Menu Button */}
            <button
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X size={24} /> : <Menu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <div className="md:hidden mt-4 pb-4 border-t">
            <Link to="/" className="block py-2 text-gray-700 hover:text-blue-600">
              Home
            </Link>
            {user ? (
              <>
                <Link to="/dashboard" className="block py-2 text-gray-700 hover:text-blue-600">
                  Dashboard
                </Link>
                <button
                  onClick={handleLogout}
                  className="w-full text-left py-2 text-red-600 hover:text-red-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <Link to="/register" className="block py-2 text-blue-600 font-semibold">
                Sign In
              </Link>
            )}
          </div>
        )}
      </nav>
    </header>
  )
}
