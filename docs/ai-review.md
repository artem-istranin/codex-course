# Automated Codex pull request reviews

The `AI Review` workflow posts Codex feedback as a comment on same-repository
pull requests targeting `main`. It runs when a PR is opened, updated, or
reopened. Fork and Dependabot PRs are skipped before secrets are used. Tests,
coverage, and Terraform validation run separately in `CI`.

## Set up the repository

1. Commit these three files together:
   - [`.github/workflows/ai-review.yml`](../.github/workflows/ai-review.yml)
   - [`.github/codex/review-config.toml`](../.github/codex/review-config.toml)
   - [`.github/codex/prompts/review.md`](../.github/codex/prompts/review.md)
2. Under **Settings > Secrets and variables > Actions**, add repository secrets
   named `OPENAI_API_KEY` and `CONTEXT7_API_KEY`. The OpenAI key needs API credit
   and access to the model configured in `review-config.toml`. Obtain the
   Context7 key from your [Context7 dashboard](https://context7.com/dashboard).
   API usage is billed separately from a ChatGPT subscription.
3. Keep the default GitHub token permissions read-only. Each job declares its
   required permissions: the reviewer can read PR context, and only the feedback
   job has `pull-requests: write`. The workflow uses GitHub's automatic job
   token, so no personal access token is needed. It posts comments and does not
   need the setting that allows Actions to create or approve pull requests.
4. Merge the three files into `main` before testing automatic reviews. The
   `pull_request_target` event uses the base repository's workflow; edits to
   the workflow, prompt, or configuration in a PR take effect after merge.
5. Open a small PR from a branch in the same repository. Check the `AI Review`
   run and its comment on the PR. Push another commit to trigger a new review.

When adapting this to another repository, update the target branch if it is
not `main`. Remove any previous Codex review and feedback jobs from your CI
workflow to avoid duplicate reviews. If AI review is not configured, disable
the workflow and do not require its check for merging.

## How the review runs

The workflow checks out the merge commit with full history and without keeping
Git credentials. It copies the prompt and configuration from `PR_BASE_SHA`
into a temporary Codex home. The PR cannot replace those trusted files in the
running review. An explicit untrusted project entry disables configuration
from the PR checkout.

A commit-pinned `openai/codex-action` installs the pinned CLI and starts the
OpenAI Responses API proxy with `drop-sudo`. This setup-only invocation has no
prompt. The sandbox preflight checks that the checkout matches the event's
head commit and that Codex can inspect the diff. The final review step runs
`codex exec` with ephemeral session storage, ignored execution rules, and
strict configuration validation.

The configuration selects `gpt-5.6-sol` with `xhigh` reasoning effort. Change
that deliberately for your account's availability and cost requirements.
Keep the action commit, CLI version, and configuration compatible when
upgrading; validate the sandbox again after changes.

The review prompt prioritizes correctness bugs, security issues, behavioral
regressions, and missing tests. It asks for concise findings with severity and
file/line references, or a clear statement that no findings were found. The
infrastructure supplies read-only GitHub MCP access to PR context and Context7
access to current documentation without changing that review policy.

Codex's final response is passed as data to a separate feedback job. That job
checks that the PR is still open and its head still matches the reviewed
commit, then posts a normal PR comment. It does not check out code or run
Codex. New runs cancel older runs for the same PR. A push can still race with
comment publication, so check the run's reviewed commit when reading feedback.

## Security boundaries

`pull_request_target` grants access to base-repository secrets. Its workflow
must never install dependencies, run tests, build the application, or execute
scripts from the checked-out PR. Keep those operations in ordinary CI.

- The workflow, prompt, and configuration come from the trusted base. Automatic
  project instructions are disabled. The trusted runtime configuration directs
  Codex to read applicable repository instructions from the base commit and
  treat PR files and discussion as review evidence.
- Repository inspection uses a read-only permission profile with shell network
  access restricted to the GitHub MCP and Context7 hosts. Apps, hooks, memories,
  subagents, remote plugins, and web search are disabled.
- The shell environment allowlist excludes both MCP credentials. The OpenAI
  key is supplied only to the action's proxy setup. Do not add secrets to the
  shell allowlist or persist checkout credentials.
- The model's GitHub connection exposes only `pull_request_read` and uses a
  read-only token. Only the separate feedback job can write a comment; model
  output is supplied through an environment variable, never inserted into
  executable JavaScript or shell source.
- Use disposable GitHub-hosted runners. `drop-sudo` changes runner privileges
  and should not be reused on a persistent shared machine.

These controls limit what the reviewer can do; they do not make its reasoning
immune to prompt injection. Keep deterministic CI and human review requirements
appropriate to your repository. The reviewer inspects source and CI results;
it does not independently execute the test suite or approve merges.

## Troubleshooting

- **No review run:** confirm the workflow is on `main`, the PR targets `main`,
  and it comes from this repository. Fork and Dependabot skips are intentional.
- **Missing secret or MCP startup failure:** configure both repository secrets.
  Context7 and GitHub MCP are required, so connection failures stop the review.
- **Comment publication denied:** check organization policy and the feedback
  job's `pull-requests: write` permission.
- **API credit or model error:** check API billing and model access for the
  project that owns the OpenAI key.
- **Sandbox preflight failure:** inspect the checkout and runtime error. Do not
  bypass the sandbox or change to `unsafe` to make the job pass.
- **Workflow edits appear ignored:** that PR still runs the base branch's
  trusted version. Test the new version after merging it.

See the [Codex GitHub Action guide](https://developers.openai.com/codex/github-action),
the [action source](https://github.com/openai/codex-action), and GitHub's
[pull_request_target security guidance](https://docs.github.com/en/actions/reference/security/securely-using-pull_request_target)
before changing the trust boundaries.

Run `node --test .github/codex/tests/*.test.mjs` to verify trusted-file loading
and comment publication behavior without API calls. CI runs these checks too.
