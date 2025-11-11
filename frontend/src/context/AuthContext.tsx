import React, { createContext, useState, useCallback, ReactNode } from 'react'
import axios from 'axios'
import { User, AuthContextType } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Check if user is already logged in
  React.useEffect(() => {
    const token = localStorage.getItem('token')
    if (token) {
      validateToken(token)
    }
  }, [])

  const validateToken = async (token: string) => {
    try {
      setIsLoading(true)
      const response = await axios.get(`${API_BASE_URL}/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      })
      setUser(response.data.user)
      setError(null)
    } catch (err) {
      localStorage.removeItem('token')
      setUser(null)
    } finally {
      setIsLoading(false)
    }
  }

  const loginWithGoogle = useCallback(async (token: string) => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await axios.post(`${API_BASE_URL}/auth/google-callback`, {
        token
      })

      localStorage.setItem('token', response.data.access_token)
      setUser(response.data.user)
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Google login failed'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const loginWithFacebook = useCallback(async (token: string) => {
    try {
      setIsLoading(true)
      setError(null)

      const response = await axios.post(`${API_BASE_URL}/auth/facebook-callback`, {
        token
      })

      localStorage.setItem('token', response.data.access_token)
      setUser(response.data.user)
    } catch (err: any) {
      const message = err.response?.data?.detail || 'Facebook login failed'
      setError(message)
      throw err
    } finally {
      setIsLoading(false)
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('token')
    setUser(null)
    setError(null)
  }, [])

  const value: AuthContextType = {
    user,
    isLoading,
    error,
    loginWithGoogle,
    loginWithFacebook,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const context = React.useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
