<template>
  <div class="kin-page" :class="{ 'kin-page--drawer-open': sidebarOpen }">
    <!-- Mobile: button to open the measurements drawer -->
    <button class="kin-menu-btn" @click="sidebarOpen = true" aria-label="Open motions list">
      <span class="kin-menu-btn__icon">&#9776;</span>
      <span>Motions</span>
    </button>

    <!-- Backdrop behind the drawer on small screens -->
    <div v-if="sidebarOpen" class="kin-backdrop" @click="sidebarOpen = false" />

    <!-- Sidebar: list of measurements grouped by joint -->
    <aside class="kin-sidebar" :class="{ 'kin-sidebar--open': sidebarOpen }">
      <div class="kin-sidebar__header">
        <div>
          <div class="kin-title">Kinematics Reference</div>
          <div class="kin-subtitle">Joint motions of human biomechanics</div>
        </div>
        <button class="kin-sidebar__close" @click="sidebarOpen = false" aria-label="Close menu">
          &times;
        </button>
      </div>

      <div class="kin-list">
        <button
          class="kin-item kin-item--static"
          :class="{ 'kin-item--active': !selected }"
          @click="selectStatic">
          <span class="kin-item__dot" style="background-color: #9aa3b0" />
          <span class="kin-item__label">Skeleton (no motion)</span>
        </button>

        <div v-for="group in groups" :key="group.name" class="kin-group">
          <div class="kin-group__name">{{ group.name }}</div>
          <button
            v-for="m in group.items"
            :key="m.id"
            class="kin-item"
            :class="{ 'kin-item--active': selected && selected.id === m.id }"
            @click="selectMeasurement(m)">
            <span class="kin-item__dot" :style="{ backgroundColor: planeColor(m.plane) }" />
            <span class="kin-item__label">{{ m.label }}</span>
          </button>
        </div>
      </div>

      <a class="kin-back" href="/">&larr; Back to viewer</a>
    </aside>

    <!-- Viewer -->
    <main class="kin-viewer">
      <div ref="canvas" class="kin-canvas" />

      <div v-if="loading" class="kin-loading">
        <div class="kin-spinner" />
        <div>Loading skeleton… {{ loadedCount }}/{{ totalToLoad }}</div>
      </div>

      <!-- Click-catcher to dismiss open dropdowns -->
      <div v-if="openMenu" class="kin-menu-catcher" @click="openMenu = null" />

      <!-- Compact dropdown toolbar -->
      <div class="kin-views">
        <!-- View / camera presets -->
        <div class="kin-dropdown">
          <button class="kin-view-btn kin-view-btn--menu"
            :class="{ 'kin-view-btn--active': openMenu === 'view' }"
            @click="toggleMenu('view')">
            View: {{ currentViewLabel }} <span class="kin-caret">▾</span>
          </button>
          <div v-if="openMenu === 'view'" class="kin-menu">
            <button v-for="v in viewPresets" :key="v.id"
              class="kin-menu__item" :class="{ 'kin-menu__item--active': activeView === v.id }"
              @click="selectView(v.id); openMenu = null">
              <span class="kin-menu__check">{{ activeView === v.id ? '✓' : '' }}</span>{{ v.label }}
            </button>
          </div>
        </div>

        <!-- Display / overlay toggles -->
        <div class="kin-dropdown">
          <button class="kin-view-btn kin-view-btn--menu"
            :class="{ 'kin-view-btn--active': openMenu === 'display' }"
            @click="toggleMenu('display')">
            Display <span class="kin-caret">▾</span>
          </button>
          <div v-if="openMenu === 'display'" class="kin-menu kin-menu--wide">
            <button class="kin-menu__item" :class="{ 'kin-menu__item--active': showPlanes }"
              @click="togglePlanes">
              <span class="kin-menu__check">{{ showPlanes ? '✓' : '' }}</span>Planes
            </button>
            <button class="kin-menu__item" :class="{ 'kin-menu__item--active': showBoneNames }"
              @click="toggleBoneNames">
              <span class="kin-menu__check">{{ showBoneNames ? '✓' : '' }}</span>Bone names
            </button>
            <button class="kin-menu__item" :class="{ 'kin-menu__item--active': showSubgroups }"
              @click="toggleSubgroups">
              <span class="kin-menu__check">{{ showSubgroups ? '✓' : '' }}</span>Subgroups
            </button>
            <button class="kin-menu__item" :class="{ 'kin-menu__item--active': showGuideLabels }"
              @click="toggleGuideLabels">
              <span class="kin-menu__check">{{ showGuideLabels ? '✓' : '' }}</span>Motion labels
            </button>
            <div class="kin-menu__divider" />
            <div class="kin-menu__row">
              <span>Label size</span>
              <div class="kin-menu__size">
                <button class="kin-view-btn kin-view-btn--icon" title="Smaller labels"
                  @click="changeLabelSize(-1)">A&minus;</button>
                <button class="kin-view-btn kin-view-btn--icon" title="Larger labels"
                  @click="changeLabelSize(1)">A+</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Control panel -->
      <div v-if="selected" class="kin-panel">
        <div class="kin-controls">
          <button class="kin-play" @click="togglePlay">
            <span v-if="playing">❚❚</span><span v-else>▶</span>
          </button>
          <span class="kin-range-label">{{ selected.min }}&deg;</span>
          <input
            class="kin-slider"
            type="range"
            :min="selected.min"
            :max="selected.max"
            :value="angle"
            step="0.5"
            @input="onScrub($event)" />
          <span class="kin-range-label">{{ selected.max }}&deg;</span>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import * as THREE from 'three'
import * as THREE_OC from '@/orbitControls'
import { OBJLoader } from 'three/examples/jsm/loaders/OBJLoader.js'
import { MEASUREMENT_GROUPS, PLANES } from '@/util/kinematics/measurements'
import {
  skeletonModel,
  BODY_ORDER,
  DESCENDANTS,
  computeWorldTransforms,
  localRotationsForMeasurement,
  quaternionFromAxisAngleDeg,
} from '@/util/kinematics/forwardKinematics'

