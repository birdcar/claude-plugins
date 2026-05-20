#!/usr/bin/env node
// Per-skill validator template — generated into every new skill's evals/ directory
// by skill-forge. Specializes the plugin-level scripts/validate-skill.mjs with
// the skill's name and component manifest so improve-skill has deterministic
// ground truth across versions.
//
// Source: Inspired by walkinglabs/learn-harness-engineering harness-creator (MIT)
//         and adapted to the per-skill self-improvement pattern.
//
// Substitute the following placeholders when the generator copies this file:
//   {{SKILL_NAME}}     — the kebab-case skill name (e.g., "forge-harness")
//   {{COMPONENT_MANIFEST_JSON}} — JSON-encoded array of required files relative to the skill dir
//                         (e.g., '["SKILL.md","trigger-tests.md","evals/evals.json"]')
//   {{MIN_OVERALL}}    — the minimum acceptable plugin-level score (default 70)

import { spawnSync } from 'node:child_process';
import { access, readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const SKILL_DIR = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SKILL_NAME = '{{SKILL_NAME}}';
// Generator replaces the JSON.parse argument with a JSON-encoded array of
// component-manifest paths (relative to the skill directory).
const COMPONENT_MANIFEST = JSON.parse('{{COMPONENT_MANIFEST_JSON}}');
const MIN_OVERALL = Number('{{MIN_OVERALL}}' || 70);

const args = parseArgs(process.argv.slice(2));

if (args.help) {
  console.log(`Usage: node evals/validate.mjs [--json] [--min-score N]

Per-skill validator for "${SKILL_NAME}". Wraps the plugin-level
validate-skill.mjs and adds component-manifest assertions.

Exit code is 0 when the skill scores at least --min-score (default ${MIN_OVERALL}).`);
  process.exit(0);
}

// 1. Run the plugin-level deterministic validator on this skill directory.
const pluginValidator = path.resolve(SKILL_DIR, '..', '..', '..', 'scripts', 'validate-skill.mjs');
const pluginResult = spawnSync('node', [pluginValidator, '--target', SKILL_DIR, '--json'], {
  encoding: 'utf8',
});

if (pluginResult.error) {
  console.error(`Failed to invoke ${pluginValidator}: ${pluginResult.error.message}`);
  process.exit(2);
}

let pluginScore;
try {
  pluginScore = JSON.parse(pluginResult.stdout);
} catch (err) {
  console.error(`Plugin validator returned non-JSON output:\n${pluginResult.stdout}`);
  process.exit(2);
}

// 2. Add component-manifest assertions specific to this skill.
const manifestChecks = await Promise.all(
  COMPONENT_MANIFEST.map(async (relPath) => {
    const fullPath = path.join(SKILL_DIR, relPath);
    const present = await fileExists(fullPath);
    return { pass: present, message: `Component manifest: ${relPath}` };
  })
);

// 3. Assert evals.json has at least 5 cases each with prompt/expected_output/expectations.
const evalsPath = path.join(SKILL_DIR, 'evals', 'evals.json');
let evalsCheck = { pass: false, message: 'evals.json has >= 5 well-formed cases' };
try {
  const evalsContent = JSON.parse(await readFile(evalsPath, 'utf8'));
  const cases = Array.isArray(evalsContent.evals) ? evalsContent.evals : [];
  const wellFormed =
    cases.length >= 5 &&
    cases.every(
      (c) =>
        typeof c.prompt === 'string' &&
        c.prompt.length > 0 &&
        typeof c.expected_output === 'string' &&
        c.expected_output.length > 0 &&
        Array.isArray(c.expectations) &&
        c.expectations.length >= 3
    );
  evalsCheck = { pass: wellFormed, message: 'evals.json has >= 5 well-formed cases' };
} catch {
  // file missing or invalid — already a fail
}

const specializedChecks = [...manifestChecks, evalsCheck];
const passed = specializedChecks.filter((c) => c.pass).length;
const specializationScore = Math.round((passed / specializedChecks.length) * 100);

// 4. Combine.
const report = {
  skill_name: SKILL_NAME,
  plugin_validator: pluginScore,
  specialization: {
    score: specializationScore,
    passed,
    total: specializedChecks.length,
    checks: specializedChecks,
  },
  combined_overall: Math.round((pluginScore.overall + specializationScore) / 2),
};

if (args.json) {
  console.log(JSON.stringify(report, null, 2));
} else {
  console.log(`Skill: ${SKILL_NAME}`);
  console.log(
    `Plugin validator: ${pluginScore.overall}/100 (bottleneck: ${pluginScore.bottleneck})`
  );
  console.log(
    `Specialization checks: ${specializationScore}/100 (${passed}/${specializedChecks.length})`
  );
  for (const check of specializedChecks) {
    console.log(`  ${check.pass ? 'PASS' : 'FAIL'} ${check.message}`);
  }
  console.log(`Combined: ${report.combined_overall}/100`);
}

if (report.combined_overall < (Number(args.minScore) || MIN_OVERALL)) {
  process.exitCode = 1;
}

function parseArgs(argv) {
  const args = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      args._.push(token);
      continue;
    }
    const [rawKey, inlineValue] = token.slice(2).split('=', 2);
    const key = rawKey.replace(/-([a-z])/g, (_, l) => l.toUpperCase());
    if (inlineValue !== undefined) args[key] = inlineValue;
    else if (argv[i + 1] && !argv[i + 1].startsWith('--')) {
      args[key] = argv[i + 1];
      i += 1;
    } else args[key] = true;
  }
  return args;
}

async function fileExists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}
