import axios from 'axios'
import { SubscriptionPlan, Subscription, Payment } from '../types'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const subscriptionService = {
  getPlans: async (): Promise<SubscriptionPlan[]> => {
    const { data } = await apiClient.get('/subscriptions/plans')
    return data.plans
  },

  getUserSubscription: async (userId: string): Promise<Subscription | null> => {
    try {
      const { data } = await apiClient.get(`/subscriptions/${userId}`)
      return data.subscription
    } catch (error) {
      return null
    }
  },

  createSubscription: async (planId: string): Promise<Subscription> => {
    const { data } = await apiClient.post('/subscriptions', { plan_id: planId })
    return data.subscription
  }
}

export const paymentService = {
  initiatePayment: async (
    subscriptionId: string,
    amount: number,
    currency: string = 'GEL'
  ): Promise<{ order_id: string; redirect_url: string }> => {
    const { data } = await apiClient.post('/payments/initiate', {
      subscription_id: subscriptionId,
      amount,
      currency
    })
    return data
  },

  checkPaymentStatus: async (orderId: string): Promise<Payment> => {
    const { data } = await apiClient.get(`/payments/status/${orderId}`)
    return data.payment
  },

  completePayment: async (orderId: string): Promise<Payment> => {
    const { data } = await apiClient.post(`/payments/complete/${orderId}`)
    return data.payment
  }
}

export default apiClient