const objLoader = new OBJLoader()
const GEOMETRY_BASE = 'https://mc-opencap-public.s3.us-west-2.amazonaws.com/geometries/'

const BONE_COLOR = 0xe9e2d2
const HIGHLIGHT_COLOR = 0x4995e0

// Lift the whole skeleton off the ground plane so it isn't cramped against the floor.
const MODEL_LIFT = 0.05

// Map an individual geometry (a single bone mesh) to a readable anatomical name.
// Each rigid body segment is built from one or more of these "subgroup" bones.
const SUBGROUP_NAMES = {
  r_pelvis: 'Ilium (R)',
  l_pelvis: 'Ilium (L)',
  sacrum: 'Sacrum',
  r_femur: 'Femur',
  l_femur: 'Femur',
  r_tibia: 'Tibia',
  l_tibia: 'Tibia',
  r_fibula: 'Fibula',
  l_fibula: 'Fibula',
  r_talus: 'Talus',
  l_talus: 'Talus',
  r_foot: 'Calcaneus',
  l_foot: 'Calcaneus',
  r_bofoot: 'Toes',
  l_bofoot: 'Toes',
  hat_spine: 'Spine',
  hat_jaw: 'Jaw',
  hat_skull: 'Skull',
  hat_ribs_scap: 'Ribs & scapula',
  humerus_rv: 'Humerus',
  humerus_lv: 'Humerus',
  ulna_rv: 'Ulna',
  ulna_lv: 'Ulna',
  radius_rv: 'Radius',
  radius_lv: 'Radius',
}

// Per-segment nudge (metres) applied along the bone's local long axis (downward) for the
// "Bones" segment label. A body's origin sits at its proximal joint, so for long distal
// bones (e.g. tibia) the label otherwise lands up near the parent segment.
const BONE_LABEL_DROP = {
  tibia_r: 0.18,
  tibia_l: 0.18,
}

function subgroupName(geom) {
  if (SUBGROUP_NAMES[geom]) return SUBGROUP_NAMES[geom]
  // The hand is composed of many small bones; collapse them into anatomical groups
  // so the viewer isn't flooded with ~27 overlapping labels per hand.
  if (/^(pisiform|lunate|scaphoid|triquetrum|hamate|capitate|trapezoid|trapezium)_/.test(geom)) {
    return 'Carpals'
  }
  if (/^metacarpal\d+_/.test(geom)) return 'Metacarpals'
  if (/_(proximal|medial|distal)_/.test(geom)) return 'Phalanges'
  return geom
}

