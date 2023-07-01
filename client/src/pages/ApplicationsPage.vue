<script lang="ts">
import { api, type Application, type User } from '@/api';
import { messageErrors, user } from '@/state';
import { Category, Department, Level, currency_symbol, level_status, level_icon } from '@/enums';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      user,
      Category, Department, Level,
      currency_symbol, level_status, level_icon,
    };
  },
  data() {
    return {
      loading: true,
      applications: new Array<Application>(),
      display: new Array<Application>(),
      users: new Map<number, User>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.applications = (await api.get('main/applications/')).data as Application[];
      this.display = this.applications.filter((application) => application.level === 1 + (user.value?.approval_level ?? 0));
      for (const user of (await api.get('accounts/users/')).data as User[]) {
        this.users.set(user.pk, user);
      }
      this.loading = false;
    } catch (e) {
      messageErrors(e);
    }
  },
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">待处理记录</h1>
      <table class="ui compact fixed selectable striped single line celled table">
        <thead>
          <tr>
            <th class="two wide">类目</th>
            <th class="two wide">部门</th>
            <th class="two wide">申请人</th>
            <th class="four wide">事由</th>
            <th>金额</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <router-link custom v-for="application in display" :key="application.pk"
            :to="`/api/main/application/${application.pk}/`" v-slot="{ navigate }">
            <tr @click="navigate">
              <td>{{ Category[application.category] }}</td>
              <td>{{ Department[application.department] }}</td>
              <td>
                <!-- <img class="ui avatar image" :src="users.get(application.user)?.avatar" /> -->
                {{ users.get(application.user)?.name }}
              </td>
              <td>{{ application.reason }}</td>
              <td>{{ `${currency_symbol(application.currency)}${application.amount}` }}</td>
              <td :class="level_status(application.level)">
                <i class="icon" :class="level_icon(application.level)"></i>
                {{ Level[application.level] }}
              </td>
            </tr>
          </router-link>
        </tbody>
      </table>
    </loading-text>
  </div>
</template>

<style scoped></style>
