<script lang="ts">
import axios from 'axios';
import { api, type User, type Destination } from '@/api';
import { messageErrors, user } from '@/state';
import { FormErrors } from '@/errors';
import { ApplicationFields, EventFields, DestinationFields } from '@/forms';
import { choices, Category, Department, Currency } from '@/enums';

import FileUpload from './components/FileUpload.vue';

export default {
  components: { FileUpload },
  setup() {
    return {
      user,
      choices, Category, Department, Currency
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
        name: [],
        sort_code: [],
        account_number: [],
        business: [],
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
        text: `${dest.star ? '★ ' : ''}${dest.name} - ${dest.sort_code} - ${dest.account_number}`, 
      }));
      this.fields.department = data.department;
    } catch (e) {
      messageErrors(e);
    }
  },
  methods: {
    async submit() {
      if (user.value === undefined) return;
      try {
        this.errors.clear();
        this.waiting = true;
        this.success = false;
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
      dest_fields.name = this.fields.name;
      dest_fields.sort_code = this.fields.sort_code;
      dest_fields.account_number = this.fields.account_number;
      dest_fields.business = this.fields.business;
      await api.post('main/me/destinations/', dest_fields);
    },
    fill() {
      // console.log(this.select_dest);
      if (!this.select_dest) return;
      const dest = this.select_dest.value as Destination;
      this.fields.name = dest.name;
      this.fields.sort_code = dest.sort_code;
      this.fields.account_number = dest.account_number;
      this.fields.business = dest.business;
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
      <div class="field" :class="{ error: errors.fields.amount.length > 0 || errors.fields.currency.length > 0 }">
        <label>申请金额</label>
        <div class="fields">
          <div class="seven wide field" :class="{ error: errors.fields.amount.length > 0 }">
            <input placeholder="0.00" v-model="fields.amount" @input="errors.fields.amount.length = 0">
          </div>
          <div class="three wide field" :class="{ error: errors.fields.currency.length > 0 }">
            <select class="ui selection dropdown" v-model="fields.currency">
              <option v-for="choice in choices(Currency)" :value="choice.value">{{ choice.text }}</option>
            </select>
          </div>
        </div>
      </div>
      <h4 class="ui dividing header">收款账户</h4>
      <div class="fields">
        <div class="fourteen wide field">
          <sui-dropdown search selection v-model="select_dest" :options="destinations" placeholder="从现有账户中搜索…" />
        </div>
        <div class="one wide field">
          <button class="ui icon button" :class="{ disabled: waiting, loading: waiting }" @click.prevent="fill">
            <i class="sync alternate icon"></i>
          </button>
        </div>
      </div>
      <div class="fields">
        <div class="six wide field" :class="{ error: errors.fields.name.length > 0 }">
          <label>Recipient Name</label>
          <input placeholder="Recipient Name" v-model="fields.name" @input="errors.fields.name.length = 0" />
        </div>
        <div class="four wide field" :class="{ error: errors.fields.sort_code.length > 0 }">
          <label>Sort Code</label>
          <input placeholder="Sort Code" maxlength="6" v-model="fields.sort_code"
            @input="errors.fields.sort_code.length = 0" />
        </div>
        <div class="four wide field" :class="{ error: errors.fields.account_number.length > 0 }">
          <label>Account Number</label>
          <input placeholder="Account No." maxlength="8" v-model="fields.account_number"
            @input="errors.fields.account_number.length = 0" />
        </div>
        <div class="two wide field" :class="{ error: errors.fields.business.length > 0 }">
          <label>Business</label>
          <sui-checkbox toggle v-model="fields.business" />
        </div>
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
