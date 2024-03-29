<script lang="ts">
import { api } from '@/api';
import { FormErrors } from '@/errors';
import { messageErrors, user } from '@/state';
import { Department, Privilege } from '@/enums';
import axios from 'axios';

// import MarkdownContent from './MarkdownContent.vue';

class FormFields {}

export default {
  // components: { MarkdownContent },
  setup() {
    return { user, Department, Privilege };
  },
  // See: https://vuejs.org/guide/components/v-model.html
  props: ['modelValue'],
  emits: ['update:modelValue'],
  data() {
    return {
      waiting: false,
      fields: new FormFields(),
      errors: new FormErrors<FormFields>({}),
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
        await api.delete('accounts/me/');
        window.location.reload(); // Page refresh is required for new CSRF token.
        return;
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
  <sui-modal v-if="user" size="tiny" v-model="modalActive">
    <sui-modal-header>{{ user.name }} @{{ user.username }}</sui-modal-header>

    <sui-modal-content scrolling>
      <sui-form></sui-form>
      <b>{{ `${Department[user.department]} - ${Privilege[user.approval_level]}/${Privilege[user.application_level]}` }}</b>
      <br><br>
      <a v-if="user.admin" href="/admin/" target="_blank" class="ui button">
        <sui-icon name="key" />
        Administration
      </a>
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
      <sui-button primary @click="modalActive = false">OK</sui-button>
      <sui-button :disabled="waiting" :loading="waiting" @click="submit">Log out</sui-button>
    </sui-modal-actions>
  </sui-modal>
</template>

<style scoped></style>