export default {
  name: 'Kinematics',
  data() {
    return {
      groups: MEASUREMENT_GROUPS,
      selected: null,
      angle: 0,
      displayAngle: 0,
      playing: true,
      loading: true,
      loadedCount: 0,
      totalToLoad: 0,
      activeView: 'sagittal',
      lockedView: null,
      showPlanes: false,
      showBoneNames: false,
      showSubgroups: false,
      showGuideLabels: true,
      labelScale: 1,
      sidebarOpen: false,
      openMenu: null,
      viewPresets: [
        { id: 'sagittal', label: 'Side' },
        { id: 'frontal', label: 'Front' },
        { id: 'transverse', label: 'Top' },
        { id: 'perspective', label: '3D' },
      ],
    }
  },
  computed: {
    currentViewLabel() {
      const v = this.viewPresets.find((p) => p.id === this.activeView)
      return v ? v.label : '3D'
    },
    directionLabel() {
      if (!this.selected) return ''
      const dir = this.selected.dir
      if (this.displayAngle > 0.5) return dir ? dir[0] : 'positive'
      if (this.displayAngle < -0.5) return dir ? dir[1] || dir[0] : 'negative'
      return 'neutral'
    },
  },
  mounted() {
    this.initScene()
    this.loadBones()
    window.addEventListener('resize', this.onResize)
    window.addEventListener('keydown', this.onKeydown)
    // default to the static skeleton (no motion)
    this.selectStatic()
    this.phase = 0
    this.lastT = performance.now()
    this.animate()
  },
  beforeDestroy() {
    window.removeEventListener('resize', this.onResize)
    window.removeEventListener('keydown', this.onKeydown)
    if (this._raf) cancelAnimationFrame(this._raf)
    this.clearGuide()
    if (this.renderer) {
      this.renderer.dispose()
      const el = this.renderer.domElement
      if (el && el.parentNode) el.parentNode.removeChild(el)
    }
  },
  methods: {
    planeColor(p) {
      return (PLANES[p] && PLANES[p].color) || '#888'
    },
    planeLabel(p) {
      return (PLANES[p] && PLANES[p].label) || p
    },
    initScene() {
      const container = this.$refs.canvas
      const ratio = container.clientWidth / container.clientHeight

      this.camera = new THREE.PerspectiveCamera(45, ratio, 0.05, 200)
      this.scene = new THREE.Scene()
      this.scene.background = new THREE.Color(0x14171c)
      this.scene.fog = new THREE.FogExp2(0x14171c, 0.04)

      this.renderer = new THREE.WebGLRenderer({ antialias: true })
      this.renderer.setPixelRatio(window.devicePixelRatio || 1)
      this.renderer.shadowMap.enabled = true
      this.renderer.setSize(container.clientWidth, container.clientHeight)
      container.appendChild(this.renderer.domElement)

      this.controls = new THREE_OC.OrbitControls(this.camera, this.renderer.domElement)
      this.controls.target.set(0, 0.9, 0)
      this.controls.enableDamping = true
      this.controls.dampingFactor = 0.1

      // ground
      {
        const size = 6
        const grid = new THREE.GridHelper(size, 24, 0x3a3f48, 0x262a30)
        grid.position.y = 0
        this.scene.add(grid)

        const planeGeo = new THREE.PlaneGeometry(size, size)
        const planeMat = new THREE.MeshPhongMaterial({ color: 0x1b1f25, side: THREE.DoubleSide })
        const plane = new THREE.Mesh(planeGeo, planeMat)
        plane.rotation.x = -Math.PI / 2
        plane.position.y = -0.001
        plane.receiveShadow = true
        this.scene.add(plane)
      }

      // lights
      this.scene.add(new THREE.HemisphereLight(0xbfd4ff, 0x404038, 0.7))
      {
        const light = new THREE.DirectionalLight(0xffffff, 0.85)
        light.position.set(2.5, 4, 2)
        light.castShadow = true
        light.shadow.camera.left = -3
        light.shadow.camera.right = 3
        light.shadow.camera.top = 3
        light.shadow.camera.bottom = -3
        light.shadow.camera.near = 0.1
        light.shadow.camera.far = 20
        light.shadow.mapSize.width = 1024
        light.shadow.mapSize.height = 1024
        this.scene.add(light)
      }
      {
        const fill = new THREE.DirectionalLight(0xffffff, 0.25)
        fill.position.set(-2, 2, -2)
        this.scene.add(fill)
      }

      this.buildPlanes()
      this.buildBoneLabels()
      this.setView('sagittal')
    },
    formatBoneName(body) {
      const names = {
        pelvis: 'Pelvis',
        femur: 'Femur',
        tibia: 'Tibia',
        talus: 'Talus',
        calcn: 'Calcaneus',
        toes: 'Toes',
        torso: 'Torso',
        humerus: 'Humerus',
        ulna: 'Ulna',
        radius: 'Radius',
        hand: 'Hand',
      }
      const m = body.match(/^([a-z]+)(?:_(r|l))?$/)
      if (!m) return body
      const base = names[m[1]] || m[1]
      const side = m[2] === 'r' ? ' R' : m[2] === 'l' ? ' L' : ''
      return base + side
    },
    buildBoneLabels() {
      const group = new THREE.Group()
      this.boneLabels = {}
      this.boneLeaders = {}
      const dotGeo = new THREE.SphereGeometry(0.007, 10, 10)
      BODY_ORDER.forEach((body) => {
        const s = this.makeTextSprite(this.formatBoneName(body), '#aee1ff', 0.00045)
        s.visible = false
        group.add(s)
        this.boneLabels[body] = s

        // leader line from the bone to its label
        const lineGeo = new THREE.BufferGeometry()
        lineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6), 3))
        const lineMat = new THREE.LineBasicMaterial({
          color: 0x6fb7e6,
          transparent: true,
          opacity: 0.55,
          depthTest: false,
        })
        const line = new THREE.Line(lineGeo, lineMat)
        line.renderOrder = 997
        line.visible = false
        group.add(line)

        // marker dot at the bone
        const dot = new THREE.Mesh(
          dotGeo,
          new THREE.MeshBasicMaterial({ color: 0xaee1ff, depthTest: false, transparent: true })
        )
        dot.renderOrder = 997
        dot.visible = false
        group.add(dot)

        this.boneLeaders[body] = { line, dot }
      })
      this.boneLabelsGroup = group
      this.scene.add(group)
    },
    toggleBoneNames() {
      this.showBoneNames = !this.showBoneNames
      this.updatePose(this.angle)
    },
    buildSubgroupLabels() {
      if (this.subgroupsBuilt) return
      this.subgroupsBuilt = true
      const group = new THREE.Group()
      this.subgroups = []
      const dotGeo = new THREE.SphereGeometry(0.005, 8, 8)
      BODY_ORDER.forEach((body) => {
        // Collect this segment's geometry roots by anatomical subgroup name.
        const byName = {}
        this.meshesByBody[body].forEach((root) => {
          const name = subgroupName(root.userData.geom)
          if (!byName[name]) byName[name] = []
          byName[name].push(root)
        })
        const names = Object.keys(byName)
        names.forEach((name, idx) => {
          const sprite = this.makeTextSprite(name, '#ffd9a8', 0.0004)
          sprite.visible = false
          group.add(sprite)

          const lineGeo = new THREE.BufferGeometry()
          lineGeo.setAttribute('position', new THREE.BufferAttribute(new Float32Array(6), 3))
          const line = new THREE.Line(
            lineGeo,
            new THREE.LineBasicMaterial({
              color: 0xe0a86a,
              transparent: true,
              opacity: 0.5,
              depthTest: false,
            })
          )
          line.renderOrder = 998
          line.visible = false
          group.add(line)

          const dot = new THREE.Mesh(
            dotGeo,
            new THREE.MeshBasicMaterial({ color: 0xffd9a8, depthTest: false, transparent: true })
          )
          dot.renderOrder = 998
          dot.visible = false
          group.add(dot)

          this.subgroups.push({ body, roots: byName[name], sprite, line, dot, idx, count: names.length })
        })
      })
      this.subgroupGroup = group
      this.scene.add(group)
      this.updatePose(this.angle)
    },
    toggleSubgroups() {
      this.showSubgroups = !this.showSubgroups
      this.updatePose(this.angle)
    },
    buildPlanes() {
      const cy = 0.9 + MODEL_LIFT
      const defs = [
        { key: 'sagittal', w: 1.0, h: 1.9, rot: [0, 0, 0] }, // divides L/R, normal = z
        { key: 'frontal', w: 1.0, h: 1.9, rot: [0, Math.PI / 2, 0] }, // divides front/back, normal = x
        { key: 'transverse', w: 1.0, h: 1.0, rot: [-Math.PI / 2, 0, 0] }, // horizontal, normal = y
      ]
      const group = new THREE.Group()
      this.planeMats = {}
      defs.forEach((d) => {
        const color = new THREE.Color(this.planeColor(d.key)).getHex()
        const geo = new THREE.PlaneGeometry(d.w, d.h)
        const fill = new THREE.MeshBasicMaterial({
          color,
          transparent: true,
          opacity: 0.08,
          side: THREE.DoubleSide,
          depthWrite: false,
        })
        const mesh = new THREE.Mesh(geo, fill)
        mesh.rotation.set(d.rot[0], d.rot[1], d.rot[2])
        mesh.position.set(0, cy, 0)
        const edgeMat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.4 })
        const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo), edgeMat)
        mesh.add(edges)
        group.add(mesh)
        this.planeMats[d.key] = { fill, edge: edgeMat }
      })

      // Plane name labels (positioned on each plane, colored by plane)
      this.planeLabelSprites = {}
      const nameDefs = [
        { key: 'sagittal', text: 'Sagittal plane', pos: [0, cy + 0.82, 0] },
        { key: 'frontal', text: 'Frontal plane', pos: [0, cy + 0.95, 0.42] },
        { key: 'transverse', text: 'Transverse plane', pos: [0.42, cy + 0.02, 0.42] },
      ]
      nameDefs.forEach((n) => {
        const s = this.makeTextSprite(n.text, this.planeColor(n.key), 0.00075)
        s.position.set(n.pos[0], n.pos[1], n.pos[2])
        group.add(s)
        this.planeLabelSprites[n.key] = s
      })

      // Anatomical direction labels around the body
      const dirColor = '#cfd5de'
      const dirDefs = [
        { text: 'Superior', pos: [0, cy + 1.02, 0] },
        { text: 'Inferior', pos: [0, cy - 1.02, 0] },
        { text: 'Anterior', pos: [0.62, cy - 0.2, 0] },
        { text: 'Posterior', pos: [-0.62, cy - 0.2, 0] },
        { text: 'Right', pos: [0, cy - 0.2, 0.62] },
        { text: 'Left', pos: [0, cy - 0.2, -0.62] },
      ]
      dirDefs.forEach((dd) => {
        const s = this.makeTextSprite(dd.text, dirColor, 0.0007)
        s.position.set(dd.pos[0], dd.pos[1], dd.pos[2])
        group.add(s)
      })

      group.visible = this.showPlanes
      this.planesGroup = group
      this.scene.add(group)
    },
    applyPlaneEmphasis() {
      if (!this.planeMats) return
      Object.keys(this.planeMats).forEach((k) => {
        const active = this.selected && this.selected.plane === k
        this.planeMats[k].fill.opacity = active ? 0.16 : 0.045
        this.planeMats[k].edge.opacity = active ? 0.85 : 0.2
        if (this.planeLabelSprites && this.planeLabelSprites[k]) {
          this.planeLabelSprites[k].material.opacity = active ? 1 : 0.45
        }
      })
    },
    togglePlanes() {
      this.showPlanes = !this.showPlanes
      if (this.planesGroup) this.planesGroup.visible = this.showPlanes
    },
    loadBones() {
      this.meshesByBody = {}
      BODY_ORDER.forEach((b) => (this.meshesByBody[b] = []))

      const tasks = []
      BODY_ORDER.forEach((body) => {
        const info = skeletonModel.bodies[body]
        info.attachedGeometries.forEach((geom) => {
          tasks.push({ body, geom })
        })
      })
      this.totalToLoad = tasks.length

      tasks.forEach(({ body, geom }) => {
        const baseName = geom.substr(0, geom.length - 4)
        const url = `${GEOMETRY_BASE}${baseName}.obj`
        objLoader.load(
          url,
          (root) => {
            const sf = skeletonModel.bodies[body].scaleFactors
            root.scale.set(sf[0], sf[1], sf[2])
            root.traverse((child) => {
              if (child instanceof THREE.Mesh) {
                child.castShadow = true
                child.receiveShadow = true
                child.material = new THREE.MeshPhongMaterial({
                  color: BONE_COLOR,
                  shininess: 12,
                  specular: 0x222222,
                })
              }
            })
            // Record the geometry name and its local (scaled) centroid so we can later
            // place per-bone "subgroup" labels at the right spot on the segment.
            root.userData.geom = baseName
            root.userData.body = body
            root.updateMatrixWorld(true)
            const box = new THREE.Box3().setFromObject(root)
            const center = new THREE.Vector3()
            box.getCenter(center)
            root.userData.localCenter = center
            this.meshesByBody[body].push(root)
            this.scene.add(root)
            this.loadedCount += 1
            if (this.loadedCount >= this.totalToLoad) {
              this.loading = false
              this.buildSubgroupLabels()
            }
            this.applyHighlight()
          },
          undefined,
          () => {
            this.loadedCount += 1
            if (this.loadedCount >= this.totalToLoad) this.loading = false
          }
        )
      })
    },
    selectMeasurement(m) {
      this.selected = m
      this.phase = 0
      this.angle = m.neutral
      this.displayAngle = Math.round(m.neutral)
      this.playing = true
      // Keep the user's chosen camera view across measurements; otherwise default to
      // the view that best shows this motion's plane.
      this.activeView = this.lockedView || (m.plane === 'transverse' ? 'perspective' : m.plane)
      this.applyVisibility()
      this.setView(this.activeView)
      this.applyHighlight()
      this.applyPlaneEmphasis()
      this.updatePose(m.neutral)
      this.buildGuide()
      this.sidebarOpen = false
    },
    selectStatic() {
      this.selected = null
      this.playing = false
      this.sidebarOpen = false
      this.clearGuide()
      this.visibleBodies = null
      if (this.meshesByBody) {
        BODY_ORDER.forEach((b) => this.meshesByBody[b].forEach((r) => (r.visible = true)))
      }
      this.applyHighlight()
      this.applyPlaneEmphasis()
      this.setView(this.lockedView || 'perspective')
      this.updatePose(0)
    },
    farthestDescendant(jointBody) {
      const base = this.neutralBase || (this.neutralBase = computeWorldTransforms({}))
      const c = base[jointBody].position
      let best = jointBody
      let bestD = 0
      ;(DESCENDANTS[jointBody] || []).forEach((b) => {
        if (b === jointBody) return
        const d = base[b].position.distanceTo(c)
        if (d > bestD) {
          bestD = d
          best = b
        }
      })
      return best
    },
    clearGuide() {
      if (!this.guideGroup) return
      this.guideGroup.traverse((o) => {
        if (o.geometry) o.geometry.dispose()
        if (o.material) {
          if (o.material.map) o.material.map.dispose()
          o.material.dispose()
        }
      })
      this.scene.remove(this.guideGroup)
      this.guideGroup = null
    },
    makeTextSprite(text, colorHex, worldScale = 0.0009) {
      const pad = 16
      const fontSize = 52
      const canvas = document.createElement('canvas')
      const ctx = canvas.getContext('2d')
      ctx.font = `700 ${fontSize}px Roboto, Arial, sans-serif`
      const textW = ctx.measureText(text).width
      canvas.width = Math.ceil(textW + pad * 2)
      canvas.height = fontSize + pad * 2
      // rounded background pill
      const r = 14
      ctx.fillStyle = 'rgba(20,23,28,0.85)'
      const w = canvas.width
      const h = canvas.height
      ctx.beginPath()
      ctx.moveTo(r, 0)
      ctx.arcTo(w, 0, w, h, r)
      ctx.arcTo(w, h, 0, h, r)
      ctx.arcTo(0, h, 0, 0, r)
      ctx.arcTo(0, 0, w, 0, r)
      ctx.closePath()
      ctx.fill()
      ctx.font = `700 ${fontSize}px Roboto, Arial, sans-serif`
      ctx.fillStyle = colorHex
      ctx.textBaseline = 'middle'
      ctx.textAlign = 'center'
      ctx.fillText(text, w / 2, h / 2 + 2)

      const texture = new THREE.Texture(canvas)
      texture.needsUpdate = true
      texture.minFilter = THREE.LinearFilter
      const mat = new THREE.SpriteMaterial({ map: texture, transparent: true, depthTest: false })
      const sprite = new THREE.Sprite(mat)
      // Remember the intrinsic size so the user-controlled labelScale can be re-applied.
      sprite.userData.baseScale = { x: canvas.width * worldScale, y: canvas.height * worldScale }
      const s = this.labelScale || 1
      sprite.scale.set(sprite.userData.baseScale.x * s, sprite.userData.baseScale.y * s, 1)
      sprite.renderOrder = 999
      return sprite
    },
    applyLabelScale() {
      if (!this.scene) return
      const s = this.labelScale
      this.scene.traverse((o) => {
        if (o.isSprite && o.userData && o.userData.baseScale) {
          o.scale.set(o.userData.baseScale.x * s, o.userData.baseScale.y * s, 1)
        }
      })
    },
    changeLabelSize(delta) {
      const next = Math.round((this.labelScale + delta * 0.2) * 100) / 100
      this.labelScale = Math.min(2.6, Math.max(0.4, next))
      this.applyLabelScale()
    },
    buildGuide() {
      if (!this.scene || !this.selected) return
      this.clearGuide()
      const m = this.selected
      const group = new THREE.Group()
      const colorHexNum = new THREE.Color(this.planeColor(m.plane)).getHex()
      const colorStr = this.planeColor(m.plane)

      const neutralWorld = computeWorldTransforms(localRotationsForMeasurement(m, m.neutral))
      const C = neutralWorld[m.jointBody].position.clone()
      C.y += MODEL_LIFT

      // dirFn(deg) -> unit vector from joint center toward the tracer at that angle
      let dirFn
      let radius
      if (m.isolate) {
        const refByPlane = { sagittal: [0, 1, 0], frontal: [0, 0, 1], transverse: [1, 0, 0] }
        const ref = new THREE.Vector3().fromArray(refByPlane[m.plane] || [0, 1, 0])
        dirFn = (deg) => ref.clone().applyQuaternion(quaternionFromAxisAngleDeg(m.axis, deg))
        radius = 0.16
      } else {
        const endpoint = this.farthestDescendant(m.jointBody)
        const vN = neutralWorld[endpoint].position.clone().sub(neutralWorld[m.jointBody].position)
        radius = Math.min(vN.length(), 0.28)
        dirFn = (deg) => {
          const w = computeWorldTransforms(localRotationsForMeasurement(m, deg))
          return w[endpoint].position.clone().sub(w[m.jointBody].position).normalize()
        }
      }

      const N = 56
      const pts = []
      for (let i = 0; i < N; i++) {
        const deg = m.min + ((m.max - m.min) * i) / (N - 1)
        pts.push(C.clone().add(dirFn(deg).multiplyScalar(radius)))
      }

      const lineGeo = new THREE.BufferGeometry().setFromPoints(pts)
      const lineMat = new THREE.LineBasicMaterial({ color: colorHexNum, linewidth: 2, depthTest: false, transparent: true })
      const line = new THREE.Line(lineGeo, lineMat)
      line.renderOrder = 998
      group.add(line)

      const addArrow = (tip, prev) => {
        const dir = tip.clone().sub(prev).normalize()
        const cone = new THREE.Mesh(
          new THREE.ConeGeometry(0.018, 0.05, 14),
          new THREE.MeshBasicMaterial({ color: colorHexNum, depthTest: false, transparent: true })
        )
        cone.renderOrder = 998
        cone.position.copy(tip)
        cone.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir)
        group.add(cone)
      }
      addArrow(pts[N - 1], pts[N - 2])
      addArrow(pts[0], pts[1])

      const labels = m.dir || ['+', '−']
      const labelOffset = 0.05
      const posEnd = pts[N - 1].clone().add(pts[N - 1].clone().sub(C).normalize().multiplyScalar(labelOffset))
      const negEnd = pts[0].clone().add(pts[0].clone().sub(C).normalize().multiplyScalar(labelOffset))
      this.guideLabelSprites = []
      const s0 = this.makeTextSprite(labels[0], colorStr)
      s0.position.copy(posEnd)
      s0.visible = this.showGuideLabels
      group.add(s0)
      this.guideLabelSprites.push(s0)
      if (labels[1]) {
        const s1 = this.makeTextSprite(labels[1], '#c7cdd6')
        s1.position.copy(negEnd)
        s1.visible = this.showGuideLabels
        group.add(s1)
        this.guideLabelSprites.push(s1)
      }

      this.guideGroup = group
      this.scene.add(group)
    },
    toggleGuideLabels() {
      this.showGuideLabels = !this.showGuideLabels
      if (this.guideLabelSprites) {
        this.guideLabelSprites.forEach((s) => (s.visible = this.showGuideLabels))
      }
    },
    toggleMenu(name) {
      this.openMenu = this.openMenu === name ? null : name
    },
    applyVisibility() {
      if (!this.meshesByBody || !this.selected) return
      // For isolated measurements (pelvis), only render the joint's own body so the
      // segment's reorientation is clear instead of the whole skeleton tipping.
      const onlyBodies = this.selected.isolate ? new Set([this.selected.jointBody]) : null
      this.visibleBodies = onlyBodies
      BODY_ORDER.forEach((body) => {
        const visible = !onlyBodies || onlyBodies.has(body)
        this.meshesByBody[body].forEach((root) => {
          root.visible = visible
        })
      })
    },
    applyHighlight() {
      if (!this.meshesByBody) return
      const moving = this.selected ? new Set(DESCENDANTS[this.selected.jointBody] || []) : new Set()
      BODY_ORDER.forEach((body) => {
        const isMoving = moving.has(body)
        this.meshesByBody[body].forEach((root) => {
          root.traverse((child) => {
            if (child instanceof THREE.Mesh && child.material) {
              child.material.color.setHex(isMoving ? HIGHLIGHT_COLOR : BONE_COLOR)
              child.material.emissive &&
                child.material.emissive.setHex(isMoving ? 0x0a1b2e : 0x000000)
            }
          })
        })
      })
    },
    updatePose(angleDeg) {
      if (!this.meshesByBody) return
      const localRots = this.selected ? localRotationsForMeasurement(this.selected, angleDeg) : {}
      const world = computeWorldTransforms(localRots)
      BODY_ORDER.forEach((body) => {
        const t = world[body]
        this.meshesByBody[body].forEach((root) => {
          root.position.set(t.position.x, t.position.y + MODEL_LIFT, t.position.z)
          root.quaternion.copy(t.quaternion)
        })
        if (this.boneLabels && this.boneLabels[body]) {
          const visible =
            this.showBoneNames && (!this.visibleBodies || this.visibleBodies.has(body))
          let ax = t.position.x
          let ay = t.position.y + MODEL_LIFT
          let az = t.position.z
          // Drop the anchor down the bone's long axis for distal segments so the label
          // sits on the bone instead of at the proximal joint (e.g. tibia under the femur).
          const drop = BONE_LABEL_DROP[body]
          if (drop) {
            const d = new THREE.Vector3(0, -drop, 0).applyQuaternion(t.quaternion)
            ax += d.x
            ay += d.y
            az += d.z
          }
          // push the label outward from the body's vertical axis so the leader points in clearly
          let rx = ax
          let rz = az
          const rlen = Math.hypot(rx, rz)
          if (rlen < 1e-3) {
            rx = 1
            rz = 0
          } else {
            rx /= rlen
            rz /= rlen
          }
          const off = 0.16
          const lx = ax + rx * off
          const ly = ay + 0.03
          const lz = az + rz * off

          const lab = this.boneLabels[body]
          lab.position.set(lx, ly, lz)
          lab.visible = visible

          const leader = this.boneLeaders[body]
          if (leader) {
            const p = leader.line.geometry.attributes.position.array
            p[0] = ax
            p[1] = ay
            p[2] = az
            p[3] = lx
            p[4] = ly
            p[5] = lz
            leader.line.geometry.attributes.position.needsUpdate = true
            leader.line.visible = visible
            leader.dot.position.set(ax, ay, az)
            leader.dot.visible = visible
          }
        }
      })

      this.updateSubgroupLabels()
    },
    updateSubgroupLabels() {
      if (!this.subgroups) return
      const tmp = new THREE.Vector3()
      const center = new THREE.Vector3()
      this.subgroups.forEach((sg) => {
        const visible =
          this.showSubgroups && (!this.visibleBodies || this.visibleBodies.has(sg.body))
        sg.sprite.visible = visible
        sg.line.visible = visible
        sg.dot.visible = visible
        if (!visible) return

        // World centroid of this subgroup = average of its geometries' centers.
        center.set(0, 0, 0)
        sg.roots.forEach((root) => {
          tmp.copy(root.userData.localCenter || center)
          tmp.applyQuaternion(root.quaternion).add(root.position)
          center.add(tmp)
        })
        center.multiplyScalar(1 / sg.roots.length)
        const ax = center.x
        const ay = center.y
        const az = center.z

        // Push the label outward and stagger vertically so multiple subgroups
        // within one segment don't stack on top of each other.
        let rx = ax
        let rz = az
        const rlen = Math.hypot(rx, rz)
        if (rlen < 1e-3) {
          rx = 1
          rz = 0
        } else {
          rx /= rlen
          rz /= rlen
        }
        const off = 0.1
        const stagger = (sg.idx - (sg.count - 1) / 2) * 0.06
        const lx = ax + rx * off
        const ly = ay + stagger
        const lz = az + rz * off

        sg.sprite.position.set(lx, ly, lz)
        const p = sg.line.geometry.attributes.position.array
        p[0] = ax
        p[1] = ay
        p[2] = az
        p[3] = lx
        p[4] = ly
        p[5] = lz
        sg.line.geometry.attributes.position.needsUpdate = true
        sg.dot.position.set(ax, ay, az)
      })
    },
    animate() {
      this._raf = requestAnimationFrame(this.animate)
      const now = performance.now()
      const dt = Math.min((now - this.lastT) / 1000, 0.05)
      this.lastT = now

      if (this.playing && this.selected) {
        // ~0.5 Hz full sweep; smooth ease via cosine ping-pong
        this.phase += dt * 0.9
        const param = (1 - Math.cos(this.phase)) / 2 // 0..1..0
        const m = this.selected
        this.angle = m.min + (m.max - m.min) * param
        const rounded = Math.round(this.angle)
        if (rounded !== this.displayAngle) this.displayAngle = rounded
        this.updatePose(this.angle)
      }

      if (this.controls) this.controls.update()
      if (this.renderer) this.renderer.render(this.scene, this.camera)
    },
    onKeydown(e) {
      if (e.code === 'Space' || e.key === ' ') {
        const tag = e.target && e.target.tagName
        if (tag === 'TEXTAREA' || (tag === 'INPUT' && e.target.type !== 'range')) return
        e.preventDefault()
        if (this.selected) this.togglePlay()
      }
    },
    togglePlay() {
      this.playing = !this.playing
      if (this.playing) {
        // resume from current angle: solve phase from current param
        const m = this.selected
        const param = (this.angle - m.min) / (m.max - m.min)
        this.phase = Math.acos(1 - 2 * Math.min(Math.max(param, 0), 1))
      }
    },
    onScrub(e) {
      this.playing = false
      this.angle = parseFloat(e.target.value)
      this.displayAngle = Math.round(this.angle)
      this.updatePose(this.angle)
    },
    selectView(id) {
      this.lockedView = id
      this.setView(id)
    },
    setView(id) {
      this.activeView = id
      if (!this.camera || !this.controls) return
      const iso = this.selected && this.selected.isolate
      // Zoom in tight on the isolated segment (pelvis ~0.9m high); otherwise frame full body.
      const target = new THREE.Vector3(0, (iso ? 0.92 : 0.9) + MODEL_LIFT, 0)
      let pos
      switch (id) {
        case 'sagittal': // view along Z (from the right side) -> see sagittal plane
          pos = new THREE.Vector3(0.05, target.y + 0.05, 3.2 * (iso ? 0.42 : 1))
          break
        case 'frontal': // view along X (from the front)
          pos = new THREE.Vector3(3.4 * (iso ? 0.42 : 1), target.y + 0.05, 0.05)
          break
        case 'transverse': // view from above
          pos = new THREE.Vector3(0.01, target.y + 3.6 * (iso ? 0.4 : 1), 0.02)
          break
        default: // perspective
          pos = new THREE.Vector3(2.6 * (iso ? 0.45 : 1), target.y + (iso ? 0.45 : 0.8), 2.6 * (iso ? 0.45 : 1))
      }
      this.camera.position.copy(pos)
      this.controls.target.copy(target)
      this.controls.update()
    },
    onResize() {
      const container = this.$refs.canvas
      if (!container || !this.renderer) return
      this.renderer.setSize(container.clientWidth, container.clientHeight)
      this.camera.aspect = container.clientWidth / container.clientHeight
      this.camera.updateProjectionMatrix()
    },
  },
}
</script>

