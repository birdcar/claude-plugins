#!/usr/bin/env node
// Per-skill validator for forge-harness.
// Wraps the plugin-level validator and adds an evals.json sanity check.
import { spawnSync } from 'node:child_process';
import { readFile } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const SKILL_DIR = path.resolve(__dirname, '..');
const PLUGIN_VALIDATOR = path.resolve(SKILL_DIR, '..', '..', 'scripts', 'validate-skill.mjs');
const EVALS_PATH = path.join(__dirname, 'evals.json');

const jsonMode = process.argv.includes('--json');

const plugin = spawnSync('node', [PLUGIN_VALIDATOR, '--target', SKILL_DIR, '--json'], {
  encoding: 'utf8',
});
if (plugin.error) {
  console.error(`Failed to invoke plugin validator: ${plugin.error.message}`);
  process.exit(2);
}
let pluginResult;
try {
  pluginResult = JSON.parse(plugin.stdout);
} catch (err) {
  console.error(`Plugin validator did not return JSON:\n${plugin.stdout}`);
  process.exit(2);
}

const evalsCheck = await validateEvals(EVALS_PATH);
const merged = {
  ...pluginResult,
  evals: evalsCheck,
  passed: pluginResult.overall >= 70 && evalsCheck.pass,
};

if (jsonMode) {
  console.log(JSON.stringify(merged, null, 2));
} else {
  console.log(`forge-harness validation`);
  console.log(`Overall: ${merged.overall}/100  Bottleneck: ${merged.bottleneck}`);
  console.log(`Evals check: ${evalsCheck.pass ? 'PASS' : 'FAIL'} — ${evalsCheck.message}`);
  console.log(`Result: ${merged.passed ? 'PASS' : 'FAIL'}`);
}

process.exitCode = merged.passed ? 0 : 1;

async function validateEvals(filePath) {
  let raw;
  try {
    raw = await readFile(filePath, 'utf8');
  } catch {
    return { pass: false, message: `evals.json missing at ${filePath}`, caseCount: 0 };
  }
  let data;
  try {
    data = JSON.parse(raw);
  } catch (err) {
    return { pass: false, message: `evals.json is not valid JSON: ${err.message}`, caseCount: 0 };
  }
  const cases = Array.isArray(data.evals) ? data.evals : [];
  if (cases.length < 5)
    return {
      pass: false,
      message: `evals.json has ${cases.length} cases; need >= 5`,
      caseCount: cases.length,
    };
  const bad = cases.filter(
    (c) =>
      !c.prompt || !c.expected_output || !Array.isArray(c.expectations) || c.expectations.length < 3
  );
  if (bad.length) {
    const ids = bad.map((c) => c.id ?? '?').join(', ');
    return {
      pass: false,
      message: `eval case(s) ${ids} missing prompt/expected_output or have <3 expectations`,
      caseCount: cases.length,
    };
  }
  return {
    pass: true,
    message: `${cases.length} cases, all with prompt + expected_output + 3+ expectations`,
    caseCount: cases.length,
  };
}
