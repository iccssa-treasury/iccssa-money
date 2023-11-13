<script lang="ts">

import { type File, filename_display, file_href } from '@/api';

export default {
  setup() {
    return { filename_display, file_href };
  },
  props: {
    file: {
      type: Object as () => File,
      required: true,
    },
  },
};
</script>

<template>
  <a class="ui basic label" :href="file_href(file)">
    <i class="file icon"></i>{{ filename_display(file) }}
  </a>
</template>
