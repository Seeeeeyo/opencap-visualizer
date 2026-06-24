// Biomechanics kinematics measurements demonstrated on the OpenSim (LaiUhlrich2022) skeleton.
//
// Each measurement isolates a single joint degree-of-freedom and animates it through its
// functional range of motion using forward kinematics.
//
// Coordinate convention (neutral standing pose, body-local frame == world frame):
//   +x = anterior (forward)   -x = posterior (backward)
//   +y = superior (up)        -y = inferior (down)
//   +z = right (lateral R)    -z = left
//
// `jointBody` is the body whose rotation relative to its parent is animated.
// `axis` is the rotation axis in that body's local (neutral) frame; the sign is chosen
// so that `max` corresponds to the anatomically-named positive direction.
// `prePose` optionally fixes other joints first (e.g. flex the elbow so shoulder
// rotation becomes visible).

export const PLANES = {
  sagittal: { label: 'Sagittal', color: '#4995e0' },
  frontal: { label: 'Frontal', color: '#e35335' },
  transverse: { label: 'Transverse', color: '#f0b429' },
}

const M = [
  // ----------------------------- HIP -----------------------------
  {
    id: 'hip_flexion',
    group: 'Hip',
    label: 'Hip flexion / extension',
    plane: 'sagittal',
    jointBody: 'femur_r',
    axis: [0, 0, 1],
    min: -20,
    max: 120,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    normalRom: '120° flexion · 20° extension',
    description:
      'Movement of the thigh in the sagittal plane about a medio-lateral axis. Flexion brings the thigh forward and up (e.g. lifting the knee); extension drives it behind the body.',
  },
  {
    id: 'hip_abduction',
    group: 'Hip',
    label: 'Hip abduction / adduction',
    plane: 'frontal',
    jointBody: 'femur_r',
    axis: [-1, 0, 0],
    min: -25,
    max: 45,
    neutral: 0,
    dir: ['Abduction', 'Adduction'],
    normalRom: '45° abduction · 25° adduction',
    description:
      'Movement of the thigh in the frontal plane about an antero-posterior axis. Abduction moves the leg away from the midline; adduction brings it back across the body.',
  },
  {
    id: 'hip_rotation',
    group: 'Hip',
    label: 'Hip internal / external rotation',
    plane: 'transverse',
    jointBody: 'femur_r',
    axis: [0, 1, 0],
    min: -45,
    max: 45,
    neutral: 0,
    dir: ['Internal', 'External'],
    prePose: [{ body: 'tibia_r', axis: [0, 0, -1], deg: 80 }],
    normalRom: '45° internal · 45° external',
    description:
      'Rotation of the thigh about its long (vertical) axis. Internal rotation turns the knee inward toward the midline; external rotation turns it outward. Shown with the knee flexed so the motion is visible.',
  },
  // ----------------------------- KNEE -----------------------------
  {
    id: 'knee_flexion',
    group: 'Knee',
    label: 'Knee flexion / extension',
    plane: 'sagittal',
    jointBody: 'tibia_r',
    axis: [0, 0, -1],
    min: 0,
    max: 140,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    normalRom: '0° (extension) → 140° flexion',
    description:
      'Bending and straightening of the knee in the sagittal plane. Flexion swings the shank posteriorly (heel toward the buttock); extension straightens the leg.',
  },
  // ----------------------------- ANKLE / FOOT -----------------------------
  {
    id: 'ankle_dorsiflexion',
    group: 'Ankle & Foot',
    label: 'Ankle dorsiflexion / plantarflexion',
    plane: 'sagittal',
    jointBody: 'talus_r',
    axis: [0, 0, 1],
    min: -50,
    max: 20,
    neutral: 0,
    dir: ['Dorsiflexion', 'Plantarflexion'],
    normalRom: '20° dorsiflexion · 50° plantarflexion',
    description:
      'Movement of the foot at the ankle (talocrural) joint in the sagittal plane. Dorsiflexion lifts the forefoot toward the shin; plantarflexion points the toes down.',
  },
  {
    id: 'subtalar_inversion',
    group: 'Ankle & Foot',
    label: 'Subtalar inversion / eversion',
    plane: 'frontal',
    jointBody: 'calcn_r',
    axis: [1, 0, 0],
    min: -20,
    max: 20,
    neutral: 0,
    dir: ['Inversion', 'Eversion'],
    normalRom: '~20° inversion · ~10° eversion',
    description:
      'Rotation of the rearfoot at the subtalar joint. Inversion turns the sole inward toward the midline; eversion turns the sole outward.',
  },
  // ----------------------------- TRUNK / LUMBAR -----------------------------
  {
    id: 'trunk_flexion',
    group: 'Trunk',
    label: 'Trunk flexion / extension',
    plane: 'sagittal',
    jointBody: 'torso',
    axis: [0, 0, -1],
    min: -30,
    max: 80,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    normalRom: '80° flexion · 30° extension',
    description:
      'Forward and backward bending of the trunk relative to the pelvis in the sagittal plane. Flexion bends the torso forward; extension arches it back.',
  },
  {
    id: 'trunk_lateral',
    group: 'Trunk',
    label: 'Trunk lateral flexion',
    plane: 'frontal',
    jointBody: 'torso',
    axis: [1, 0, 0],
    min: -35,
    max: 35,
    neutral: 0,
    dir: ['Right bend', 'Left bend'],
    normalRom: '~35° to each side',
    description:
      'Side-bending of the trunk in the frontal plane about an antero-posterior axis, tilting the torso toward the left or right.',
  },
  {
    id: 'trunk_rotation',
    group: 'Trunk',
    label: 'Trunk axial rotation',
    plane: 'transverse',
    jointBody: 'torso',
    axis: [0, 1, 0],
    min: -45,
    max: 45,
    neutral: 0,
    dir: ['Left rot.', 'Right rot.'],
    normalRom: '~45° to each side',
    description:
      'Twisting of the trunk about a vertical axis in the transverse plane, rotating the shoulders relative to the pelvis.',
  },
  // ----------------------------- SHOULDER -----------------------------
  {
    id: 'shoulder_flexion',
    group: 'Shoulder',
    label: 'Shoulder flexion / extension',
    plane: 'sagittal',
    jointBody: 'humerus_r',
    axis: [0, 0, 1],
    min: -60,
    max: 170,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    normalRom: '170° flexion · 60° extension',
    description:
      'Movement of the upper arm in the sagittal plane. Flexion raises the arm forward and overhead; extension drives it behind the body.',
  },
  {
    id: 'shoulder_abduction',
    group: 'Shoulder',
    label: 'Shoulder abduction / adduction',
    plane: 'frontal',
    jointBody: 'humerus_r',
    axis: [-1, 0, 0],
    min: 0,
    max: 170,
    neutral: 0,
    dir: ['Abduction', 'Adduction'],
    normalRom: '170° abduction',
    description:
      'Movement of the upper arm in the frontal plane. Abduction lifts the arm out to the side and overhead; adduction returns it to the body.',
  },
  {
    id: 'shoulder_rotation',
    group: 'Shoulder',
    label: 'Shoulder internal / external rotation',
    plane: 'transverse',
    jointBody: 'humerus_r',
    axis: [0, 1, 0],
    min: -90,
    max: 90,
    neutral: 0,
    dir: ['Internal', 'External'],
    prePose: [{ body: 'ulna_r', axis: [0, 0, 1], deg: 90 }],
    normalRom: '~70° internal · 90° external',
    description:
      'Rotation of the upper arm about its long axis. Demonstrated with the elbow flexed 90°: internal rotation swings the forearm across the body, external rotation swings it outward.',
  },
  // ----------------------------- ELBOW / FOREARM -----------------------------
  {
    id: 'elbow_flexion',
    group: 'Elbow & Forearm',
    label: 'Elbow flexion / extension',
    plane: 'sagittal',
    jointBody: 'ulna_r',
    axis: [0, 0, 1],
    min: 0,
    max: 145,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    normalRom: '0° → 145° flexion',
    description:
      'Bending and straightening of the elbow in the sagittal plane, bringing the forearm toward or away from the upper arm.',
  },
  {
    id: 'forearm_pronation',
    group: 'Elbow & Forearm',
    label: 'Forearm pronation / supination',
    plane: 'transverse',
    jointBody: 'radius_r',
    axis: [0, 1, 0],
    min: -80,
    max: 80,
    neutral: 0,
    dir: ['Pronation', 'Supination'],
    prePose: [{ body: 'ulna_r', axis: [0, 0, 1], deg: 90 }],
    normalRom: '~80° pronation · 80° supination',
    description:
      'Rotation of the forearm about its long axis, turning the palm down (pronation) or up (supination). Shown with the elbow flexed 90°.',
  },
  // ----------------------------- WRIST -----------------------------
  {
    id: 'wrist_flexion',
    group: 'Wrist',
    label: 'Wrist flexion / extension',
    plane: 'sagittal',
    jointBody: 'hand_r',
    axis: [0, 0, 1],
    min: -70,
    max: 70,
    neutral: 0,
    dir: ['Flexion', 'Extension'],
    prePose: [{ body: 'humerus_r', axis: [0, 0, 1], deg: 90 }],
    normalRom: '70° flexion · 70° extension',
    description:
      'Bending of the hand at the wrist in the sagittal plane. Flexion curls the palm toward the forearm; extension lifts the back of the hand up. Shown with the arm raised forward.',
  },
  // ----------------------------- PELVIS (whole-body relative to ground) -----------------------------
  {
    id: 'pelvic_tilt',
    group: 'Pelvis',
    label: 'Pelvic tilt (anterior / posterior)',
    plane: 'sagittal',
    jointBody: 'pelvis',
    axis: [0, 0, -1],
    min: -15,
    max: 30,
    neutral: 0,
    isolate: true,
    dir: ['Anterior', 'Posterior'],
    normalRom: '~30° anterior · 15° posterior',
    description:
      'Rotation of the whole pelvis about a medio-lateral axis. Anterior tilt rotates the top of the pelvis forward (increasing lumbar curve); posterior tilt rotates it back.',
  },
  {
    id: 'pelvic_obliquity',
    group: 'Pelvis',
    label: 'Pelvic obliquity (list)',
    plane: 'frontal',
    jointBody: 'pelvis',
    axis: [1, 0, 0],
    min: -20,
    max: 20,
    neutral: 0,
    isolate: true,
    dir: ['Right down', 'Right up'],
    normalRom: '~20° to each side',
    description:
      'Rotation of the pelvis in the frontal plane about an antero-posterior axis, raising one hip relative to the other (hip hike / drop).',
  },
  {
    id: 'pelvic_rotation',
    group: 'Pelvis',
    label: 'Pelvic axial rotation',
    plane: 'transverse',
    jointBody: 'pelvis',
    axis: [0, 1, 0],
    min: -30,
    max: 30,
    neutral: 0,
    isolate: true,
    dir: ['Left forward', 'Right forward'],
    normalRom: '~30° to each side',
    description:
      'Rotation of the pelvis about a vertical axis in the transverse plane, advancing one side of the pelvis forward.',
  },
]

export const MEASUREMENTS = M

export const MEASUREMENT_GROUPS = M.reduce((groups, m) => {
  let g = groups.find((x) => x.name === m.group)
  if (!g) {
    g = { name: m.group, items: [] }
    groups.push(g)
  }
  g.items.push(m)
  return groups
}, [])
