<script lang="ts">

export default {
  props: {
    time: { type: String, required: true },
    avatar: { type: String, required: true },
    name: { type: String, required: true },
    action: { type: String, required: true },
    category: { type: String, required: true },
    contents: { type: String, required: false },
    file: { type: String, required: false },
  },
  computed: {
    filename() {
      if (this.file === null || this.file === undefined) return '';
      const filename = this.file.substring(this.file.lastIndexOf('/') + 1);
      const query = filename.indexOf('?');
      return decodeURIComponent(query === -1 ? filename : filename.substring(0, query));
    }
  }
};
</script>

<template>
  <a :href="file">
    <div class="ui header">
      <img class="ui tiny bordered avatar image" :src="avatar" />
      <div class="content">
        <span v-if="file" :data-tooltip="filename">
          <i class="file icon"></i>
        </span>
        {{ `${name}${action}了${category}申请` }}
        {{ contents ? `: "${contents}"` : '' }}
        <div class="sub header">{{ time }}</div>
      </div>
    </div>
  </a>
</template>
