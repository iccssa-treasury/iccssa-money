<script lang="ts">
import { friendlyDate } from '@/dates';
import { type File } from '@/api';

import FileLink from './FileLink.vue';

export default {
  components: { FileLink },
  setup() {
    return { friendlyDate };
  },
  props: {
    time: { type: String, required: true },
    avatar: { type: String, required: true },
    name: { type: String, required: true },
    action: { type: String, required: true },
    contents: { type: String, required: false },
    files: { type: Array<File>, required: true },
    // For application events
    category: { type: String, required: false },
    // For income receipts
    display_amount: { type: String, required: false },
    amount: {type: Number, required: false},
  },
  computed: {
    date() {
      return friendlyDate(new Date(this.time));
    },
    title() {
      if (this.category) {
        // For application events
        return `${this.action}了${this.category}申请`;
      } else {
        // For income receipts
        return this.amount! > 0 ? 
          `确认收款 ${this.display_amount}` : 
          `${this.action}了收款合同`;
      }
    },
    show_action() {
      if (this.category) {
        // For application events
        return this.action != '评论';
      } else {
        // For income receipts
        return this.amount! > 0 || this.action != '评论';
      }
    }
  }
};
</script>

<template>
  <div class="comment">
    <a class="avatar">
      <img :src="avatar" />
    </a>
    <div class="content">
      <a class="author">
        {{ name }}
        <span v-if="show_action">{{ title }}</span>
      </a>
      <div class="metadata">
        <span class="date">{{ date }}</span>
      </div>
      <div class="text">{{ contents }}</div>
      <file-link v-for="file in files" :file="file" />
    </div>
  </div>
  <div class="ui divider"></div>
</template>