<style lang="scss" scoped>
.kin-page {
  position: fixed;
  inset: 0;
  display: flex;
  background: #14171c;
  color: #e9ecf1;
  font-family: Roboto, sans-serif;
}

.kin-sidebar {
  width: 320px;
  flex: 0 0 320px;
  display: flex;
  flex-direction: column;
  background: #1b1f25;
  border-right: 1px solid #2a2f37;

  &__header {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 12px;
    padding: 20px 20px 14px;
    border-bottom: 1px solid #2a2f37;
  }

  &__close {
    display: none; // shown only on small screens
    flex: 0 0 auto;
    width: 34px;
    height: 34px;
    border: none;
    border-radius: 8px;
    background: #232831;
    color: #c7cdd6;
    font-size: 22px;
    line-height: 1;
    cursor: pointer;
    &:hover {
      background: #2b3442;
      color: #fff;
    }
  }
}

// Mobile-only "open drawer" button (hidden on desktop)
.kin-menu-btn {
  display: none;
  position: absolute;
  top: 12px;
  left: 12px;
  z-index: 30;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: rgba(27, 31, 37, 0.9);
  border: 1px solid #2a2f37;
  border-radius: 10px;
  color: #e9ecf1;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  backdrop-filter: blur(6px);
  &__icon {
    font-size: 15px;
    line-height: 1;
  }
}

