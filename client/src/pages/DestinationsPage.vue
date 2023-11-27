<script lang="ts">
import { api, type User, type Destination } from '@/api';
import { messageErrors, user } from '@/state';
import { DestinationFields } from '@/forms';
import LoadingText from './components/LoadingText.vue';

export default {
  components: { LoadingText },
  setup() {
    return {
      user,
    };
  },
  data() {
    return {
      loading: true,
      destinations: new Array<Destination>(),
      fields: new DestinationFields(),
      editing: null as number | null,
      adding: null as number | null,
      tables: [
        { title: '英镑账户', platform: 0, name: 'Name', sort_code: 'Sort Code', account_number: 'Account Number', business: 'Business', colspan: 6 },
        { title: '支付宝账户', platform: 2, name: '收款人姓名', card_number: '支付宝账号', colspan: 4 },
        { title: '微信账户', platform: 3, name: '收款人姓名', card_number: '微信账号', colspan: 4 },
        { title: '银行卡账户', platform: 1, name: '收款人姓名', card_number: '银行卡号', bank_name: '开户行名称', colspan: 5 },
      ]
    };
  },
  async created() {
    try {
      const data = (await api.get('accounts/me/')).data;
      if (data) user.value = data as User;
      // console.log(data);
      this.destinations = (await api.get('main/me/destinations/')).data as Destination[];
      this.loading = false;
    } catch (e) {
      messageErrors(e);
    }
  },
  computed: {
    groups() {
      return [0, 1, 2, 3].map((index) =>
        this.destinations
          .filter((destination) => destination.platform === index)
          .sort((a, b) => this.sort_bool(a.star, b.star)
            || this.sort_bool(a.public, b.public)
            || a.name.localeCompare(b.name))
      );
    },
  },
  methods: {
    sort_bool(a: boolean, b: boolean) {
      return a === b ? 0 : a ? -1 : 1;
    },
    add(platform: number) {
      this.editing = null;
      this.fields = new DestinationFields();
      this.fields.platform = platform;
      this.adding = platform;
    },
    edit(destination: Destination) {
      this.adding = null;
      this.fields.platform = destination.platform;
      this.fields.name = destination.name;
      this.fields.sort_code = destination.sort_code;
      this.fields.account_number = destination.account_number;
      this.fields.business = destination.business;
      this.fields.card_number = destination.card_number;
      this.fields.bank_name = destination.bank_name;
      this.fields.public = destination.public;
      this.fields.star = destination.star;
      this.editing = destination.pk;
    },
    async toggle_public(destination: Destination) {
      try {
        await api.patch(`main/destination/${destination.pk}/`, { public: !destination.public });
        destination.public = !destination.public;
      } catch (e) {
        messageErrors(e);
      }
    },
    async toggle_star(destination: Destination) {
      try {
        await api.patch(`main/destination/${destination.pk}/`, { star: !destination.star });
        destination.star = !destination.star;
      } catch (e) {
        messageErrors(e);
      }
    },
    async save_edit(destination: Destination) {
      try {
        await api.patch(`main/destination/${this.editing}/`, this.fields);
        destination.name = this.fields.name;
        destination.sort_code = this.fields.sort_code;
        destination.account_number = this.fields.account_number;
        destination.business = this.fields.business;
        destination.card_number = this.fields.card_number;
        destination.bank_name = this.fields.bank_name;
        this.editing = null;
      } catch (e) {
        messageErrors(e);
      }
    },
    async save_add() {
      try {
        const destination = (await api.post('main/me/destinations/', this.fields)).data as Destination;
        this.destinations.push(destination);
        this.adding = null;
      } catch (e) {
        messageErrors(e);
      }
    },
    async remove(destination: Destination) {
      try {
        await api.delete(`main/destination/${destination.pk}/`);
        this.destinations.splice(this.destinations.indexOf(destination), 1);
      } catch (e) {
        messageErrors(e);
      }
    }
  }
}
</script>

