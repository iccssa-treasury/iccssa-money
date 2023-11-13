<script lang="ts">
import { api, type User, type File, type Receipt, type Income, type Budget } from '@/api';
import { messageErrors, user } from '@/state';
import { ReceiptFields } from '@/forms';
import { Action, Currency, Level, Department, currency_symbol, display_amount, received_amount, level_status, level_icon } from '@/enums';
import defaultAvatar from '@/assets/default-avatar.png';

import ApplicationEvent from './components/ApplicationEvent.vue';
import FilesUpload from './components/FilesUpload.vue';

export default {
  components: { ApplicationEvent, FilesUpload },
  setup() {
    return {
      user,
      Action, Currency, Level, Department, 
      currency_symbol, display_amount, received_amount, level_status, level_icon
    };
  },
  props: {
    pk: { type: String, required: true },
  },
  data() {
    return {
      waiting: false,
      income: null as Income | null,
      receipts: new Array<Receipt>(),
      budget: null as Budget | null,
      users: new Map<number, User>(),
      receipt_fields: new ReceiptFields(),
      files: new Map<number, File>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.income = (await api.get(`main/income/${this.pk}/`)).data as Income;
      this.receipt_fields.currency = this.income.currency;
      this.receipts = (await api.get(`main/income/${this.pk}/receipts/`)).data as Receipt[];
      for (const file of (await api.get(`main/income/${this.pk}/files/`)).data as File[])
        this.files.set(file.pk, file);
      if (this.income.budget !== null)
        this.budget = (await api.get(`main/budget/${this.income.budget}/`)).data as Budget;
      for (const user of (await api.get('accounts/users/')).data as User[])
        this.users.set(user.pk, user);
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    can_cancel() {
      if (user.value === undefined || this.income === null) return false;
      return user.value.pk === this.income.user && this.income.level > 0;
    },
    has_receive_access() {
      if (user.value === undefined || this.income === null) return false;
      return user.value.approval_level === 1 && this.income.level > 0;
    },
    can_receive_full() {
      return this.has_receive_access && 
        this.receipt_fields.currency === this.income?.currency && 
        this.income?.received[Currency[1 - this.income?.currency]] === 0;
    },
    can_complete() {
      return this.has_receive_access && 
        (this.income?.received[Currency[this.income?.currency]] === this.income?.amount ||
          this.income?.received[Currency[1 - this.income?.currency]] > 0);
    },
    can_receive() {
      return this.has_receive_access && this.receipt_fields.amount > 0;
    },
    computed_amount: {
      get() {
        return this.receipt_fields.amount === 0? '': this.receipt_fields.amount / 100;
      },
      set(value: number) {
        this.receipt_fields.amount = Math.round(value * 100);
      },
    },
  },
  methods: {
    async receipt(income: string, action: number) {
      try {
        this.waiting = true;
        this.receipt_fields.action = action;
        await api.post(`main/income/${income}/receipts/`, this.receipt_fields, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        // manual update
        this.income = (await api.get(`main/income/${this.pk}/`)).data as Income;
        this.receipts = (await api.get(`main/income/${this.pk}/receipts/`)).data as Receipt[];
        this.budget = (await api.get(`main/budget/${this.income.budget}/`)).data as Budget;
        for (const file of (await api.get(`main/income/${this.pk}/files/`)).data as File[])
          this.files.set(file.pk, file);
        this.receipt_fields = new ReceiptFields();
      } catch (e) {
        messageErrors(e);
      }
      this.waiting = false;
    },
    switch_currency() {
      this.receipt_fields.currency = 1 - this.receipt_fields.currency;
    },
    receive_full() {
      this.receipt_fields.amount = this.income?.amount! - this.income?.received[Currency[this.income?.currency]];
    },
    avatar(pk: number) {
      return this.users.get(pk)?.avatar ?? defaultAvatar;
    },
  },
};
</script>

<template>
  <div v-if="user !== undefined && income !== null" class="ui text container"
    style="padding: 1em 0; min-height: 80vh">
    <h1 class="ui header">
      <div class="content">
        {{ `${income.reason} #${income.pk}` }}
      </div>
    </h1>
    <table class="ui definition table">
      <thead></thead>
      <tbody>
        <tr>
          <td class="three wide">所属部门</td>
          <td>{{ Department[income.department] }}</td>
        </tr>
        <tr>
          <td>负责人</td>
          <td>{{ users.get(income.user)?.name }}</td>
        </tr>
        <tr>
          <td>预算方案</td>
          <td>{{ budget?.reason ?? "[未分配]" }}</td>
        </tr>
        <tr>
          <td>应收金额</td>
          <td>{{ display_amount(income.currency, income.amount) }}</td>
        </tr>
        <tr>
          <td>实收金额</td>
          <td>{{ received_amount(income.received, income.currency) }}</td>
        </tr>
        <tr>
          <td>当前状态</td>
          <td :class="level_status(income.level)">
            <i class="icon" :class="level_icon(income.level)"></i>
            {{ Level[income.level] }}
          </td>
        </tr>
        <tr v-if="has_receive_access">
          <td>确认收款</td>
          <td>
            <div class="ui labeled action input">
              <label for="amount" class="ui label" @click="switch_currency">{{ currency_symbol(receipt_fields.currency) }}</label>
              <input placeholder="0.00" v-model="computed_amount" id="amount">
              <button class="ui teal button" @click="receive_full" :disabled="!can_receive_full">
                <i class="check icon"></i>全额收款
              </button>
            </div>
          </td>
        </tr>
        <tr>
          <td>添加评论</td>
          <td>
            <div class="ui form">
              <div class="field">
                <textarea placeholder="添加评论…" v-model="receipt_fields.contents" rows="3"></textarea>
              </div>
            </div>
          </td>
        </tr>
        <tr>
          <td>添加附件</td>
          <td>
            <files-upload v-model="receipt_fields.files" />
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td colspan="2">
            <button v-if="can_cancel" class="ui primary orange button" :class="{ disabled: waiting, loading: waiting }"
              @click="receipt(pk, 4)">
              <i class="times icon"></i>删除
            </button>
            <button v-if="can_complete" class="ui primary positive button" :class="{ disabled: waiting, loading: waiting }"
              @click="receipt(pk, 5)">
              <i class="check icon"></i>完成
            </button>
            <button v-if="!can_receive" class="ui right floated primary button" :class="{ disabled: waiting, loading: waiting }"
              @click="receipt(pk, 0)">
              <i class="comment icon"></i>评论
            </button>
            <button v-if="can_receive" class="ui right floated green button" :class="{ disabled: waiting, loading: waiting }"
              @click="receipt(pk, 0)">
              <i class="piggy bank icon"></i>收款
            </button>
          </td>
        </tr>
      </tfoot>
    </table>
    <div class="ui big comments">
      <!-- <h2 class="ui dividing header">合同时间线</h2> -->
      <div v-for="receipt in receipts" :key="receipt.pk" class="item">
        <application-event
          :time="receipt.timestamp"
          :avatar="avatar(receipt.user)"
          :name="users.get(receipt.user)?.name??''"
          :action="Action[receipt.action]"
          :display_amount="display_amount(receipt.currency, receipt.amount)"
          :amount="receipt.amount"
          :contents="receipt.contents"
          :files="receipt.files.map(pk => files.get(pk)!)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>.ui.dropdown:not(.search) {
  padding: 0.5em 0.5em !important;
}</style>