.kin-backdrop {
  display: none;
  position: absolute;
  inset: 0;
  z-index: 35;
  background: rgba(0, 0, 0, 0.5);
}

.kin-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.2px;
}
.kin-subtitle {
  font-size: 12px;
  color: #8b94a3;
  margin-top: 2px;
}

.kin-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 10px 0;
}

.kin-group {
  margin-bottom: 14px;

  &__name {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #6f7886;
    padding: 4px 10px;
  }
}

.kin-item--static {
  margin-bottom: 6px;
}
.kin-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  text-align: left;
  background: transparent;
  border: none;
  color: #c7cdd6;
  padding: 9px 10px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 13.5px;
  transition: background 0.12s, color 0.12s;

  &:hover {
    background: #232831;
    color: #fff;
  }
  &--active {
    background: #2b3442;
    color: #fff;
  }
  &__dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    flex: 0 0 9px;
  }
  &__label {
    line-height: 1.2;
  }
}

.kin-back {
  display: block;
  padding: 14px 20px;
  border-top: 1px solid #2a2f37;
  color: #8b94a3;
  font-size: 13px;
  text-decoration: none;
  &:hover {
    color: #fff;
  }
}

.kin-viewer {
  position: relative;
  flex: 1;
  min-width: 0;
}
.kin-canvas {
  position: absolute;
  inset: 0;
}

