# Maintaining the GitHub research archive

The research materials are maintained at **[SABIKGIT/a3p5-nemesis](https://github.com/SABIKGIT/a3p5-nemesis)** and accompany **[arXiv:2609.18245](https://arxiv.org/abs/2609.18245)**.

## Prepare an update

Clone the existing repository and work from its root:

```bash
git clone https://github.com/SABIKGIT/a3p5-nemesis.git
cd a3p5-nemesis
git switch -c research-update
```

Edit the relevant source files and keep the scientific outputs consistent with any methodological changes. The [contribution guide](../CONTRIBUTING.md) explains the evidence boundaries and the [reproduction guide](reproduce.md) describes verification modes.

## Verify and record the distribution

```bash
python scripts/verify.py
# After reviewing the intended changes:
python scripts/manifest.py --write
python scripts/manifest.py --check
git diff --check
git status --short
```

Use the scientific environment and optional reproduction modes when changing calculations or benchmark code. Preserve the imported archive provenance and historical reports; save new local reports as `verification/local-*.json`.

## Publish the reviewed changes

```bash
git add .
git commit -m "Update NEMESIS research materials"
git push -u origin research-update
```

Open a pull request to `main`, review the changes, and check the **Actions** results. The standard workflow verifies the file manifest and archived numerical evidence. Its manual `full_reproduction` option also replays saved models, refits the benchmark candidates and regenerates engineering tables in temporary storage.

## What belongs in the archive

Keep the manuscript sources, research inputs, recorded results, models, diagrams and attribution notices. The outer delivery ZIP is a transport package; it is not repository source. Local environments, caches, temporary outputs and `.env` files are excluded by `.gitignore`.

The repository preserves the original licensing status. See [LICENSE_STATUS.md](../LICENSE_STATUS.md) and [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md) before reusing material. Future releases can provide downloadable bundles without duplicating those transport archives in the source tree.
