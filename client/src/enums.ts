import type { Json } from './api';

export type Choice = { value: number; text: string }
export function choices(e: any): Choice[] {
  return Object.keys(e).filter(i => isNaN(Number(i))).map(k => ({ value: e[k], text: k }));
}

export enum Privilege {
  审计 = 1,
  主席 = 2,
  执委 = 3,
  部员 = 4,
  访客 = 5,
}

export enum Department {
  未分配 = 0,
  主席团 = 1,
  秘书处 = 2,
  财务处 = 3,
  事业部 = 4,
  媒体部 = 5,
  赞助部 = 6,
  文艺部 = 7,
  文化部 = 8,
  外联部 = 9,
  体育部 = 10,
}

export enum Category {
  报销 = 0,
  付款 = 1,
  预支 = 2,
}

export enum Source {
  合同 = 0,
  活动 = 1,
  换汇 = 2,
  退款 = 3,
}

export enum Level {
  已取消 = -1,
  已完成 = 0,
  待付款 = 1,
  待财务审批 = 2,
  待主席审批 = 3,
  待部门审批 = 4,
  待成员审批 = 5,
}

export function level_status(level: Level) {
  switch (level) {
    case -1: return 'negative';
    case 0: return 'positive';
    default: return 'warning';
  }
}

export function level_icon(level: Level) {
  switch (level) {
    case -1: return 'times';
    case 0: return 'check';
    case 1: return 'comment dollar';
    default: return 'clock';
  }
}

export enum Action {
  评论 = 0,
  批准 = 1,
  驳回 = 2,
  创建 = 3,
  撤销 = 4,
  完成 = 5,
}

export enum Currency {
  英镑 = 0,
  人民币 = 1,
}

export enum Platform {
  银行转帐 = 1,
  支付宝 = 2,
  微信支付 = 3,
}

export function currency_symbol(currency: Currency) {
  switch (currency) {
    case 0: return '£';
    case 1: return '¥';
  }
}

export function display_amount(currency: Currency, amount: number) {
  return currency_symbol(currency) + (amount/100).toFixed(2);
}

export function received_amount(received: Json, default_currency: Currency) {
  const amounts = [0,1].map(i => received[Currency[i]]);
  const displays = [0,1].map(i => display_amount(i, amounts[i]));
  const display = displays.filter((_, i) => amounts[i])
  return display.length ? display.join(' + ') : displays[default_currency];
}