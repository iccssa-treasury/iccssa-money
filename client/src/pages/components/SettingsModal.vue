<script lang="ts">
import { api } from '@/api';
import { FormErrors } from '@/errors';
import { messageErrors, user } from '@/state';
import axios from 'axios';

// import MarkdownContent from './MarkdownContent.vue';

class FormFields {
  application: number = 0;
  approval: number = 0;
  income: number = 0;
}

export default {
  // components: { MarkdownContent },
  setup() {
    return { user };
  },
  // See: https://vuejs.org/guide/components/v-model.html
  props: ['modelValue'],
  emits: ['update:modelValue'],
  data() {
    return {
      waiting: false,
      fields: new FormFields(),
      errors: new FormErrors<FormFields>({
        application: [],
        approval: [],
        income: [],
      }),
    };
  },
  computed: {
    modalActive: {
      get(): boolean {
        return this.modelValue;
      },
      set(value: boolean) {
        this.$emit('update:modelValue', value);
      },
    },
  },
  methods: {
    async submit() {
      try {
        this.errors.clear();
        this.waiting = true;
        await api.patch('accounts/me/notification/settings/', this.fields);
        window.location.reload(); // Page refresh is required for new CSRF token.
        return;
      } catch (e) {
        if (axios.isAxiosError(e)) this.errors.decode(e);
        else messageErrors(e);
      }
      this.waiting = false;
    },
    calibrate() {
      this.fields.application = user.value?.notification_settings['application'] ?? 0;
      this.fields.approval = user.value?.notification_settings['approval'] ?? 0;
      this.fields.income = user.value?.notification_settings['income'] ?? 0;
    }
  },
};
</script>

<template>
  <sui-modal v-if="user" size="tiny" v-model="modalActive" :onshow="calibrate()">
    <sui-modal-header>通知设置</sui-modal-header>
    <sui-modal-content scrolling>
      <sui-form></sui-form>
      <sui-list>
        <sui-list-item>
          <sui-icon name="bell" />
          <sui-list-content>
            <sui-list-header>报销申请</sui-list-header>
            <sui-list-description>
              <sui-slider
                v-model="fields.application"
                labeled="ticked"
                :labels="['关闭', '仅必要', '开启']"
                :max="2"
              />
            </sui-list-description>
          </sui-list-content>
        </sui-list-item>
        <sui-list-item v-if="user.application_level<4">
          <sui-icon name="bell" />
          <sui-list-content>
            <sui-list-header>财务审核</sui-list-header>
            <sui-list-description>
              <sui-slider
                v-model="fields.approval"
                labeled="ticked"
                :labels="['关闭', '仅必要', '开启']"
                :max="2"
              />
            </sui-list-description>
          </sui-list-content>
        </sui-list-item>
        <sui-list-item v-if="user.representative">
          <sui-icon name="bell" />
          <sui-list-content>
            <sui-list-header>收入记录</sui-list-header>
            <sui-list-description>
              <sui-slider
                v-model="fields.income"
                labeled="ticked"
                :labels="['关闭', '仅必要', '开启']"
                :max="2"
              />
            </sui-list-description>
          </sui-list-content>
        </sui-list-item>
      </sui-list>
    </sui-modal-content>

    <sui-modal-actions>
      <sui-message v-if="errors.all.length > 0" icon error>
        <sui-icon name="info" />
        <sui-message-content>
          <sui-list bulleted>
            <sui-list-item v-for="error of errors.all" :key="error">
              {{ error }}
            </sui-list-item>
          </sui-list>
        </sui-message-content>
      </sui-message>
      <sui-button primary :disabled="waiting" :loading="waiting" @click="submit">保存</sui-button>
      <sui-button @click="modalActive = false">关闭</sui-button>
    </sui-modal-actions>
  </sui-modal>
</template>

<style scoped>
.slider {
  margin: 2em;
  max-width: 80%;
}
</style>
