<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="500" content-class="github-info-dialog">
    <v-card>
      <v-card-title class="text-subtitle-1">
        Source Code & Support
        <v-spacer></v-spacer>
        <v-btn icon small @click="$emit('input', false)">
          <v-icon small>mdi-close</v-icon>
        </v-btn>
      </v-card-title>
      <v-divider></v-divider>
      <v-card-text class="pa-4">
        <div class="d-flex align-center justify-center mb-4">
          <svg class="github-logo-popup" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
          </svg>
        </div>
        <p class="mb-4 text-center">
          The source code for this project is available on GitHub. You can view the repository, contribute to the project, or ask questions through GitHub issues.
        </p>
        <div class="d-flex flex-column">
          <v-btn
            color="blue darken-2"
            dark
            class="mb-3"
            @click="$emit('open-github-repo')"
          >
            <v-icon left>mdi-github</v-icon>
            View Source Code
          </v-btn>
          <v-btn
            color="grey darken-2"
            dark
            @click="$emit('open-github-issues')"
          >
            <v-icon left>mdi-message-question</v-icon>
            Ask Questions
          </v-btn>
        </div>
      </v-card-text>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'GithubInfoDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .github-info-dialog {
  .v-card {
    background-color: #1E1E1E !important;
    color: #FFFFFF !important;
    border-radius: 12px;
    overflow: hidden;
  }

  .v-card-title {
    background-color: #282828 !important;
    color: #FFFFFF !important;
    padding: 16px 24px;
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  }

  .v-card-text {
    color: #FFFFFF !important;
    background-color: #1E1E1E !important;
  }

  .v-btn {
    color: #FFFFFF !important;
  }
}

.github-logo-popup {
  width: 64px;
  height: 64px;
  color: #FFFFFF;
}
</style>
