<script lang="ts">
import { api, type User } from '@/api';
import { messageErrors, user } from '@/state';
import { useRouter } from 'vue-router';
import PopupMessages from './pages/components/PopupMessages.vue';
import BaseLayout from './pages/components/BaseLayout.vue';
import SignUpModal from './pages/components/SignUpModal.vue';
import LogInModal from './pages/components/LogInModal.vue';
import SessionModal from './pages/components/SessionModal.vue';
import SettingsModal from './pages/components/SettingsModal.vue';
import DocumentationModal from './pages/components/DocumentationModal.vue';
import defaultAvatar from '@/assets/default-avatar.png';

// See: https://stackoverflow.com/a/66258242
export default {
  components: { PopupMessages, BaseLayout, SignUpModal, LogInModal, SessionModal, SettingsModal, DocumentationModal },
  setup() {
    return { user };
  },
  data() {
    return {
      loading: true,
      signUpModalIsActive: false,
      logInModalIsActive: false,
      sessionModalIsActive: false,
      settingsModalIsActive: false,
      versionModalIsActive: false,
    };
  },
  methods: {
    currentPathIs(s: string): boolean {
      return useRouter().currentRoute.value.path === s;
    },
  },
  computed: {
    landingPage(): boolean {
      return this.currentPathIs('/');
    },
    avatar(): string {
      return user.value?.avatar ?? defaultAvatar;
    },
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
    } catch (e) {
      messageErrors(e);
    }
  },
};
</script>

<template>
  <base-layout :landingPage="currentPathIs('/')">
    <template #navigation>
      <router-link to="/" class="header item">
        <span>帝国财务</span>
      </router-link>
      <router-link v-if="user?.application_level!<5" to="/me/applications/" class="item" :class="{ active: currentPathIs('/me/applications/') }">
        <i class="file invoice dollar icon" />
        <span>报销申请</span>
      </router-link>
      <router-link v-if="user?.representative" to="/incomes/" class="item" :class="{ active: currentPathIs('/incomes/') }">
        <i class="coins icon" />
        <span>收入记录</span>
      </router-link>
      <router-link v-if="user?.application_level!<4" to="/budgets/" class="item" :class="{ active: currentPathIs('/budgets/') }">
        <i class="piggy bank icon" />
        <span>活动预算</span>
      </router-link>
      <router-link v-if="user?.application_level!<4" to="/applications/" class="item" :class="{ active: currentPathIs('/applications/') }">
        <i class="balance scale icon" />
        <span>财务审核</span>
      </router-link>
      <router-link v-if="user?.application_level!<5" to="/me/destinations/" class="item" :class="{ active: currentPathIs('/me/destinations/') }">
        <i class="credit card outline icon" />
        <span>账户管理</span>
      </router-link>
      <a v-if="!user" @click="logInModalIsActive = true" class="right item">
        <span>Log in</span>
      </a>
      <a v-if="!user" @click="signUpModalIsActive = true" class="item">
        <i class="user circle icon" />
        <span>Sign up</span>
      </a>
      <a v-if="user" @click="settingsModalIsActive = true" class="right item">
        <i class="bell icon" />
        <span>通知</span>
      </a>
      <a v-if="user" @click="sessionModalIsActive = true" class="item">
        <img class="ui bordered avatar image" :src="avatar" :alt="`${user.username}'s avatar`" />
        <span>{{ user.username }}</span>
      </a>
    </template>
    <template #footer>
      <div class="ui small inverted link list">
        <a class="item" href="https://iccssa.org/">© 2023-2024 帝国理工中国学生学者联谊会</a>
        <a class="link item" @click="versionModalIsActive = true"><i>v0.26.331 beta</i></a>
      </div>
    </template>
    <template #modals>
      <sign-up-modal v-model="signUpModalIsActive" />
      <log-in-modal v-model="logInModalIsActive" />
      <session-modal v-model="sessionModalIsActive" />
      <settings-modal v-model="settingsModalIsActive" />
      <documentation-modal v-model="versionModalIsActive" title="更新日志" hide no_icon />
    </template>
  </base-layout>
  <popup-messages />
</template>

<style scoped></style>
