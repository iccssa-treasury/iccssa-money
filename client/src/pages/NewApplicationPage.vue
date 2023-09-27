<script lang="ts">
import axios from 'axios';
import { api, type User, type Destination, destination_display } from '@/api';
import { messageErrors, user } from '@/state';
import { FormErrors } from '@/errors';
import { ApplicationFields, DestinationFields } from '@/forms';
import { choices, Category, Department, Currency, Platform } from '@/enums';

import FileUpload from './components/FileUpload.vue';

export default {
  components: { FileUpload },
  setup() {
    return {
      user,
      choices, Category, Department, Currency, Platform,
      destination_display
    };
  },
  data() {
    return {
      success: false,
      waiting: false,
      fields: new ApplicationFields(),
      destinations: new Array(),
      select_dest: null as { value: Destination, text: String } | null,
      save_dest: false,
      errors: new FormErrors<ApplicationFields>({
        category: [],
        department: [],
        platform: [],
        name: [],
        sort_code: [],
        account_number: [],
        business: [],
        card_number: [],
        bank_name: [],
        currency: [],
        amount: [],
        reason: [],
        contents: [],
        file: [],
      }),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      const destinations = (await api.get('main/destinations/')).data as Destination[];
      this.destinations = destinations.map((dest) => ({ 
        value: dest, 
        text: `${dest.star ? '★ ' : ''}${destination_display(dest)}`, 
      }));
      this.fields.department = data.department;
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    computed_amount: {
      get() {
        return this.fields.amount === 0? '': this.fields.amount / 100;
      },
      set(value: number) {
        this.fields.amount = Math.round(value * 100);
      },
    },
    name_caption() {
      return this.fields.currency === 0? 'Recipient Name': '收款人姓名';
    },
    card_number_caption() {
      return ['Card Number', '银行卡号', '支付宝账号', '微信号'][this.fields.platform];
    },
    filtered_destinations() {
      return this.destinations.filter((dest) => dest.value.platform === this.fields.platform);
    }
  },
  methods: {
    async submit() {
      if (user.value === undefined) return;
      try {
        this.errors.clear();
        this.waiting = true;
        this.success = false;
        this.trim_destination();
        await api.post('main/applications/new/', this.fields, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        if (this.save_dest) await this.save();
        // manual clear
        this.fields = new ApplicationFields();
        this.fields.department = user.value.department;
        this.select_dest = null;
        this.save_dest = false;
        this.success = true;
      } catch (e) {
        if (axios.isAxiosError(e)) this.errors.decode(e);
        else messageErrors(e);
      }
      this.waiting = false;
    },
    async save() {
      const dest_fields = new DestinationFields();
      dest_fields.platform = this.fields.platform;
      dest_fields.name = this.fields.name;
      dest_fields.sort_code = this.fields.sort_code;
      dest_fields.account_number = this.fields.account_number;
      dest_fields.business = this.fields.business;
      dest_fields.card_number = this.fields.card_number;
      dest_fields.bank_name = this.fields.bank_name;
      await api.post('main/me/destinations/', dest_fields);
    },
    trim_destination() {
      if (this.fields.platform > 0) {
        this.fields.sort_code = '';
        this.fields.account_number = '';
        this.fields.business = false;
      }
      if (this.fields.platform === 0) this.fields.card_number = '';
      if (this.fields.platform !== 1) this.fields.bank_name = '';
    },
    switch_currency() {
      this.fields.platform = this.fields.currency;
    },
    fill() {
      // console.log(this.select_dest);
      if (!this.select_dest) return;
      const dest = this.select_dest.value as Destination;
      this.fields.name = dest.name;
      this.fields.sort_code = dest.sort_code;
      this.fields.account_number = dest.account_number;
      this.fields.business = dest.business;
      this.fields.card_number = dest.card_number;
      this.fields.bank_name = dest.bank_name;
    },
  },
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <h1 class="ui header">创建{{ Category[fields.category] }}申请</h1>
    <form class="ui form">
      <h4 class="ui dividing header">基础信息</h4>
      <div class="fields">
        <div class="ten wide field" :class="{ error: errors.fields.reason.length > 0 }">
          <label>申请事由</label>
          <input placeholder="资金用途..." v-model="fields.reason" @input="errors.fields.reason.length = 0" />
        </div>
        <div class="three wide field" :class="{ error: errors.fields.category.length > 0 }">
          <label>财务类目</label>
          <select class="ui selection dropdown" v-model="fields.category">
            <option v-for="choice in choices(Category)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
        <div class="three wide field" :class="{ error: errors.fields.department.length > 0 }">
          <label>所属部门</label>
          <select class="ui selection dropdown" v-model="fields.department">
            <option v-for="choice in choices(Department)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
      </div>
      <div class="fields">
        <div class="seven wide field" :class="{ error: errors.fields.amount.length > 0 }">
          <label>申请金额</label>
          <input placeholder="0.00" v-model="computed_amount" @input="errors.fields.amount.length = 0">
        </div>
        <div class="three wide field" :class="{ error: errors.fields.currency.length > 0 }">
          <label>币种</label>
          <select class="ui selection dropdown" v-model="fields.currency" @change="switch_currency">
            <option v-for="choice in choices(Currency)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
        <div class="three wide field" v-if="fields.currency">
          <label>收款方式</label>
          <select class="ui selection dropdown" v-model="fields.platform">
            <option v-for="choice in choices(Platform)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
      </div>
      <h4 class="ui dividing header">收款账户</h4>
      <div class="fields">
        <div class="fourteen wide field">
          <sui-dropdown search selection v-model="select_dest" :options="filtered_destinations" placeholder="从现有账户中搜索…" />
        </div>
        <div class="one wide field">
          <button class="ui icon button" :class="{ disabled: waiting, loading: waiting }" @click.prevent="fill">
            <i class="sync alternate icon"></i>
          </button>
        </div>
      </div>
      <div class="fields">
        <div class="six wide field" :class="{ error: errors.fields.name.length > 0 }">
          <label>{{ name_caption }}</label>
          <input :placeholder="name_caption" v-model="fields.name" @input="errors.fields.name.length = 0" />
        </div>
        <div v-if="!fields.platform" class="four wide field" :class="{ error: errors.fields.sort_code.length > 0 }">
          <label>Sort Code</label>
          <input placeholder="Sort Code" maxlength="6" v-model="fields.sort_code"
            @input="errors.fields.sort_code.length = 0" />
        </div>
        <div v-if="!fields.platform" class="four wide field" :class="{ error: errors.fields.account_number.length > 0 }">
          <label>Account Number</label>
          <input placeholder="Account No." maxlength="8" v-model="fields.account_number"
            @input="errors.fields.account_number.length = 0" />
        </div>
        <div v-if="!fields.platform" class="two wide field" :class="{ error: errors.fields.business.length > 0 }">
          <label>Business</label>
          <sui-checkbox toggle v-model="fields.business" />
        </div>
        <div v-if="fields.platform" class="ten wide field" :class="{ error: errors.fields.card_number.length > 0 }">
          <label>{{ card_number_caption }}</label>
          <input :placeholder="card_number_caption" v-model="fields.card_number" @input="errors.fields.card_number.length = 0" />
        </div>
      </div>
      <div v-if="fields.platform === 1" class="field" :class="{ error: errors.fields.bank_name.length > 0 }">
        <label>开户行名称</label>
        <input placeholder="开户行名称" v-model="fields.bank_name" @input="errors.fields.bank_name.length = 0" />
      </div>
      <div class="field">
        <sui-checkbox toggle v-model="save_dest" label="保存到我的账户列表" />
      </div>
      <h4 class="ui dividing header">辅助信息</h4>
      <div class="field">
        <label>备注</label>
        <textarea placeholder="补充申请详细信息…" rows="10" style="resize: vertical" v-model="fields.contents"></textarea>
      </div>
      <div class="field">
        <label>附件</label>
        <file-upload v-model="fields.file" />
      </div>
      <button class="ui primary button" :class="{ disabled: waiting, loading: waiting }" @click.prevent="submit">
        提交申请
      </button>
    </form>

    <div v-if="success" class="ui success icon message">
      <p>申请已提交，请到报销申请列表中查看。</p>
    </div>

    <div v-if="errors.all.length > 0" class="ui error icon message">
      <i class="info icon" />
      <div class="content">
        <ul class="ui bulleted list">
          <li v-for="error of errors.all" :key="error" class="item">
            {{ error }}
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ui.dropdown:not(.search) {
  padding: 0.5em 0.5em !important;
}
</style>
