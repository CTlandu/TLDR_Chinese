<template>
  <div class="min-h-screen bg-base-100 flex flex-col">
    <Navbar />

    <main class="flex-1">
      <section class="max-w-xl mx-auto w-full px-4 sm:px-6 pt-12 pb-16">
        <p v-if="state === 'loading'" class="text-base-content/50">加载中...</p>

        <template v-else-if="state === 'invalid'">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-base-content">
            链接无效或已过期
          </h1>
          <p class="mt-3 text-base-content/60">
            可以从最近一封邮件底部的「取消订阅」重新打开。
          </p>
          <router-link to="/" class="btn btn-primary mt-8">返回首页</router-link>
        </template>

        <template v-else-if="state === 'failed'">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-base-content">
            页面加载失败
          </h1>
          <p class="mt-3 text-base-content/60">网络或服务出了点问题，请稍后刷新重试。</p>
          <router-link to="/" class="btn btn-primary mt-8">返回首页</router-link>
        </template>

        <template v-else-if="state === 'already'">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-base-content">
            你已经退订了
          </h1>
          <p class="mt-3 text-base-content/60">
            之后不会再收到【太长不看】科技日推的邮件。
          </p>
          <router-link to="/" class="btn btn-primary mt-8">返回首页</router-link>
        </template>

        <template v-else-if="state === 'done'">
          <h1 class="text-2xl sm:text-3xl font-extrabold text-base-content">
            取消订阅成功
          </h1>
          <div class="mt-3 space-y-2 text-base-content/60">
            <p>你已成功取消订阅 TLDR Chinese 每日科技新闻。</p>
            <p>如果改变主意，随时可以重新订阅。</p>
            <p v-if="gaveFeedback">谢谢你的反馈。</p>
          </div>
          <router-link to="/" class="btn btn-primary mt-8">返回首页</router-link>
        </template>

        <form v-else @submit.prevent="submit">
          <h1 class="text-2xl sm:text-3xl font-extrabold leading-snug text-base-content">
            确定不再接收【太长不看】科技日推？
          </h1>
          <p class="mt-3 text-base-content/60">
            方便的话告诉我们为什么，原因可以不填。
          </p>

          <fieldset class="mt-8">
            <legend class="text-sm font-bold text-base-content/80">
              退订原因（可多选）
            </legend>
            <div class="mt-3">
              <label
                v-for="reason in reasons"
                :key="reason.key"
                class="flex cursor-pointer items-center gap-3 py-2"
              >
                <input
                  v-model="selected"
                  type="checkbox"
                  :value="reason.key"
                  class="checkbox checkbox-primary checkbox-sm"
                />
                <span class="text-base-content/80">{{ reason.label }}</span>
              </label>
            </div>
          </fieldset>

          <label class="mt-6 block">
            <span class="text-sm font-bold text-base-content/80">
              {{ selected.includes('other') ? '具体是什么原因？' : '还有什么想说的？（可选）' }}
            </span>
            <textarea
              v-model="comment"
              rows="4"
              maxlength="500"
              class="textarea mt-2 w-full rounded border border-white/10 bg-base-200 text-base text-base-content placeholder:text-base-content/30 focus:border-primary focus:outline-none"
            ></textarea>
          </label>

          <p v-if="error" class="mt-4 text-sm text-error">{{ error }}</p>

          <div class="mt-8 flex items-center gap-5">
            <button
              type="submit"
              :disabled="submitting"
              class="btn btn-primary px-6 font-bold text-white"
            >
              {{ submitting ? '提交中...' : '确认退订' }}
            </button>
            <router-link
              to="/"
              class="text-sm text-base-content/50 transition-colors hover:text-base-content"
            >
              不退了，回首页
            </router-link>
          </div>
        </form>
      </section>
    </main>

    <Footer />
  </div>
</template>

<script>
import Navbar from '../components/Navbar.vue';
import Footer from '../components/Footer.vue';
import axios from 'axios';
import { useHead } from '@unhead/vue';

// key 要和后端 api/services/unsubscribe_feedback.py 的白名单一致
const REASONS = [
  { key: 'too_frequent', label: '每天一封太多了，看不过来' },
  { key: 'not_relevant', label: '内容和我关心的方向不太相关' },
  { key: 'quality', label: '翻译或摘要质量不够好' },
  { key: 'read_elsewhere', label: '我更习惯在网站、小红书等地方看' },
  { key: 'read_original', label: '我直接看英文原版 TLDR 了' },
  { key: 'email_issue', label: '邮件经常进垃圾箱，或者显示有问题' },
  { key: 'no_time', label: '最近太忙，暂时不需要' },
  { key: 'other', label: '其他' },
];

export default {
  name: 'UnsubscribeView',
  components: {
    Navbar,
    Footer,
  },
  setup() {
    useHead({
      title: '取消订阅 | 太长不看',
      meta: [{ name: 'robots', content: 'noindex, nofollow' }],
    });
  },
  data() {
    return {
      state: 'loading',
      reasons: REASONS,
      selected: [],
      comment: '',
      submitting: false,
      error: '',
      gaveFeedback: false,
    };
  },
  computed: {
    token() {
      const token = this.$route.query.token;
      return typeof token === 'string' ? token : '';
    },
  },
  async mounted() {
    if (!this.token) {
      this.state = 'invalid';
      return;
    }
    try {
      const API_URL = import.meta.env.VITE_API_URL || '';
      const response = await axios.get(`${API_URL}/api/unsubscribe-status`, {
        params: { token: this.token },
      });
      if (!response.data.valid) {
        this.state = 'invalid';
      } else if (response.data.already_unsubscribed) {
        this.state = 'already';
      } else {
        this.state = 'form';
      }
    } catch (error) {
      console.error('Error checking unsubscribe token:', error);
      this.state = 'failed';
    }
  },
  methods: {
    async submit() {
      this.submitting = true;
      this.error = '';
      try {
        const API_URL = import.meta.env.VITE_API_URL || '';
        const response = await axios.post(`${API_URL}/api/unsubscribe`, {
          token: this.token,
          reasons: this.selected,
          comment: this.comment,
        });
        if (response.data.already) {
          this.state = 'already';
          return;
        }
        this.gaveFeedback =
          this.selected.length > 0 || this.comment.trim().length > 0;
        this.state = 'done';
      } catch (error) {
        console.error('Error unsubscribing:', error);
        const status = error.response?.status;
        if (status === 404) {
          this.state = 'invalid';
        } else if (status === 429) {
          this.error = '操作太频繁，请稍后再试';
        } else {
          this.error = '提交失败，请稍后重试';
        }
      } finally {
        this.submitting = false;
      }
    },
  },
};
</script>
