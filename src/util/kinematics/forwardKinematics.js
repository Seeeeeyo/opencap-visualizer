import * as THREE from 'three'
import skeletonModel from './skeletonModel.json'

export { skeletonModel }

// Bodies in topological (parent-before-child) order.
export const BODY_ORDER = skeletonModel.order

// Map of body -> array of descendant bodies (the chain that moves when the body's
// joint is articulated). Includes the body itself.
export const DESCENDANTS = (() => {
  const children = {}
  BODY_ORDER.forEach((b) => {
    children[b] = []
  })
  BODY_ORDER.forEach((b) => {
    const p = skeletonModel.bodies[b].parent
    if (p) children[p].push(b)
  })
  const out = {}
  const collect = (b) => {
    let list = [b]
    children[b].forEach((c) => {
      list = list.concat(collect(c))
    })
    return list
  }
  BODY_ORDER.forEach((b) => {
    out[b] = collect(b)
  })
  return out
})()

const _offsetVecs = {}
BODY_ORDER.forEach((b) => {
  _offsetVecs[b] = new THREE.Vector3().fromArray(skeletonModel.bodies[b].offset)
})

const _rootPos = new THREE.Vector3().fromArray(skeletonModel.rootPosition)

const DEG2RAD = Math.PI / 180

export function quaternionFromAxisAngleDeg(axis, deg) {
  const a = new THREE.Vector3(axis[0], axis[1], axis[2]).normalize()
  return new THREE.Quaternion().setFromAxisAngle(a, deg * DEG2RAD)
}

// Compute world transforms for every body given a map of local rotations
// (body name -> THREE.Quaternion, relative to the parent). Missing entries are identity.
// Returns { body: { position: Vector3, quaternion: Quaternion } }.
export function computeWorldTransforms(localRotations = {}) {
  const out = {}
  for (const body of BODY_ORDER) {
    const info = skeletonModel.bodies[body]
    const local = localRotations[body] || new THREE.Quaternion()

    if (info.parent === null) {
      const worldQuat = local.clone()
      out[body] = { position: _rootPos.clone(), quaternion: worldQuat }
    } else {
      const parent = out[info.parent]
      const worldQuat = parent.quaternion.clone().multiply(local)
      const position = _offsetVecs[body]
        .clone()
        .applyQuaternion(parent.quaternion)
        .add(parent.position)
      out[body] = { position, quaternion: worldQuat }
    }
  }
  return out
}

// Build the local-rotation map for a measurement at a given joint angle (degrees).
export function localRotationsForMeasurement(measurement, angleDeg) {
  const map = {}
  if (measurement.prePose) {
    measurement.prePose.forEach((p) => {
      map[p.body] = quaternionFromAxisAngleDeg(p.axis, p.deg)
    })
  }
  const jointQuat = quaternionFromAxisAngleDeg(measurement.axis, angleDeg)
  if (map[measurement.jointBody]) {
    map[measurement.jointBody] = map[measurement.jointBody].multiply(jointQuat)
  } else {
    map[measurement.jointBody] = jointQuat
  }
  return map
}
