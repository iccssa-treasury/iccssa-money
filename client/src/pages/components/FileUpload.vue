<script lang="ts">

export default {
  props: ['modelValue'],
  emits: ['update:modelValue'],
  watch: {
    modelValue(value: null | Blob) {
      if (value === null) {
        (this.$refs.input as HTMLInputElement).value = '';
      }
    }
  },
  computed: {
    modalActive: {
      get(): null | Blob {
        return this.modelValue;
      },
      set(value: null | Blob) {
        this.$emit('update:modelValue', value);
      },
    },
  },
  methods: {
    onFileChange(event: Event) {
      if (event.target === null) return;
      const files = (event.target as HTMLInputElement).files
      this.modalActive = (files === null || !files.length) ? null : files[0];
    },
  },
};
</script>

<template>
  <div class="ui file input">
    <input type="file" @change="onFileChange" ref="input" />
  </div>
</template>
