# Automated Codex pull request reviews

The [AI Review workflow](../.github/workflows/ai-review.yml) runs on opened,
updated, and reopened PRs to `main` from branches in this repository. It uses
Codex to inspect the diff and posts the response as a PR comment. Fork PRs are
skipped because this workflow uses a repository secret.

## Setup

1. Add `OPENAI_API_KEY` under **Settings > Secrets and variables > Actions**.
   The key's project needs API credit. API billing is separate from a ChatGPT
   subscription. No additional MCP services, keys, or personal access token
   are needed for the review.
2. Merge the workflow, [configuration](../.github/codex/review-config.toml), and
   [review prompt](../.github/codex/prompts/review.md) into `main`. The workflow
   uses `pull_request_target`, so these files are loaded from the base branch.
   Changes to them take effect after merge.
3. Open a small PR from another branch in the repository and check its
   `AI Review` run and feedback comment. Push a commit to trigger another review.

Keep GitHub's default token permissions read-only. Only the feedback job has
`pull-requests: write`; it posts comments, not review approvals. When adapting
this workflow, change the target branch if necessary and remove old Codex jobs
from CI to avoid duplicate comments.

## How it works

The workflow checks out the merge commit without retaining Git credentials,
then copies the prompt and configuration from the base commit into a temporary
Codex home. Configuration from the PR checkout is disabled.

The pinned Codex action runs the original review prompt with `drop-sudo` and a
read-only sandbox that blocks shell network access. The reviewer can inspect
source but cannot change files. It has no MCP connections and uses the pinned
CLI's default model. Set the action's `model` and `effort` inputs if needed.

A separate job posts the action's final response as text after checking that
the PR is still open at the reviewed head. This job holds the comment-writing
token and does not check out code or run Codex. New runs cancel older runs for
the same PR; a push can still race with publication.

Do not add dependency installation, builds, or test execution from the PR
checkout to this secret-bearing workflow. Keep tests, coverage, and Terraform
validation in ordinary CI. AI feedback complements those checks and human review.

If a run fails, check the API key, API credit, and action logs. A newly edited
workflow still runs its base-branch version until merged. Keep the action and
CLI versions compatible when upgrading; do not bypass the sandbox to fix errors.

Run `node --test .github/codex/tests/*.test.mjs` for local checks of trusted-file
loading and comment publication. CI runs these checks too.

See the [Codex GitHub Action guide](https://developers.openai.com/codex/github-action)
and GitHub's [pull_request_target guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
for the underlying action and event behavior.
