<script lang="ts">
import MarkdownIt from 'markdown-it';

// See: https://github.com/markdown-it/markdown-it

export default {
  props: {
    markdown: { type: String, required: true },
    unsafe: { type: Boolean, default: false }, // Allow HTML in markdown.
  },
  data() {
    return { converted: '' };
  },
  created() {
    const md = new MarkdownIt({
      html: this.unsafe,
    });
    // See: https://github.com/markdown-it/markdown-it/blob/master/docs/security.md
    this.converted = md.render(this.markdown);
  },
};
</script>

<template>
  <div v-html="converted"></div>
</template>

<style scoped>
:deep(pre.tight) {
  margin: 0;
  white-space: pre-wrap;
}
</style>