.kin-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 14px;
  color: #aeb6c2;
  pointer-events: none;
}
.kin-spinner {
  width: 34px;
  height: 34px;
  border: 3px solid #2a2f37;
  border-top-color: #4995e0;
  border-radius: 50%;
  animation: kin-spin 0.9s linear infinite;
}
@keyframes kin-spin {
  to {
    transform: rotate(360deg);
  }
}

.kin-views {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 29; // sit above the click-catcher so menu items remain clickable
  display: flex;
  gap: 6px;
  background: rgba(27, 31, 37, 0.8);
  padding: 5px;
  border-radius: 10px;
  backdrop-filter: blur(6px);
}
.kin-views__sep {
  width: 1px;
  align-self: stretch;
  background: #353b44;
  margin: 2px 2px;
}
.kin-view-btn {
  background: transparent;
  border: none;
  color: #aeb6c2;
  font-size: 12.5px;
  padding: 6px 12px;
  border-radius: 7px;
  cursor: pointer;
  &:hover {
    color: #fff;
  }
  &--active {
    background: #4995e0;
    color: #fff;
  }
  &--icon {
    min-width: 34px;
    padding: 6px 8px;
    font-weight: 700;
    text-align: center;
  }
  &--menu {
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
}

.kin-caret {
  font-size: 10px;
  opacity: 0.8;
}

.kin-dropdown {
  position: relative;
}

.kin-menu-catcher {
  position: absolute;
  inset: 0;
  z-index: 28;
}

.kin-menu {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  left: auto;
  z-index: 25;
  min-width: 156px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  background: rgba(27, 31, 37, 0.97);
  border: 1px solid #2a2f37;
  border-radius: 10px;
  padding: 6px;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(8px);

  &--wide {
    min-width: 196px;
  }

  &__item {
    display: flex;
    align-items: center;
    gap: 4px;
    width: 100%;
    text-align: left;
    background: transparent;
    border: none;
    color: #c7cdd6;
    font-size: 13px;
    padding: 8px 10px;
    border-radius: 7px;
    cursor: pointer;
    &:hover {
      background: #232831;
      color: #fff;
    }
    &--active {
      color: #fff;
    }
  }
  &__check {
    display: inline-block;
    width: 14px;
    flex: 0 0 14px;
    color: #4995e0;
    font-weight: 700;
  }
  &__divider {
    height: 1px;
    background: #2a2f37;
    margin: 4px 2px;
  }
  &__row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    padding: 6px 10px;
    font-size: 13px;
    color: #c7cdd6;
  }
  &__size {
    display: flex;
    gap: 4px;
  }
}

