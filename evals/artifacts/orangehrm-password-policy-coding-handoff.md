# OrangeHRM Password Policy — Coding Handoff Evaluation

Case: `GH-ORANGEHRM-PASSWORD-POLICY`

Pinned repository: `orangehrm/orangehrm@56e23b3b09e7af29317a0943523b825843fff527`

This handoff validates repository-aware scoping; it does not authorize or
implement a change in OrangeHRM.

## Repository baseline

- Frontend `usePasswordPolicy.ts` calls
  `POST /api/v2/auth/public/validation/password`, returns the first server
  message, and stores strength.
- `PasswordInput.vue` debounces the server validation, limits input to 64
  characters, confirms matching values, and displays strength.
- Backend search identifies `PasswordStrengthService.php`,
  `PasswordStrengthValidation.php`, `PasswordStrengthValidationAPI.php`, the
  core `Password` validator, authentication provider, config service, migration,
  and fixtures. These must be inspected before implementation.

## Vertical slices

1. Policy read model: authorized admin reads effective policy, defaults,
   version, scope, and update permission. No secret or password values are
   returned.
2. Policy update: authorized admin validates and saves a new version with
   effective time and audit record. Invalid or unauthorized updates are durable
   no-ops.
3. Enforcement parity: all server password-write paths use the effective
   policy. Frontend validation is advisory UX and cannot be the only guard.
4. Transition and rollback: define treatment of existing accounts, invitations,
   reset links, active sessions, and rollback to a prior policy version.

## Required tests

- `OBL-OHR-CODE-PROBE`: map admin route/API/service/config/migration and every
  password write path before editing; report paths not found instead of
  inventing them.
- `OBL-OHR-CODE-TEST`: authorized read/update, permission denial, invalid policy,
  create/reset/change/invitation enforcement, frontend/backend message parity,
  effective-time transition, audit, rollback, and concurrent update conflict.

Forbidden: client-only enforcement, plaintext password logging, changing the
public validation endpoint without compatibility analysis, or assuming the old
issue proves current roadmap approval.

Completion: `REVIEW_COMPLETE_WITH_GAPS` — repository anchors and safe task/test
shape are established; backend path inspection, implementation, and executed
tests remain required.
