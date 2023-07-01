<script lang="ts">
import { api, type Application } from '@/api';
import { messageErrors } from '@/state';
import { Category, Department, Level, currency_symbol, level_status, level_icon } from '@/enums';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      Category, Department, Level,
      currency_symbol, level_status, level_icon,
    };
  },
  data() {
    return {
      loading: true,
      applications: new Array<Application>(),
    };
  },
  async created() {
    try {
      this.applications = (await api.get('main/me/applications/')).data as Application[];
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
      <h1 class="ui header">申请记录</h1>
      <router-link custom to="/applications/new/" v-slot="{ navigate }">
        <button class="ui button primary" @click="navigate">新建申请</button>
      </router-link>
      <table class="ui compact fixed selectable striped single line celled table">
        <thead>
          <tr>
            <th class="two wide">类目</th>
            <th class="six wide">事由</th>
            <th>金额</th>
            <th>收款方</th>
            <th>状态</th>
          </tr>
        </thead>
        <tbody>
          <router-link custom
            v-for = "application in applications"
            :key="application.pk"
            :to="`/api/main/application/${application.pk}/`"
            v-slot="{ navigate }"
          >
            <tr @click="navigate">
              <td>{{ Category[application.category] }}</td>
              <td>{{ application.reason }}</td>
              <td>{{ `${currency_symbol(application.currency)}${application.amount}` }}</td>
              <td>{{ application.name }}</td>
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
