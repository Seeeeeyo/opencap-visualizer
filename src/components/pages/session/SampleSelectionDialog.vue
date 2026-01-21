<template>
  <v-dialog :value="value" @input="$emit('input', $event)" max-width="600" content-class="sample-selection-dialog">
    <v-card class="sample-selection-dialog-card">
      <v-card-title class="headline white--text">
        <v-icon left color="primary">mdi-play-circle</v-icon>
        Choose Sample Motion Set
      </v-card-title>
      <v-card-text class="white--text pt-8">
        <div class="text-body-2 mb-4">
          Select a motion capture set to explore the visualizer's capabilities:
        </div>

        <v-row>
          <v-col
            v-for="sampleSet in availableSampleSets"
            :key="sampleSet.id"
            cols="12"
            md="6"
            class="sample-option-col"
          >
            <v-card
              class="sample-option-card sample-option-hover"
              @click="$emit('select-sample', sampleSet.id)"
              dark
              outlined
            >
              <v-card-text class="pa-4 text-center">
                <v-icon size="48" color="primary" class="mb-3">
                  {{ getSampleIcon(sampleSet.id) }}
                </v-icon>
                <div class="text-h6 mb-2">{{ sampleSet.name }}</div>
                <div class="text-caption grey--text">{{ sampleSet.description }}</div>
              </v-card-text>
            </v-card>
          </v-col>
        </v-row>

        <div class="text-caption grey--text mt-4 text-center">
          <v-icon small class="mr-1">mdi-information-outline</v-icon>
          Each set contains multiple motion capture files with different capture methods (Motion Capture, WHAM, and OpenCap Monocular)
        </div>
      </v-card-text>

      <v-card-actions>
        <v-spacer></v-spacer>
        <v-btn text @click="$emit('input', false)">Cancel</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>

<script>
export default {
  name: 'SampleSelectionDialog',
  props: {
    value: {
      type: Boolean,
      default: false
    },
    availableSampleSets: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    getSampleIcon(sampleSetId) {
      const iconMap = {
        'STS': 'mdi-chair-rolling',
        'squat': 'mdi-human-handsdown',
        'walk': 'mdi-walk',
        'rmasb': 'mdi-run-fast',
        'walk_ts': 'mdi-walk'
      };
      return iconMap[sampleSetId] || 'mdi-play-circle';
    }
  }
};
</script>

<style lang="scss" scoped>
::v-deep .sample-selection-dialog {
  .v-dialog {
    background: rgba(30, 30, 30, 0.95);
    backdrop-filter: blur(10px);
  }
}

.sample-selection-dialog-card {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.sample-option-col {
  padding: 8px !important;
}

.sample-option-card {
  height: 160px;
  transition: all 0.3s ease;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.05) !important;
  border: 1px solid rgba(255, 255, 255, 0.1) !important;
}

.sample-option-card.full-width-sample {
  height: auto;
}

.sample-option-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3) !important;
  border-color: rgba(33, 150, 243, 0.5) !important;
  background: rgba(33, 150, 243, 0.1) !important;
}

.sample-option-card .v-icon {
  transition: all 0.3s ease;
}

.sample-option-card:hover .v-icon {
  transform: scale(1.1);
  color: #2196F3 !important;
}

.sample-option-card .text-h6 {
  font-weight: 600;
}
</style>
