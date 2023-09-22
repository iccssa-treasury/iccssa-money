<script lang="ts">
import { api, type User, type Event, type Application } from '@/api';
import { messageErrors, user } from '@/state';
import { EventFields } from '@/forms';
import { Action, Level, Category, Department, display_amount, level_status, level_icon } from '@/enums';
import defaultAvatar from '@/assets/default-avatar.png';

import ApplicationEvent from './components/ApplicationEvent.vue';
import FileUpload from './components/FileUpload.vue';

export default {
  components: { ApplicationEvent, FileUpload },
  setup() {
    return {
      user,
      Action, Level, Category, Department,
      display_amount, level_status, level_icon,
    };
  },
  props: {
    pk: { type: String, required: true },
  },
  data() {
    return {
      waiting: false,
      application: null as Application | null,
      events: new Array<Event>(),
      users: new Map<number, User>(),
      contents: '',
      file: null as null | Blob,
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.application = (await api.get(`main/application/${this.pk}/`)).data as Application;
      this.events = (await api.get(`main/application/${this.pk}/events/`)).data as Event[];
      for (const user of (await api.get('accounts/users/')).data as User[]) {
        this.users.set(user.pk, user);
      }
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    can_approve() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.approval_level === this.application.level - 1 &&
        (user.value.approval_level <= 2 || user.value.department === this.application.department);
    },
    can_cancel() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.pk === this.application.user && this.application.level > 0;
    },
    can_complete() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.approval_level === 1 && this.application.level === 1;
    }
  },
  methods: {
    async event(application: string, action: number) {
      try {
        this.waiting = true;
        const event_fields = new EventFields();
        event_fields.action = action;
        event_fields.contents = this.contents;
        event_fields.file = this.file;
        await api.post(`main/application/${application}/events/`, event_fields, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        // manual update
        this.application = (await api.get(`main/application/${this.pk}/`)).data as Application;
        this.events = (await api.get(`main/application/${this.pk}/events/`)).data as Event[];
        this.contents = '';
        this.file = null;
      } catch (e) {
        messageErrors(e);
      }
      this.waiting = false;
    },
    avatar(pk: number) {
      return this.users.get(pk)?.avatar ?? defaultAvatar;
    },
  },
};
</script>

<template>
  <div v-if="user !== undefined && application !== null" class="ui text container"
    style="padding: 1em 0; min-height: 80vh">
    <h1 class="ui header">
      <img class="ui big bordered avatar image" :src="avatar(application.user)" />
      <div class="content">
        {{ `${users.get(application.user)?.name} 的${Category[application.category]}申请 #${application.pk}` }}
      </div>
    </h1>
    <table class="ui definition table">
      <thead></thead>
      <tbody>
        <tr>
          <td class="three wide">所属部门</td>
          <td>{{ Department[application.department] }}</td>
        </tr>
        <tr>
          <td>申请金额</td>
          <td>{{ display_amount(application.currency, application.amount) }}</td>
        </tr>
        <tr>
          <td>收款账户</td>
          <td>
            <span v-if="application.business">[B]</span>
            {{ `${application.name} - ${application.sort_code} - ${application.account_number}` }}
          </td>
        </tr>
        <tr>
          <td>申请事由</td>
          <td>{{ application.reason }}</td>
        </tr>
        <tr>
          <td>当前状态</td>
          <td :class="level_status(application.level)">
            <i class="icon" :class="level_icon(application.level)"></i>
            {{ Level[application.level] }}
          </td>
        </tr>
        <tr>
          <td>添加评论</td>
          <td>
            <div class="ui form">
              <div class="field">
                <textarea placeholder="添加评论…" v-model="contents" rows="3"></textarea>
              </div>
            </div>
          </td>
        </tr>
        <tr>
          <td>添加附件</td>
          <td>
            <file-upload v-model="file" />
          </td>
        </tr>
      </tbody>
      <tfoot>
        <tr>
          <td colspan="2">
            <button v-if="can_approve" class="ui primary positive button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 1)">
              <i class="check icon"></i>批准
            </button>
            <button v-if="can_approve" class="ui primary negative button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 2)">
              <i class="times icon"></i>驳回
            </button>
            <button v-if="can_complete" class="ui primary positive button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 5)">
              <i class="piggy bank icon"></i>付款
            </button>
            <button v-if="can_cancel" class="ui primary orange button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 4)">
              <i class="times icon"></i>删除
            </button>
            <button class="ui right floated primary button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 0)">
              <i class="comment icon"></i>评论
            </button>
          </td>
        </tr>
      </tfoot>
    </table>
    <div class="ui big comments">
      <!-- <h2 class="ui dividing header">申请时间线</h2> -->
      <div v-for="event in events" :key="event.pk" class="item">
        <application-event
          :time="event.timestamp"
          :avatar="avatar(event.user)"
          :name="users.get(event.user)?.name??''"
          :action="Action[event.action]"
          :category="Category[application.category]"
          :contents="event.contents"
          :file="event.file"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>.ui.dropdown:not(.search) {
  padding: 0.5em 0.5em !important;
}</style>
