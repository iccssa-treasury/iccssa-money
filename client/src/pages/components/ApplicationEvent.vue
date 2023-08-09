<script lang="ts">
import { friendlyDate } from '@/dates';

export default {
  setup() {
    return { friendlyDate };
  },
  props: {
    time: { type: String, required: true },
    avatar: { type: String, required: true },
    name: { type: String, required: true },
    action: { type: String, required: true },
    contents: { type: String, required: false },
    file: { type: String, required: false },
    // For application events
    category: { type: String, required: false },
    // For income receipts
    currency: { type: String, required: false },
    amount: {type: Number, required: false},
  },
  computed: {
    date() {
      return friendlyDate(new Date(this.time));
    },
    filename() {
      if (this.file === null || this.file === undefined) return '';
      const filename = this.file.substring(this.file.lastIndexOf('/') + 1);
      const query = filename.indexOf('?');
      return decodeURIComponent(query === -1 ? filename : filename.substring(0, query));
    },
    title() {
      if (this.category) {
        // For application events
        return `${this.action}了${this.category}申请`;
      } else {
        // For income receipts
        return this.amount! > 0 ? 
          `确认收款 ${this.currency}${this.amount}` : 
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
      <a class="ui basic label" v-if="file" :href="file">
        <i class="file icon"></i>{{ filename }}
      </a>
    </div>
  </div>
  <div class="ui divider"></div>
</template>
