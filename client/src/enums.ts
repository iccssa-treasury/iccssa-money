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
  主席团 = 0,
  秘书处 = 1,
  财务处 = 2,
  事业部 = 3,
  媒体部 = 4,
  赞助部 = 5,
  文艺部 = 6,
  文化部 = 7,
  外联部 = 8,
  体育部 = 9,
  未分配 = 10,
}

export enum Category {
  报销 = 0,
  付款 = 1,
  预支 = 2,
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
  备注 = 0,
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

export function currency_symbol(currency: Currency) {
  switch (currency) {
    case 0: return '£';
    case 1: return '¥';
  }
}