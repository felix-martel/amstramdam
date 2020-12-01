<template>
  <footer-collapsible-section :collapsed="collapsed">
    <template v-slot:control>
      <span class="sharer" @click="toggleView">
      {{ message }}
    </span>
    </template>
    <template v-slot:content>
      <a ref="link"
         :class="{copied: copied, 'link-collapsed': collapsed}"
         class="sharing-link"
         :href="trueUrl"
         @click.prevent="copyUrlToClipboard">{{ trueUrl }}</a>
    </template>
  </footer-collapsible-section>
</template>

<script>
import footerCollapsibleSection from "./footerCollapsibleSection.vue";
export default {
  components: {
    "footer-collapsible-section": footerCollapsibleSection,
  },
  data() {
    const trueUrl = window.location.href
    const url = trueUrl.replace("https://", "")
          .replace("www.", "")
          .replace(window.location.hash, "");
    return {
      url: url,
      trueUrl: trueUrl,
      collapsed: true,
      timeout: undefined,
      copied: false,
    }
  },
  methods: {
    copyUrlToClipboard() {
      const selection = window.getSelection();
      const range = document.createRange();
      range.selectNodeContents(this.$refs.link);
      selection.removeAllRanges();
      selection.addRange(range);
      // this.$refs.link.select();
      document.execCommand("copy");
      this.copied = true;
      const duration = 0.6
      window.setTimeout(() => {
        this.copied = false;
      }, duration*1000);
      this.timeout = this.startTimeout(() => {
        this.hideLink();
      }, (duration + 0.3) *1000);
    },

    clearTimeout() {
      if (typeof this.timeout !== "undefined") {
        window.clearTimeout(this.timeout);
        this.timeout = "undefined";
      }
    },

    startTimeout(handler, duration) {
      this.clearTimeout();
      this.timeout = window.setTimeout(handler, duration);
    },

    showLink() {
      this.clearTimeout();
      this.collapsed = false;
    },

    hideLink() {
      this.collapsed = true;
      this.copied = false;
      this.clearTimeout();
    },

    toggleView() {
      if (this.collapsed){
        this.showLink();
        this.timeout = this.startTimeout(() => {
          this.hideLink();
        }, 20*1000);
      } else {
        this.hideLink();
      }
    },
  },

  computed: {
    message() {
      return this.collapsed ? "Inviter des amis" : "Lien à partager : ";
    }
  }
}
</script>

<style scoped>
.sharer {
  cursor: pointer;
  display: inline-block;
  margin-right: 10px;
}
a.sharing-link {
  color: white !important;
  font-size: 1.1em;
  font-weight: bold;
  display: inline-block;
  white-space: nowrap;
  vertical-align: bottom;
}
a.sharing-link:hover {
  color: white !important;
}


a.sharing-link:not(.link-collapsed):after {
  display: block;
  content: "Lien copié !";
  background-color: black;
  padding: 5px 10px;
  position: absolute;
  top: -10px;
  left: 50%;
  opacity: 0;
  font-size: 0.8em;
  transition: all 0.2s ease-in;
}

a.sharing-link:not(.link-collapsed).copied:after {
  top: -25px;
  opacity: 1;
  transition: all 0.2s ease-out;
}
</style>