.kin-panel {
  position: absolute;
  left: 50%;
  transform: translateX(-50%);
  bottom: 22px;
  width: min(560px, calc(100% - 48px));
  background: rgba(24, 28, 34, 0.92);
  border: 1px solid #2a2f37;
  border-radius: 14px;
  padding: 12px 18px;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.45);

  &--expanded {
    width: min(680px, calc(100% - 48px));
  }

  &__top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 16px;
    margin-bottom: 10px;
  }
  &__title {
    font-size: 17px;
    font-weight: 700;
  }
  &__tags {
    display: flex;
    gap: 8px;
    margin-top: 8px;
    flex-wrap: wrap;
  }
  &__desc {
    margin: 0 0 14px;
    font-size: 13px;
    line-height: 1.5;
    color: #b9c0cb;
  }
}

.kin-tag {
  font-size: 11px;
  font-weight: 600;
  color: #fff;
  padding: 3px 9px;
  border-radius: 20px;
  letter-spacing: 0.3px;
  &--ghost {
    background: transparent !important;
    border: 1px solid #3a414c;
    color: #aeb6c2;
  }
}

.kin-angle {
  text-align: right;
  flex: 0 0 auto;
  &__value {
    display: block;
    font-size: 26px;
    font-weight: 700;
    line-height: 1;
    font-variant-numeric: tabular-nums;
  }
  &__dir {
    font-size: 12px;
    color: #8b94a3;
    text-transform: capitalize;
  }
}

