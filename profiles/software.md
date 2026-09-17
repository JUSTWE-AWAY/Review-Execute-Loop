# Software Profile

Use for code changes, debugging, tests, build work, and technical maintenance.

## Required Behavior

- Inspect existing conventions before editing.
- Keep the patch scoped; do not bundle unrelated refactors.
- Preserve user changes and avoid destructive version-control commands.
- Add or update tests in proportion to behavior and blast radius.
- Record commands and actual test/build outcomes, including failures and skipped checks.
- Do not claim a bug is fixed merely because code compiles.
- Database migrations, deployments, releases, permission changes, paid services, and external messages require explicit authorization.
- Stop for contradictory requirements, security concerns, or a needed public/API behavior change outside scope.

Generated files and formatting changes should be limited to what the task requires.
