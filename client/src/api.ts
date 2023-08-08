import axios from 'axios';

// API client configuration.

export const api = axios.create({
  baseURL: 'http://localhost:8000/api/',
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFTOKEN',
  xsrfCookieName: 'csrftoken',
  // timeout: 10000,
});

// API schemas.

export interface User {
  pk: number;
  username: string;
  password: string | null;
  name: string | null;
  email: string | null;
  admin: boolean;
  approval_level: number;
  application_level: number;
  department: number;
  representative: boolean;
  avatar: string;
  bio: string;
  date_joined: string;
  last_login: string;
}

export interface Credential {
  username: string;
  password: string;
}

export interface Destination {
  pk: number;
  user: number;
  name: string;
  sort_code: string;
  account_number: string;
  business: boolean;
  public: boolean;
  star: boolean;
}

export interface Application {
  pk: number;
  user: number;
  department: number;
  category: number;
  name: string;
  sort_code: string;
  account_number: string;
  business: boolean;
  currency: number;
  amount: number;
  reason: string;
  level: number;
}

export interface Event {
  pk: number;
  user: number;
  application: number;
  timestamp: string;
  action: number;
  contents: string;
  file: string;
}

export interface Income {
  pk: number;
  user: number;
  department: number;
  currency: number;
  amount: number;
  reason: string;
  received: number;
  level: number;
}

export interface Receipt {
  pk: number;
  user: number;
  income: number;
  timestamp: string;
  action: number;
  amount: number;
  contents: string;
  file: string;
}