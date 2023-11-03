<script lang="ts">
import { api, type Budget, type User } from '@/api';
import { messageErrors, user } from '@/state';
import { Department, Currency, display_amount } from '@/enums';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      user,
      Department, Currency, display_amount,
    };
  },
  data() {
    return {
      loading: true,
      budgets: new Array<Budget>(),
      show_all: false,
      users: new Map<number, string>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.budgets = (await api.get('main/budgets/')).data as Budget[];
      for (const user of (await api.get('accounts/users/')).data as User[]) {
        this.users.set(user.pk, user.name??'');
      }
      this.loading = false;
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    title() {
      return this.show_all ? '全部门' : Department[user.value?.department!];
    },
    filtered_budgets() {
      return this.budgets.filter(budget => this.show_all || budget.department === user.value?.department);
    }
  },
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">{{ show_all ? '全部门' : Department[user?.department!] }}预算列表</h1>
      <table class="ui compact fixed selectable striped single line celled stuck table">
        <thead>
          <tr>
            <th class="two wide">部门</th>
            <th class="two wide">负责人</th>
            <th>项目</th>
            <th class="three wide">预算额度</th>
            <th class="three wide">支出总额</th>
          </tr>
        </thead>
        <tbody>
          <router-link custom v-for="budget in filtered_budgets" :key="budget.pk" :to="`/budget/${budget.pk}/`"
            v-slot="{ navigate }">
            <tr @click="navigate">
              <td>{{ Department[budget.department] }}</td>
              <td>
                <!-- <img class="ui bordered avatar image" :src="users.get(application.user)?.avatar" /> -->
                {{ users.get(budget.user) }}
              </td>
              <td>{{ budget.reason }}</td>
              <td>{{ budget.amount > 0 ? display_amount(Currency.英镑, budget.amount) : '—' }}</td>
              <td>{{ display_amount(Currency.英镑, budget.spent) }}</td>
            </tr>
          </router-link>
        </tbody>
        <tfoot v-if="user?.budgeteer" class="full width">
          <tr>
            <th colspan="5">
              <sui-checkbox toggle v-model="show_all" label="显示全部" />
            </th>
          </tr>
        </tfoot>
      </table>
    </loading-text>
  </div>
</template>

<style scoped></style>
