import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import test from "node:test";

const root = fileURLToPath(new URL("../../../", import.meta.url));
const workflow = readFileSync(join(root, ".github/workflows/ai-review.yml"), "utf8");

// Extract the executable literal block so tests exercise the actual workflow.
function stepBlock(name, key) {
  const step = workflow.split(`- name: ${name}\n`)[1];
  assert.ok(step, `Missing workflow step: ${name}`);
  const match = step.match(new RegExp(`^( +)${key}: \\|\\n`, "m"));
  assert.ok(match, `Missing ${key} block in ${name}`);
  const indent = match[1].length + 2;
  const lines = step.slice(match.index + match[0].length).split("\n");
  const body = [];
  for (const line of lines) {
    if (line.trim() && line.search(/\S/) < indent) break;
    body.push(line.slice(indent));
  }
  return body.join("\n");
}

test("PR changes cannot replace the trusted prompt or configuration", () => {
  const fixture = mkdtempSync(join(tmpdir(), "codex-review-trust-"));
  const git = (...args) => execFileSync("git", args, { cwd: fixture });
  const paths = [".github/codex/prompts/review.md", ".github/codex/review-config.toml"];
  try {
    git("init", "-q");
    for (const path of paths) {
      mkdirSync(dirname(join(fixture, path)), { recursive: true });
      writeFileSync(join(fixture, path), readFileSync(join(root, path)));
    }
    git("add", ".");
    git("-c", "user.name=Test", "-c", "user.email=test@example.invalid", "commit", "-qm", "fixture");
    for (const path of paths) writeFileSync(join(fixture, path), "UNTRUSTED REPLACEMENT");
    const codexHome = join(fixture, "trusted-home");
    execFileSync("bash", ["-euc", stepBlock("Prepare trusted Codex configuration", "run")], {
      cwd: fixture,
      env: { ...process.env, CODEX_HOME: codexHome, PR_BASE_SHA: "HEAD", GITHUB_WORKSPACE: fixture },
    });
    assert.deepEqual(readFileSync(join(codexHome, "review.md")), readFileSync(join(root, paths[0])));
    const config = readFileSync(join(codexHome, "config.toml"), "utf8");
    assert.ok(config.startsWith(readFileSync(join(root, paths[1]), "utf8")));
    assert.ok(config.includes('trust_level = "untrusted"'));
  } finally {
    rmSync(fixture, { recursive: true, force: true });
  }
});

const AsyncFunction = Object.getPrototypeOf(async function () {}).constructor;
const publish = new AsyncFunction("github", "context", "core", "process",
  stepBlock("Post Codex feedback for the reviewed head", "script"));

for (const [state, head, shouldPost] of [["open", "reviewed", true], ["open", "newer", false], ["closed", "reviewed", false]]) {
  test(`feedback for ${state} PR at ${head} head ${shouldPost ? "posts literal data" : "is skipped"}`, async () => {
    const comments = [];
    const body = "A finding\n${{ secrets.OPENAI_API_KEY }}\n`$(exit 1)`\nfinal_message=untrusted";
    const github = { rest: {
      pulls: { get: async () => ({ data: { state, head: { sha: head }, number: 42 } }) },
      issues: { createComment: async (args) => comments.push(args) },
    } };
    const context = { repo: { owner: "test", repo: "course" }, payload: { pull_request: { number: 42 } } };
    await publish(github, context, { notice() {} }, { env: { PR_HEAD_SHA: "reviewed", CODEX_FINAL_MESSAGE: body } });
    assert.deepEqual(comments, shouldPost ? [{ owner: "test", repo: "course", issue_number: 42, body }] : []);
  });
}
