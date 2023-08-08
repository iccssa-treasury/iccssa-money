<script lang="ts">
import { api, type Income, type User } from '@/api';
import { messageErrors, user } from '@/state';
import { Department, Level, currency_symbol, level_status, level_icon } from '@/enums';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      user,
      Department, Level,
      currency_symbol, level_status, level_icon,
    };
  },
  data() {
    return {
      loading: true,
      incomes: new Array<Income>(),
      show_completed: false,
      users: new Map<number, string>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.incomes = (await api.get('main/incomes/')).data as Income[];
      for (const user of (await api.get('accounts/users/')).data as User[]) {
        this.users.set(user.pk, user.name??'');
      }
      this.loading = false;
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    display() {
      if (user.value === undefined) return new Array<Income>();
      return this.show_completed ?
        this.incomes :
        this.incomes.filter((income) => income.level === 1);
    },
  }
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">合同列表</h1>
      <table class="ui compact fixed selectable striped single line celled stuck table">
        <thead>
          <tr>
            <th class="two wide">部门</th>
            <th class="eight wide">合同款项</th>
            <th>金额</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <router-link custom v-for="income in display" :key="income.pk" :to="`/income/${income.pk}/`"
            v-slot="{ navigate }">
            <tr @click="navigate">
              <td>{{ Department[income.department] }}</td>
              <td>{{ income.reason }}</td>
              <td>{{ `${currency_symbol(income.currency)}${income.amount}` }}</td>
              <td :class="level_status(income.level)">
                <i class="icon" :class="level_icon(income.level)"></i>
                {{ Level[income.level] }}
              </td>
            </tr>
          </router-link>
        </tbody>
        <tfoot class="full width">
          <tr>
            <th colspan="4">
              <sui-checkbox toggle v-model="show_completed" label="显示全部" />
              <router-link custom to="/incomes/new/" v-slot="{ navigate }">
                <button class="ui right floated small purple button" @click="navigate">新建合同</button>
              </router-link>
            </th>
          </tr>
        </tfoot>
      </table>
    </loading-text>
  </div>
</template>

<style scoped></style>
