# Release process

1. Work on a feature branch from `develop`; keep changes reviewable.
2. Run unit tests and relevant native tests. Every pull request runs CI.
3. Merge to `develop` for a numbered development prerelease. CI computes the dev version from package.json's base version and the run number; it does not rewrite the branch.
4. Promote reviewed changes to `main`, set matching stable versions in package.json and package-lock.json, and update CHANGELOG.md.
5. Push an annotated `vX.Y.Z` tag matching package.json. Release CI checks the version, builds a clean macOS arm64 app, runs a native smoke test, and publishes the ZIP with SHA-256 checksums.

Never reuse or force-move published tags. Failed builds do not publish releases. No scheduled empty commits or meaningless version bumps. Public artifacts must never include local seeds, data directories, analysis prompts, logs, or credentials.

Development builds intentionally use a separate app name, bundle identifier, and data directory. Stable and development libraries are not automatically synchronized.
