# Detailed paper-to-code explanation contract

For each new single-paper analysis, read the complete available source and official implementation. Never claim all code paths were covered. Record inspected entry points, config/commit, coverage, and missing files. Do not execute downloaded research code.

## Related work and contents

In `related_work`, build a table from the actual Related Work, Introduction, Methods and bibliography: prior method; precise difference claimed by this paper; exact section/citation; relation type (adopted backbone / implemented alternative / experimental baseline / conceptual comparison); source URL. Mention in a bibliography is not evidence of adoption. Open the cited primary work when explaining its method. In `overview`, provide a section map explaining the purpose and dependency of each substantive section, including appendices when available. Distinguish the author's claim from your assessment.

## Tensor trace

In `tensor_trace`, follow the selected training AND inference paths in execution order: raw data → preprocessing → encoder → latent/patch tokens → conditioning → each core module → head → loss or sampler → output decoding/postprocessing → action execution if applicable.

For each core operation, give a row: step; file:function with immutable commit URL and line range; input shape/dtype/axis meanings/units; operation; output shape; why required; evidence (code/config/paper); unknowns. Track permute, reshape, flatten, concat, broadcast, normalization, embeddings, Q/K/V projections, attention mask, softmax or linear attention, residuals, output heads, scheduler timesteps, cache read/write/reset, loss reduction and masks when present. Do not substitute this generic list for the actual architecture. Record conditional branches and train/inference differences. Use symbolic dimensions when values are not specified. Numeric shapes must come from a named config or explicitly labeled toy example. Check reshape element counts, matrix contraction dimensions, concatenation axes, and broadcast compatibility.

For each important operation, explain in plain Korean what data is being combined and what information it preserves or discards, then provide the formula with symbols defined, then its actual code mapping. Include a small hand-computable example distinct from measured results. Never insert an attention formula into a model that uses a different operation. Separate source-confirmed shapes from inferred shapes; explain each inference. If source is missing, state precisely which part cannot be verified.

## Experiments and validation

In `experiments`, connect each major claim to dataset/split, protocol, baselines, metric direction/unit, main result table and ablation. Distinguish reported means/variance from unsupported significance claims. Explain what each ablation supports and what it does not establish. Connect the ablated module to its tensor-trace step. Preserve paper/code mismatches rather than silently resolving them. Checks must include related-work coverage, train/inference trace, shape compatibility, experiment-to-claim linkage, and missing evidence.

## Machine-readable model graph

Return `model_graph` with `center`, `nodes`, `edges`. Nodes: `id`, `label`, `owner`, `paper_url`, `code_url`, `concept`, `summary`. Edges: `source`, `target`, `kind` (`adopted`, `implementation`, `related`), `version`, `reason`, `evidence` (array of `{url,label}`). Keep at most 24 selected nodes. Every edge requires primary evidence URLs actually read and listed in report.sources. Related comparisons must state whether they are the authors' comparison or analyst comparison. `adopted` requires explicit use of the named version in paper or implementation; shared topic alone is `related`. Use an empty graph if evidence is insufficient. This graph is a technical relationship graph, not a bibliographic citation graph.
