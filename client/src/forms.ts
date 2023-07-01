export class UserFields {
  name: string = '';
  username: string = '';
  password: string = '';
  email: string = '';
  passwordRepeat: string = '';
  agree: boolean = false;
}

export class DestinationFields {
  name: string = '';
  sort_code: string = '';
  account_number: string = '';
  business: boolean = false;
  public: boolean = true;
  star: boolean = false;
}

export class ApplicationFields {
  category: number = 0;
  department: number = 0;
  name: string = '';
  sort_code: string = '';
  account_number: string = '';
  business: boolean = false;
  currency: number = 0;
  amount: number | null = null;
  reason: string = '';

  contents: string = '';
}

export class EventFields {
  action: number = 0;
  contents: string = '';
}