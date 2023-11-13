<script lang="ts">
import { api, type User, type File, type Application, type Income, type Budget, filename_display } from '@/api';
import { messageErrors, user } from '@/state';
import { Category, Currency, Level, Department, Source, display_amount, received_amount, level_status, level_icon } from '@/enums';

import FileLink from './components/FileLink.vue';

export default {
  components: { FileLink },
  setup() {
    return {
      user,
      Category, Currency, Level, Department, Source,
      filename_display,
      display_amount, received_amount, level_status, level_icon
    };
  },
  props: {
    pk: { type: String, required: true },
  },
  data() {
    return {
      waiting: false,
      budget: null as Budget | null,
      applications: new Array<Application>(),
      incomes: new Array<Income>(),
      users: new Map<number, string>(),
      plan: null as File | null,
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.budget = (await api.get(`main/budget/${this.pk}/`)).data as Budget;
      this.applications = (await api.get(`main/budget/${this.pk}/applications/`)).data as Application[];
      this.incomes = (await api.get(`main/budget/${this.pk}/incomes/`)).data as Income[];
      if (this.budget.plan !== null)
        this.plan = (await api.get(`main/budget/${this.pk}/plan/`)).data as File;
      for (const user of (await api.get('accounts/users/')).data as User[]) {
        this.users.set(user.pk, user.name??'');
      }
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    applications_display() {
      return this.applications.filter((application) => application.level >= 0);
    },
    incomes_display() {
      return this.incomes.filter((income) => income.level >= 0);
    },
    show_spending_bar() {
      return this.budget?.amount! > 0;
    },
    show_application_table() {
      return this.applications_display.length > 0;
    },
    remaining_percentage() {
      return (100 - this.budget?.spent! / this.budget?.amount! * 100).toFixed(1);
    },
    remaining_label() {
      const spent = display_amount(Currency.英镑, this.budget?.amount! - this.budget?.spent!);
      const amount = display_amount(Currency.英镑, this.budget?.amount!);
      return `可用余额 ${spent} / ${amount}`
    },
    show_income_bar() {
      return this.budget?.profit! > 0;
    },
    show_income_table() {
      return this.incomes_display.length > 0;
    },
    received_percentage() {
      return (this.budget?.received! / this.budget?.profit! * 100).toFixed(1);
    },
    received_label() {
      const received = display_amount(Currency.英镑, this.budget?.received!);
      const profit = display_amount(Currency.英镑, this.budget?.profit!);
      return `合计收入 ${received} / ${profit}`
    },
  }
};
</script>

<template>
  <div v-if="user !== undefined && budget !== null" class="ui text container"
    style="padding: 1em 0; min-height: 80vh">
    <h1 class="ui header">
      <div class="content">
        {{ `${budget.reason} #${budget.pk}` }}
      </div>
      <div class="sub header">
        {{ budget.description }}
        <file-link v-if="plan" :file="plan" />
      </div>
    </h1>
    <table class="ui definition table">
      <thead></thead>
      <tbody>
        <tr>
          <td class="three wide">所属部门</td>
          <td>{{ Department[budget.department] }}</td>
        </tr>
        <tr>
          <td>负责人</td>
          <td>{{ users.get(budget.user) }}</td>
        </tr>
        <tr>
          <td>支出金额</td>
          <td>{{ received_amount(budget.spent_actual, Currency.英镑) }}</td>
        </tr>
        <tr>
          <td>收入金额</td>
          <td>{{ received_amount(budget.received_actual, Currency.英镑) }}</td>
        </tr>
      </tbody>
    </table>
    <sui-progress 
      v-if="show_spending_bar"
      :percent="remaining_percentage"
      :label="remaining_label"
      class="right aligned"
      indicating
      progress
    />
    <sui-progress v-if="!show_spending_bar && show_application_table" />
    <table
      v-if="show_application_table"
      class="ui compact fixed selectable striped single line celled stuck table">
      <thead>
        <tr>
          <th class="two wide">类目</th>
          <th class="two wide">申请人</th>
          <th>事由</th>
          <th class="three wide">金额</th>
          <th class="three wide">状态</th>
        </tr>
      </thead>
      <tbody>
        <router-link custom v-for="application in applications_display" :key="application.pk" :to="`/application/${application.pk}/`"
          v-slot="{ navigate }">
          <tr @click="navigate">
            <td>{{ Category[application.category] }}</td>
            <td>
              <!-- <img class="ui bordered avatar image" :src="users.get(application.user)?.avatar" /> -->
              {{ users.get(application.user) }}
            </td>
            <td>{{ application.reason }}</td>
            <td>{{ display_amount(application.currency, application.amount) }}</td>
            <td :class="level_status(application.level)">
              <i class="icon" :class="level_icon(application.level)"></i>
              {{ Level[application.level] }}
            </td>
          </tr>
        </router-link>
      </tbody>
    </table>
    <sui-progress 
      v-if="show_income_bar"  
      :percent="received_percentage" 
      :label="received_label"
      color="purple"
      active
      progress 
    />
    <sui-progress v-if="!show_income_bar && show_income_table" />
    <table 
      v-if="show_income_table"
      class="ui compact fixed selectable striped single line celled stuck table">
      <thead>
        <tr>
          <th class="two wide">类目</th>
          <th class="two wide">负责人</th>
          <th>事由</th>
          <th class="three wide">收款</th>
          <th class="three wide">状态</th>
        </tr>
      </thead>
      <tbody>
        <router-link custom v-for="income in incomes_display" :key="income.pk" :to="`/income/${income.pk}/`"
          v-slot="{ navigate }">
          <tr @click="navigate">
            <td>{{ Source[income.category] }}</td>
            <td>{{ users.get(income.user) }}</td>
            <td>{{ income.reason }}</td>
            <td>{{ received_amount(income.received, income.currency) }}</td>
            <td :class="level_status(income.level)">
              <i class="icon" :class="level_icon(income.level)"></i>
              {{ Level[income.level] }}
            </td>
          </tr>
        </router-link>
      </tbody>
    </table>
  </div>
</template>
