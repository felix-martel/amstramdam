<template>
  <span class="sharing">
    <span class="sharer" @click="toggleView">
      {{ message }}
    </span>
    <a ref="link"
       :class="{collapsed: collapsed, copied: copied}"
       :style="{maxWidth: collapsed ? 0 : width}"
       class="sharing-link"
       :href="trueUrl"
       @click.prevent="copyUrlToClipboard">{{ trueUrl }}</a>
  </span>
</template>

<script>
// TODO: use footerCOllapsibleSection

export default {
  data() {
    const trueUrl = window.location.href
    const url = trueUrl.replace("https://", "")
          .replace("www.", "")
          .replace(window.location.hash, "");
    return {
      url: url,
      trueUrl: trueUrl,
      collapsed: true,
      width: 0,
      timeout: undefined,
      copied: false,
    }
  },
  mounted() {
    this.width = this.getIntrinsicWidth(this.$refs.link);

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
      window.setTimeout(() => {
        this.copied = false;
      }, 2*1000);
      this.timeout = this.startTimeout(() => {
        this.hideLink();
      }, 3*1000);
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

    getIntrinsicWidth(el) {
      if (!el) return -1;
      el.style.maxWidth = "none";
      const width = getComputedStyle(el).width;
      el.style.display = "inline-block";
      el.style.maxWidth = 0;
      console.log("Computed width:", width);
      return width;
    }
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
  /*margin-right: 15px;*/
  font-size: 1.1em;
  font-weight: bold;
  transition: all 0.4s ease;
  display: inline-block;
  overflow-x: hidden;
  overflow-y: visible;
  white-space: nowrap;
  vertical-align: bottom;
  box-sizing: border-box;
}
a.sharing-link:hover {
  color: white !important;
}

a.sharing-link.collapsed {
  opacity: 0;
}

a.sharing-link:not(.collapsed):after {
  display: block;
  content: "Lien copié !";
  background-color: black;
  padding: 5px 10px;
  position: absolute;
  top: -10px;
  right: 50%;
  opacity: 0;
  font-size: 0.8em;
  transition: all 0.2s ease-in;
}

a.sharing-link.copied:after {
  top: -25px;
  opacity: 1;
  transition: all 0.2s ease-out;
}
</style>