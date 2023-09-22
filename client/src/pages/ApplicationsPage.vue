<script lang="ts">
import { api, type Application, type User } from '@/api';
import { messageErrors, user } from '@/state';
import { Category, Department, Level, display_amount, level_status, level_icon } from '@/enums';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      user,
      Category, Department, Level,
      display_amount, level_status, level_icon,
    };
  },
  data() {
    return {
      loading: true,
      applications: new Array<Application>(),
      show_irrelevant: false,
      users: new Map<number, string>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.applications = (await api.get('main/applications/')).data as Application[];
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
      if (user.value === undefined) return new Array<Application>();
      const level = user.value.approval_level;
      return this.show_irrelevant ?
        this.applications :
        this.applications.filter((application) => application.level === 1 + level ||
          (application.level === 1 && level === 1)); // For Admins
    },
  }
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">待处理记录</h1>
      <table class="ui compact fixed selectable striped single line celled stuck table">
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
          <router-link custom v-for="application in display" :key="application.pk" :to="`/application/${application.pk}/`"
            v-slot="{ navigate }">
            <tr @click="navigate">
              <td>{{ Category[application.category] }}</td>
              <td>{{ Department[application.department] }}</td>
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
        <tfoot class="full width">
          <tr>
            <th colspan="6">
              <sui-checkbox toggle v-model="show_irrelevant" label="显示全部" />
            </th>
          </tr>
        </tfoot>
      </table>
    </loading-text>
  </div>
</template>

<style scoped></style>