<template>
  <div class="ui text container" style="padding: 1em 0; min-height: 80vh">
    <loading-text fill-height :loading="loading">
      <h1 class="ui header">收款账户</h1>
      <template v-for="table in tables">
        <h2 class="ui header">
          {{ table.title }}
          <i v-if="groups[table.platform].length===0 && adding!==table.platform" class="small green plus link icon" @click="add(table.platform)"></i>
        </h2>
        <table v-if="groups[table.platform].length || adding===table.platform"
          class="ui compact fixed striped single line stuck table">
          <thead>
            <tr>
              <th class="two wide"></th>
              <th class="three wide">{{ table.name }}</th>
              <th v-if="table.sort_code">{{ table.sort_code }}</th>
              <th v-if="table.account_number">{{ table.account_number }}</th>
              <th v-if="table.business" class="two wide">{{ table.business }}</th>
              <th v-if="table.card_number">{{ table.card_number }}</th>
              <th v-if="table.bank_name">{{ table.bank_name }}</th>
              <th class="two wide"></th>
            </tr>
          </thead>
          <tbody>
            <template v-for="destination in groups[table.platform]">
              <tr v-if="editing !== destination.pk">
                <td class="center aligned">
                  <i class="star link icon" :class="destination.star ? 'yellow' : ''"
                    @click="toggle_star(destination)"></i>&nbsp;
                  <i class="eye link icon" :class="destination.public ? 'teal' : 'grey slash'"
                    @click="toggle_public(destination)"></i>
                </td>
                <td>{{ destination.name }}</td>
                <td v-if="table.sort_code">{{ destination.sort_code }}</td>
                <td v-if="table.account_number">{{ destination.account_number }}</td>
                <td v-if="table.business">{{ destination.business ? "Yes" : "No" }}</td>
                <td v-if="table.card_number">{{ destination.card_number }}</td>
                <td v-if="table.bank_name">{{ destination.bank_name }}</td>
                <td class="center aligned">
                  <i class="violet edit link icon" @click="edit(destination)"></i>&nbsp;
                  <i class="red trash alternate link icon" @click="remove(destination)"></i>
                </td>
              </tr>
              <tr v-else>
                <td></td>
                <td><form class="ui form"><input v-model="fields.name"></form></td>
                <td v-if="table.sort_code"><form class="ui form"><input v-model="fields.sort_code"></form></td>
                <td v-if="table.account_number"><form class="ui form"><input v-model="fields.account_number"></form></td>
                <td v-if="table.business"><sui-checkbox toggle v-model="fields.business" /></td>
                <td v-if="table.card_number"><form class="ui form"><input v-model="fields.card_number"></form></td>
                <td v-if="table.bank_name"><form class="ui form"><input v-model="fields.bank_name"></form></td>
                <td class="center aligned">
                  <i class="violet save link icon" @click="save_edit(destination)"></i>&nbsp;
                  <i class="orange times link icon" @click="editing=null"></i>
                </td>
              </tr>
            </template>
            <tr v-if="adding !== table.platform">
              <td :colspan="table.colspan" class="right aligned"><i class="green plus link icon" @click="add(table.platform)"></i></td>
            </tr>
            <tr v-else>
              <td></td>
              <td><form class="ui form"><input v-model="fields.name"></form></td>
              <td v-if="table.sort_code"><form class="ui form"><input v-model="fields.sort_code"></form></td>
              <td v-if="table.account_number"><form class="ui form"><input v-model="fields.account_number"></form></td>
              <td v-if="table.business"><sui-checkbox toggle v-model="fields.business" /></td>
              <td v-if="table.card_number"><form class="ui form"><input v-model="fields.card_number"></form></td>
              <td v-if="table.bank_name"><form class="ui form"><input v-model="fields.bank_name"></form></td>
              <td>
                <i class="green save link icon" @click="save_add"></i>&nbsp;
                <i class="orange times link icon" @click="adding=null"></i>
              </td>
            </tr>
          </tbody>
        </table>
      </template>
    </loading-text>
  </div>
</template>

<style scoped></style>