.kin-controls {
  display: flex;
  align-items: center;
  gap: 14px;
}
.kin-play {
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: #4995e0;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  &:hover {
    background: #5aa6f0;
  }
}
.kin-slider {
  flex: 1;
  accent-color: #4995e0;
  cursor: pointer;
}
.kin-range-label {
  flex: 0 0 auto;
  font-size: 11px;
  color: #6f7886;
  font-variant-numeric: tabular-nums;
}

/* ---- Tablet / mobile: sidebar becomes a slide-in drawer ---- */
@media (max-width: 860px) {
  .kin-menu-btn {
    display: inline-flex;
  }

  .kin-sidebar {
    position: absolute;
    top: 0;
    left: 0;
    bottom: 0;
    width: min(320px, 86vw);
    flex: none;
    z-index: 40;
    transform: translateX(-100%);
    transition: transform 0.25s ease;
    box-shadow: 0 0 40px rgba(0, 0, 0, 0.55);

    &--open {
      transform: translateX(0);
    }
    &__close {
      display: inline-flex;
      align-items: center;
      justify-content: center;
    }
  }

  .kin-page--drawer-open .kin-backdrop {
    display: block;
  }

  // Compact dropdown toolbar pinned to the top-right on narrow screens.
  .kin-views {
    top: 10px;
    right: 10px;
    left: auto;
    max-width: none;
    flex-wrap: nowrap;
    justify-content: flex-end;
    gap: 4px;
    padding: 4px;
  }
  .kin-view-btn {
    flex: 0 0 auto;
    white-space: nowrap;
    font-size: 12px;
    padding: 6px 9px;
  }

  .kin-panel {
    bottom: 14px;
    padding: 10px 12px;
    width: calc(100% - 20px);
  }
  .kin-controls {
    gap: 10px;
  }
  .kin-play {
    width: 36px;
    height: 36px;
  }
}

@media (max-width: 480px) {
  .kin-view-btn {
    font-size: 11px;
    padding: 5px 7px;
  }
  .kin-play {
    width: 34px;
    height: 34px;
  }
  .kin-controls {
    gap: 8px;
  }
  .kin-range-label {
    font-size: 10px;
  }
}
</style>
