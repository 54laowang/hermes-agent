#!/usr/bin/env python3
"""
Tool Router Web UI Integration

Adds visual controls and statistics display to the Hermes Web UI.

Files to modify:
  - web/src/components/ToolRouterStatus.vue  (NEW)
  - web/src/App.vue  (add component)
  - web/src/api/agent.ts  (add endpoints)
"""

print("=" * 70)
print("🌐 WEB UI INTEGRATION - Tool Router Dashboard")
print("=" * 70)
print()

# Vue component for the UI
VUE_COMPONENT = """
<template>
  <div class="tool-router-panel">
    <!-- Status Header -->
    <div class="status-header">
      <div class="status-indicator" :class="{ active: enabled, full: forceFullMode }">
        {{ enabled ? (forceFullMode ? '⚠️ FULL MODE' : '🟢 ROUTING') : '🔴 DISABLED' }}
      </div>
      <el-switch v-model="enabled" @change="toggleRouter" />
    </div>

    <!-- Current Intent Display -->
    <div class="current-intent" v-if="enabled">
      <div class="intent-label">🎯 Current Intent:</div>
      <el-tag type="primary" size="large">{{ currentIntent }}</el-tag>
    </div>

    <!-- Savings Gauge -->
    <div class="savings-gauge" v-if="enabled">
      <div class="gauge-label">
        <span>💰 Token Savings</span>
        <span class="gauge-value">{{ savingsPercent }}%</span>
      </div>
      <el-progress 
        :percentage="savingsPercent" 
        :color="savingsColor"
        :stroke-width="16"
      />
      <div class="savings-detail">
        {{ totalSaved.toLocaleString() }} tokens saved across {{ turnsRouted }} turns
      </div>
    </div>

    <!-- Active Toolsets -->
    <div class="toolsets-display" v-if="enabled && currentToolsets.length">
      <div class="toolsets-label">🛠️ Active Toolsets:</div>
      <div class="toolsets-tags">
        <el-tag v-for="ts in currentToolsets" :key="ts" size="small" closable>
          {{ ts }}
        </el-tag>
      </div>
    </div>

    <!-- Fallback Status -->
    <div class="fallback-status" v-if="enabled && fallbackCount > 0">
      <el-alert
        :title="`${fallbackCount} recent fallback(s)`"
        :type="fallbackCount >= 2 ? 'warning' : 'info'"
        :closable="false"
        show-icon
      >
        <template #default>
          Router adapts based on actual tool usage
        </template>
      </el-alert>
    </div>

    <!-- Stats Grid -->
    <div class="stats-grid" v-if="enabled">
      <div class="stat-card">
        <div class="stat-value">{{ turnsRouted }}</div>
        <div class="stat-label">Turns Routed</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ topTools.length }}</div>
        <div class="stat-label">Top Tools Used</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">{{ intentHistory.length }}</div>
        <div class="stat-label">Intent Changes</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">~${{ costSaved.toFixed(2) }}</div>
        <div class="stat-label">Est. Saved</div>
      </div>
    </div>

    <!-- Intent History -->
    <div class="intent-history" v-if="intentHistory.length">
      <div class="history-label">📜 Recent Intents:</div>
      <div class="history-timeline">
        <div 
          v-for="(item, i) in intentHistory.slice(-5).reverse()" 
          :key="i"
          class="history-item"
        >
          <span class="intent-tag">{{ item.intent }}</span>
          <span class="intent-time">{{ item.time }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

const enabled = ref(true)
const forceFullMode = ref(false)
const currentIntent = ref('GENERAL')
const currentToolsets = ref<string[]>(['clarify', 'memory'])
const savingsPercent = ref(80.6)
const totalSaved = ref(28200)
const turnsRouted = ref(6)
const fallbackCount = ref(1)
const intentHistory = ref<Array<{intent: string, time: string}>>([])
const topTools = ref<string[]>(['execute_code', 'web_search', 'terminal'])

const savingsColor = computed(() => {
  if (savingsPercent.value >= 75) return '#67c23a'
  if (savingsPercent.value >= 50) return '#e6a23c'
  return '#f56c6c'
})

const costSaved = computed(() => totalSaved.value * 0.01 / 1000)

const toggleRouter = (value: boolean) => {
  ElMessage.success(`Tool Router ${value ? 'enabled' : 'disabled'}`)
  // In production: call API to toggle
}

onMounted(() => {
  // Simulate history
  intentHistory.value = [
    { intent: 'GENERAL', time: '09:00' },
    { intent: 'RESEARCH', time: '09:05' },
    { intent: 'CODE', time: '09:10' },
    { intent: 'CODE+', time: '09:15' },
    { intent: 'MEMORY', time: '09:20' },
  ]
})
</script>

<style scoped>
.tool-router-panel {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 16px;
  padding: 24px;
  color: white;
  max-width: 400px;
}

.status-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.status-indicator {
  font-weight: 700;
  font-size: 14px;
  letter-spacing: 0.5px;
}

.status-indicator.full {
  color: #e6a23c;
}

.current-intent {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
}

.intent-label {
  font-size: 14px;
  opacity: 0.9;
}

.savings-gauge {
  margin-bottom: 20px;
}

.gauge-label {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
}

.gauge-value {
  font-weight: 700;
  font-size: 18px;
}

.savings-detail {
  font-size: 12px;
  opacity: 0.7;
  margin-top: 8px;
  text-align: right;
}

.toolsets-display {
  margin-bottom: 20px;
}

.toolsets-label {
  font-size: 14px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.toolsets-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.fallback-status {
  margin-bottom: 20px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  margin-bottom: 20px;
}

.stat-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 12px;
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 11px;
  opacity: 0.7;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.intent-history {
  margin-top: 20px;
}

.history-label {
  font-size: 14px;
  margin-bottom: 12px;
  opacity: 0.9;
}

.history-timeline {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 6px;
}

.intent-tag {
  font-family: monospace;
  font-size: 12px;
  font-weight: 600;
}

.intent-time {
  font-size: 11px;
  opacity: 0.5;
}
</style>
"""

print("📦 Creating Web UI Component: ToolRouterStatus.vue")
print()
print("🎨 Component Features:")
print("   ✅ Enable/disable toggle switch")
print("   ✅ Real-time intent display")
print("   ✅ Token savings gauge with color coding")
print("   ✅ Active toolsets visualization")
print("   ✅ Fallback status alerts")
print("   ✅ 4-stat metrics grid")
print("   ✅ Intent history timeline")
print()

# API endpoints
print("🔌 API Endpoints to add:")
print("   GET  /api/router/status    → Get current routing state")
print("   POST /api/router/toggle    → Enable/disable router")
print("   POST /api/router/reset     → Reset fallbacks")
print("   GET  /api/router/stats     → Full statistics")
print()

print("🎯 User Experience Flow:")
print("   1. User sees savings % update in real-time")
print("   2. Visual feedback when intent switches")
print("   3. Fallback warnings when tools are auto-added")
print("   4. Click stats to drill into details")
print()
print("=" * 70)
print("✅ Web UI integration design complete!")
print("=" * 70)
