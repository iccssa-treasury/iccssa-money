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
      show_pending: true,
      show_completed: true,
      show_inactive: false,
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
  computed: {
    display() {
      return this.applications.filter((application) => 
        this.show_pending && application.level > 0 ||
        this.show_completed && application.level === 0 ||
        this.show_inactive && application.level < 0
      );
    },
  }
};
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">申请记录</h1>
      <table class="ui compact fixed selectable striped single line celled stuck table">
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
          <router-link custom v-for="application in display" :key="application.pk"
            :to="`/application/${application.pk}/`" v-slot="{ navigate }">
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
        <tfoot class="full width">
          <tr>
            <th colspan="5">
              <sui-checkbox toggle v-model="show_pending" label="待审批" />
              <sui-checkbox toggle v-model="show_completed" label="已完成" />
              <sui-checkbox toggle v-model="show_inactive" label="已取消" />
              <router-link custom to="/applications/new/" v-slot="{ navigate }">
                <button class="ui right floated small primary button" @click="navigate">新建申请</button>
              </router-link>
            </th>
          </tr>
        </tfoot>
      </table>
    </loading-text>
  </div>
</template>

<style scoped>
  .checkbox {
    padding-right: 1em;
  }
</style>
