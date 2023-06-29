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
  personal: boolean;
  business: boolean;
  last_usage: string;
}

export interface Application {
  pk: number;
  user: number;
  destination: number;
  department: number;
  category: number;
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
