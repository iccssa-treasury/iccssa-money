<script lang="ts">

import { FileFields } from '@/forms';
import FileUpload from './FileUpload.vue';

export default {
  components: { FileUpload },
  props: {
    modelValue: {
      type: Array<FileFields>,
      required: true,
    },
  },
  emits: ['update:modelValue'],
  methods: {
    modelUpdate() {
      this.$emit('update:modelValue', this.modelValue);
    },
    addFile() {
      this.modelValue.push({ file: null, filename: '' });
      this.modelUpdate();
    },
    deleteFile() {
      this.modelValue.pop();
      this.modelUpdate();
    }
  },
};
</script>

<template>
  <div class="ui stackable very compact grid">
    <div class="row" v-for="(file, index) in modelValue" :key="index">
      <div class="nine wide column">
        <file-upload v-model="file.file" :key="index" @update:model-value="modelUpdate" />
      </div>
      <div class="seven wide column">
        <div class="ui icon input">
          <input type="text" placeholder="文件标题..." v-model="file.filename" @change="modelUpdate" />
          <i class="ui red trash link icon" v-if="index===modelValue.length-1" @click.prevent="deleteFile"></i>
        </div>
      </div>
    </div>
    <div class="row">
      <div class="one wide column">
        <button class="ui teal icon button" @click.prevent="addFile">
          <i class="ui plus icon"></i>
        </button>
      </div>
    </div>
  </div>
</template>
