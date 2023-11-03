export class UserFields {
  name: string = '';
  username: string = '';
  password: string = '';
  email: string = '';
  passwordRepeat: string = '';
  agree: boolean = false;
}

export class DestinationFields {
  platform: number = 0;
  name: string = '';
  sort_code: string = '';
  account_number: string = '';
  business: boolean = false;
  card_number: string = '';
  bank_name: string = '';
  public: boolean = true;
  star: boolean = false;
}

export class ApplicationFields {
  category: number = 0;
  department: number = 0;
  budget: number = 0;
  platform: number = 0;
  name: string = '';
  sort_code: string = '';
  account_number: string = '';
  business: boolean = false;
  card_number: string = '';
  bank_name: string = '';
  currency: number = 0;
  amount: number = 0;
  reason: string = '';
  // Event fields
  contents: string = '';
  file: null | Blob = null;
}

export class EventFields {
  action: number = 0;
  contents: string = '';
  file: null | Blob = null;
}

export class IncomeFields {
  category: number = 0;
  department: number = 0;
  budget: number = 0;
  currency: number = 0;
  amount: number = 0;
  reason: string = '';
  // Event fields
  contents: string = '';
  file: null | Blob = null;
}

export class ReceiptFields {
  action: number = 0;
  currency: number = 0;
  amount: number = 0;
  contents: string = '';
  file: null | Blob = null;
}