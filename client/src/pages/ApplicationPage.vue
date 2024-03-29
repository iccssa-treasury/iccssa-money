<script lang="ts">
import { api, type User, type File, type Event, type Application, type Budget, destination_display } from '@/api';
import { messageErrors, user } from '@/state';
import { EventFields } from '@/forms';
import { Action, Level, Category, Department, Platform, display_amount, level_status, level_icon } from '@/enums';
import defaultAvatar from '@/assets/default-avatar.png';

import ApplicationEvent from './components/ApplicationEvent.vue';
import FilesUpload from './components/FilesUpload.vue';

export default {
  components: { ApplicationEvent, FilesUpload },
  setup() {
    return {
      user,
      Action, Level, Category, Department, Platform,
      display_amount, level_status, level_icon,
      destination_display
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
      budget: null as Budget | null,
      users: new Map<number, User>(),
      event_fields: new EventFields(),
      files: new Map<number, File>(),
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.application = (await api.get(`main/application/${this.pk}/`)).data as Application;
      this.events = (await api.get(`main/application/${this.pk}/events/`)).data as Event[];
      for (const file of (await api.get(`main/application/${this.pk}/files/`)).data as File[])
        this.files.set(file.pk, file);
      if (this.application.budget !== null)
        this.budget = (await api.get(`main/budget/${this.application.budget}/`)).data as Budget;
      for (const user of (await api.get('accounts/users/')).data as User[])
        this.users.set(user.pk, user);
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    can_approve() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.approval_level === this.application.level - 1 &&
        (user.value.approval_level <= 2 || user.value.department === this.budget?.department);
    },
    can_cancel() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.pk === this.application.user && this.application.level > 0;
    },
    can_complete() {
      if (user.value === undefined || this.application === null) return false;
      return user.value.approval_level === 1 && this.application.level === 1;
    },
    can_comment() {
      return this.event_fields.contents || this.has_file;
    },
    has_file() {
      return this.event_fields.files.filter(f => f.file !== null).length > 0;
    }
  },
  methods: {
    async event(application: string, action: number) {
      try {
        this.waiting = true;
        this.event_fields.action = action;
        await api.post(`main/application/${application}/events/`, this.event_fields, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        // manual update
        this.application = (await api.get(`main/application/${this.pk}/`)).data as Application;
        this.events = (await api.get(`main/application/${this.pk}/events/`)).data as Event[];
        this.budget = (await api.get(`main/budget/${this.application.budget}/`)).data as Budget;
        for (const file of (await api.get(`main/application/${this.pk}/files/`)).data as File[])
          this.files.set(file.pk, file);
        this.event_fields = new EventFields();
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
          <td>{{ Department[budget?.department!] }}</td>
        </tr>
        <tr>
          <td>预算方案</td>
          <td>
            {{ budget?.reason }}
            <router-link v-if="user.budgeteer" :to="`/budget/${application.budget}/`">
              <i class="external alternate icon" />
            </router-link>
          </td>
        </tr>
        <tr>
          <td>申请金额</td>
          <td>{{ display_amount(application.currency, application.amount) }}</td>
        </tr>
        <tr v-if="application.platform">
          <td>收款方式</td>
          <td>{{ Platform[application.platform] }}</td>
        </tr>
        <tr>
          <td>收款账户</td>
          <td>
            <span v-if="application.business">[B]</span>
            {{ destination_display(application) }}
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
                <textarea placeholder="添加评论…" v-model="event_fields.contents" rows="3"></textarea>
              </div>
            </div>
          </td>
        </tr>
        <tr>
          <td>添加附件</td>
          <td>
            <files-upload v-model="event_fields.files" />
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
            <button v-if="can_comment" class="ui right floated primary button" :class="{ disabled: waiting, loading: waiting }"
              @click="event(pk, 0)">
              <i :class="has_file ? 'file alternate' : 'comment'" class="icon"></i>
              {{ event_fields.contents ? '评论' : '提交' }}
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
          :files="event.files.map(pk => files.get(pk)!)"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>.ui.dropdown:not(.search) {
  padding: 0.5em 0.5em !important;
}</style>
