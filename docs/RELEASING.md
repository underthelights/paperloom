# Release process

1. Work on a feature branch from `develop`; keep changes reviewable.
2. Run unit tests and relevant native tests. Every pull request runs CI.
3. Merge to `develop` to run CI. When a downloadable development build is needed, open Actions → Release → Run workflow and select `develop` (or run `gh workflow run release.yml --ref develop`). The release workflow computes a numbered prerelease from package.json's base version and its run number; it does not rewrite the branch. Ordinary merges do not publish development ZIPs.
4. Promote reviewed changes to `main`, set matching stable versions in package.json and package-lock.json, and update CHANGELOG.md.
5. Push an annotated `vX.Y.Z` tag matching package.json. Release CI checks the version, builds a clean macOS arm64 app, runs a native smoke test, and publishes the ZIP with SHA-256 checksums.

Never reuse or force-move published tags. Failed builds do not publish releases. No scheduled empty commits or meaningless version bumps. Public artifacts must never include local seeds, data directories, analysis prompts, logs, or credentials.

Development builds intentionally use a separate app name, bundle identifier, and data directory. Stable and development libraries are not automatically synchronized.

## Publication and local storage

Release publication runs only for `v*` tag pushes or an explicit workflow dispatch. For dispatch, select `develop`; dispatching on `main` does not build or publish. A development publication is skipped if its tested commit has already been superseded on `develop`. Stable releases still require the existing matching tag.

The workflow's 14-day artifact retention applies to GitHub Actions artifacts, not published release assets. Existing releases and local backups are not deleted by this policy. Explicit publication reduces unnecessary builds without silently discarding rollback data.

A published development release and the installed application are separate. For example, publishing `v2.2.0-dev.15` does not upgrade an installed `2.1.1` app. There is no automatic updater. The canonical stable installation is `/Applications/Paperloom.app`; do not add a local development app without an explicit request. Development builds use their separate data directory. Never delete library databases or research files to clean up release artifacts.
