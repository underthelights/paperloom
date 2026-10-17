# Review policy

Review behavioral changes, not only formatting. Prioritize data loss, identity collisions, prompt/source trust boundaries, URL fetching and SSRF, process cancellation, concurrency, persistent annotations, release privacy, and backward compatibility.

For each finding, record the triggering input, affected file/line, observed impact, and a focused regression test when appropriate. Do not invent findings. Separate verified bugs from untested risks. Never describe passing tests as proof of complete correctness.

CI checks Python tests, JavaScript syntax, and public artifact inputs. Release CI additionally validates the packaged Electron application with an empty isolated profile. Dependabot proposes weekly updates; never auto-merge a dependency solely because it is newer.

The owner's local Codex review automation checks new commits and CI failures daily. It reports only actionable changes, preserves uncommitted work, and develops fixes on review branches. The repository itself does not grant an AI service credentials or promise unattended merges into main.
