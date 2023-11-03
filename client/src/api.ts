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

export interface Json {
  [key: string]: any;
}

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
  budgeteer: boolean;
  notification_settings: Json;
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
  platform: number;
  name: string;
  sort_code: string;
  account_number: string;
  business: boolean;
  card_number: string;
  bank_name: string;
  public: boolean;
  star: boolean;
}

export interface Budget {
  pk: number;
  user: number;
  department: number;
  level: number;
  reason: string;
  description: string;
  file: string;
  amount: number;
  spent: number;
  spent_actual: Json;
  profit: number;
  received: number;
  received_actual: Json;
}

export interface Application {
  pk: number;
  user: number;
  department: number;
  category: number;
  budget: number;
  platform: number;
  name: string;
  sort_code: string;
  account_number: string;
  business: boolean;
  card_number: string;
  bank_name: string;
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
  category: number;
  budget: number;
  currency: number;
  amount: number;
  reason: string;
  received: Json;
  level: number;
}

export interface Receipt {
  pk: number;
  user: number;
  income: number;
  timestamp: string;
  action: number;
  currency: number;
  amount: number;
  contents: string;
  file: string;
}

export function destination_display(destination: Destination | Application): string {
  switch (destination.platform) {
    case 0: // BANK_GBP
      return `${destination.name} - ${destination.sort_code} - ${destination.account_number}`;
    case 1: // BANK_CNY
      return `${destination.name} - ${destination.card_number} [${destination.bank_name}]`;
    default: // ALIPAY, WECHAT
      return `${destination.name} - ${destination.card_number}`;
  }
}

export function filename_display(file: string): string {
  if (file === null || file === undefined) return '';
  const filename = file.substring(file.lastIndexOf('/') + 1);
  const query = filename.indexOf('?');
  return decodeURIComponent(query === -1 ? filename : filename.substring(0, query));
}