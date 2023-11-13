<script lang="ts">
import axios from 'axios';
import { api, type User, type Budget } from '@/api';
import { messageErrors, user } from '@/state';
import { FormErrors } from '@/errors';
import { IncomeFields } from '@/forms';
import { choices, Department, Currency, Source } from '@/enums';

import FilesUpload from './components/FilesUpload.vue';

export default {
  components: { FilesUpload },
  setup() {
    return {
      user,
      choices, Department, Currency, Source,
    };
  },
  data() {
    return {
      success: false,
      waiting: false,
      fields: new IncomeFields(),
      budgets: new Array<Budget>(),
      errors: new FormErrors<IncomeFields>({
        category: [],
        department: [],
        budget: [],
        currency: [],
        amount: [],
        reason: [],
        contents: [],
        files: [],
      }),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.budgets = (await api.get('main/budgets/')).data as Budget[];
      this.fields.department = data.department;
      this.fields.budget = this.filtered_budgets[0].value;
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
    filtered_budgets() {
      return this.budgets
        .filter((budget) => budget.department === this.fields.department)
        .map((budget) => ({ value: budget.pk, text: budget.reason }));
    }
  },
  methods: {
    async submit() {
      if (user.value === undefined) return;
      try {
        this.errors.clear();
        this.waiting = true;
        this.success = false;
        await api.post('main/incomes/new/', this.fields, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        // manual clear
        this.fields = new IncomeFields();
        this.fields.department = user.value.department;
        this.fields.budget = this.filtered_budgets[0].value;
        this.success = true;
      } catch (e) {
        if (axios.isAxiosError(e)) this.errors.decode(e);
        else messageErrors(e);
      }
      this.waiting = false;
    },
  },
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <h1 class="ui header">创建收款合同</h1>
    <form class="ui form">
      <h4 class="ui dividing header">基础信息</h4>
      <div class="fields">
        <div class="three wide field" :class="{ error: errors.fields.category.length > 0 }">
          <label>财务类目</label>
          <select class="ui selection dropdown" v-model="fields.category">
            <option v-for="choice in choices(Source)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
        <div class="ten wide field" :class="{ error: errors.fields.reason.length > 0 }">
          <label>合同标题</label>
          <input placeholder="实体名称..." v-model="fields.reason" @input="errors.fields.reason.length = 0" />
        </div>
      </div>
      <div class="fields">
        <div class="three wide field" :class="{ error: errors.fields.department.length > 0 }">
          <label>所属部门</label>
          <select class="ui selection dropdown" v-model="fields.department">
            <option v-for="choice in choices(Department)" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
        <div class="seven wide field" :class="{ error: errors.fields.budget.length > 0 }">
          <label>预算方案</label>
          <select class="ui selection dropdown" v-model="fields.budget">
            <option v-for="choice in filtered_budgets" :value="choice.value">{{ choice.text }}</option>
          </select>
        </div>
      </div>
      <div class="field" :class="{ error: errors.fields.amount.length > 0 || errors.fields.currency.length > 0 }">
        <label>应收金额</label>
        <div class="fields">
          <div class="seven wide field" :class="{ error: errors.fields.amount.length > 0 }">
            <input placeholder="0.00" v-model="computed_amount" @input="errors.fields.amount.length = 0">
          </div>
          <div class="three wide field" :class="{ error: errors.fields.currency.length > 0 }">
            <select class="ui selection dropdown" v-model="fields.currency">
              <option v-for="choice in choices(Currency)" :value="choice.value">{{ choice.text }}</option>
            </select>
          </div>
        </div>
      </div>
      <h4 class="ui dividing header">辅助信息</h4>
      <div class="field">
        <label>备注</label>
        <textarea placeholder="补充合同详细信息…" rows="10" style="resize: vertical" v-model="fields.contents"></textarea>
      </div>
      <div class="field">
        <label>附件</label>
        <files-upload v-model="fields.files" />
      </div>
      <button class="ui purple button" :class="{ disabled: waiting, loading: waiting }" @click.prevent="submit">
        上传合同
      </button>
    </form>

    <div v-if="success" class="ui success icon message">
      <p>合同已上传，请到收入记录列表中查看。</p>
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
