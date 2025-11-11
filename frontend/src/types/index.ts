export interface User {
  id: string;
  email: string;
  name: string;
  picture?: string;
  oauth_provider: 'google' | 'facebook';
  created_at: string;
}

export interface SubscriptionPlan {
  id: string;
  name: string;
  price: number;
  currency: string;
  duration_months: number;
  features: string[];
  description: string;
}

export interface Subscription {
  id: string;
  user_id: string;
  plan_id: string;
  status: 'active' | 'inactive' | 'cancelled';
  start_date: string;
  end_date: string;
  auto_renew: boolean;
  created_at: string;
}

export interface Payment {
  id: string;
  user_id: string;
  subscription_id: string;
  amount: number;
  currency: string;
  status: 'pending' | 'completed' | 'failed';
  flitt_order_id?: string;
  created_at: string;
  completed_at?: string;
}

export interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  error: string | null;
  loginWithGoogle: (token: string) => Promise<void>;
  loginWithFacebook: (token: string) => Promise<void>;
  logout: () => void;
}
