<script lang="ts">
import { api } from '@/api';
import { messageErrors } from '@/state';

import MarkdownContent from './MarkdownContent.vue';

interface Documentation {
  content: string;
}

export default {
  components: { MarkdownContent },
  props: {
    modelValue: { type: Boolean, required: true },
    title: { type: String, required: true },
    hide: { type: Boolean, default: false },
    no_icon: { type: Boolean, default: false },
  },
  emits: ['update:modelValue'],
  data() {
    return {
      documentation: null as null | Documentation,
    }
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
  async created() {
    try {
      this.documentation = (await api.get(`main/documentation/${this.title}/`)).data as Documentation;
    } catch (e) {
      messageErrors(e);
    }
  },
};
</script>

<template>
  <span v-if="!hide">{{ title }}&nbsp;</span>
  <i v-if="!no_icon" class="question circle outline link icon" @click="modalActive = true" />
  
  <sui-modal size="tiny" v-model="modalActive">
    <sui-modal-header>{{ title }}</sui-modal-header>
    <sui-modal-content scrolling>
      <markdown-content v-if="documentation" :markdown="documentation?.content??''" unsafe />
    </sui-modal-content>
    <sui-modal-actions>
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
