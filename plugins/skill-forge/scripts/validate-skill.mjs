#!/usr/bin/env node
import { access, readFile, readdir, writeFile, mkdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

export const SUBSYSTEMS = ['instructions', 'state', 'verification', 'scope', 'lifecycle'];

const args = parseArgs(process.argv.slice(2));

if (args.help) {
  console.log(`Usage: node scripts/validate-skill.mjs [--target DIR] [--json] [--html FILE] [--min-score N]

Scores a Claude Code skill across five subsystems:
  instructions, state, verification, scope, lifecycle

The target should be the skill directory (the directory containing SKILL.md).
Exit code is 1 when the skill scores below --min-score (default 70).`);
  process.exit(0);
}

const target = path.resolve(args.target || args._[0] || process.cwd());
const minScore = Number(args.minScore || 70);
const artifacts = await loadSkillArtifacts(target);
const result = scoreSkill(artifacts);

if (args.html) {
  const htmlPath = path.resolve(args.html);
  await writeText(htmlPath, htmlReport(result, `Skill Assessment: ${path.basename(target)}`));
  console.log(`HTML report written to ${htmlPath}`);
}

if (args.json) {
  console.log(JSON.stringify(result, null, 2));
} else {
  console.log(formatScoreReport(result, target));
}

if (result.overall < minScore) {
  process.exitCode = 1;
}

// -------- Skill loading --------

export async function loadSkillArtifacts(skillDir) {
  const skillMd = await readMaybe(path.join(skillDir, 'SKILL.md'));
  const triggerTests = await readMaybe(path.join(skillDir, 'trigger-tests.md'));

  // Plugin root lives two levels up from a marketplace skill: {plugin}/skills/{skill-name}/.
  const pluginRoot = path.resolve(skillDir, '..', '..');
  const pluginJsonPath = path.join(pluginRoot, 'plugin.json');
  const pluginJsonRaw = await readMaybe(pluginJsonPath);
  let pluginJson = null;
  if (pluginJsonRaw) {
    try {
      pluginJson = JSON.parse(pluginJsonRaw);
    } catch {
      pluginJson = null;
    }
  }

  const docsDir = path.join(pluginRoot, 'docs');
  const contract = await readMaybe(path.join(docsDir, 'contract.md'));
  const spec = await readMaybe(path.join(docsDir, 'spec.md'));
  const learnings = await readMaybe(path.join(docsDir, 'learnings.md'));
  const historyRaw = await readMaybe(path.join(docsDir, 'history.json'));
  let historyValid = null; // null = absent, true = valid, false = invalid
  if (historyRaw !== null) {
    try {
      JSON.parse(historyRaw);
      historyValid = true;
    } catch {
      historyValid = false;
    }
  }

  const scriptsDir = path.join(skillDir, 'scripts');
  const scriptFiles = await listShallow(scriptsDir, /\.(mjs|py)$/);
  const scriptShebangs = await Promise.all(
    scriptFiles.map(async (file) => ({
      file,
      hasShebang: (await readMaybe(file))?.startsWith('#!') ?? false,
    }))
  );

  return {
    skillDir,
    skillMd,
    triggerTests,
    pluginRoot,
    pluginJson,
    pluginJsonExists: pluginJsonRaw !== null,
    contract,
    spec,
    learnings,
    historyExists: historyRaw !== null,
    historyValid,
    docsDirExists: await exists(docsDir),
    scriptFiles,
    scriptShebangs,
  };
}

// -------- Scoring --------

export function scoreSkill(a) {
  const { frontmatter, body } = parseSkillMd(a.skillMd || '');
  const description = (frontmatter.description || '').trim();
  const name = (frontmatter.name || '').trim();
  const bodyLines = body.split('\n');
  const firstHundred = bodyLines.slice(0, 100).join('\n');

  const checks = {
    instructions: [
      { pass: !!name && !!description, message: 'Frontmatter has name and description' },
      {
        pass: !!name && /^[a-z][a-z0-9-]*$/.test(name) && name.length <= 64,
        message: 'Name is kebab-case and <= 64 chars',
      },
      {
        pass: hasTriggerPhrases(description) && isThirdPerson(description),
        message: 'Description is third-person with trigger phrases',
      },
      {
        pass: hasNegativeCase(description) && description.length > 0 && description.length <= 1024,
        message: 'Description has negative cases and <= 1024 chars',
      },
      {
        pass: /(^|\n)#+\s*Critical Rules\b/i.test(firstHundred) && bodyLines.length <= 500,
        message: 'Body has Critical Rules in first 100 lines and <= 500 lines',
      },
    ],
    state: [
      { pass: !!a.contract, message: 'docs/contract.md present' },
      {
        pass: !!a.contract && /(^|\n)#+\s*Problem Statement\b/i.test(a.contract || ''),
        message: 'contract.md has Problem Statement section',
      },
      {
        pass: !!a.spec && /(^|\n)#+\s*Component Manifest\b/i.test(a.spec || ''),
        message: 'spec.md present with Component Manifest section',
      },
      { pass: a.learnings !== null, message: 'docs/learnings.md present' },
      {
        pass: !a.historyExists || a.historyValid === true,
        message: 'history.json valid JSON (or absent)',
      },
    ],
    verification: [
      { pass: !!a.triggerTests, message: 'trigger-tests.md present' },
      {
        pass:
          countNumberedUnder(
            a.triggerTests || '',
            /should\s+trigger/i,
            /should\s+not\s+trigger/i
          ) >= 10,
        message: 'trigger-tests.md has >= 10 should-trigger entries',
      },
      {
        pass: countNumberedUnder(a.triggerTests || '', /should\s+not\s+trigger/i, null) >= 10,
        message: 'trigger-tests.md has >= 10 should-not-trigger entries',
      },
      {
        pass: a.scriptShebangs.every((s) => s.hasShebang),
        message: 'All .mjs/.py scripts have shebang lines',
      },
      {
        pass: !!a.triggerTests && /\|.*pass/i.test(a.triggerTests || ''),
        message: 'trigger-tests.md has a results table',
      },
    ],
    scope: [
      {
        pass: hasNegativeCase(description),
        message: 'Description includes "Do NOT use" / "Do not use" phrase',
      },
      {
        pass: !a.pluginJsonExists || !!a.pluginJson?.version,
        message: 'plugin.json has version field (or absent)',
      },
      {
        pass: !a.pluginJsonExists || !!a.pluginJson?.description,
        message: 'plugin.json has description field (or absent)',
      },
      { pass: description.length <= 1024, message: 'Description within 1024-char budget' },
      {
        pass: hasTriggerPhrases(description),
        message: 'Description scopes activation via trigger phrases',
      },
    ],
    lifecycle: [
      { pass: a.docsDirExists, message: 'docs/ directory exists' },
      {
        pass: !!a.contract && !!a.spec && a.learnings !== null,
        message: 'docs/ has contract.md + spec.md + learnings.md',
      },
      {
        pass:
          /improve|retrospective/i.test(a.learnings || '') ||
          /(^|\n)##\s*\d{4}-\d{2}-\d{2}/.test(a.learnings || ''),
        message: 'learnings.md wired for retrospectives or has dated entry',
      },
      {
        pass: !a.historyExists || a.historyValid === true,
        message: 'history.json valid (or absent)',
      },
      {
        pass: bodyLines.length > 0 && bodyLines.length <= 500,
        message: 'SKILL.md body is non-empty and within 500-line budget',
      },
    ],
  };

  const subsystems = Object.fromEntries(
    Object.entries(checks).map(([name, subsystemChecks]) => {
      const passed = subsystemChecks.filter((c) => c.pass).length;
      const score = Math.round((passed / subsystemChecks.length) * 5);
      return [name, { score, passed, total: subsystemChecks.length, checks: subsystemChecks }];
    })
  );

  const total = Object.values(subsystems).reduce((sum, item) => sum + item.score, 0);
  const overall = Math.round((total / (SUBSYSTEMS.length * 5)) * 100);
  const bottleneck = Object.entries(subsystems).sort((a, b) => a[1].score - b[1].score)[0][0];
  return { overall, bottleneck, subsystems };
}

// -------- Parsing helpers --------

function parseSkillMd(text) {
  if (!text || !text.startsWith('---')) return { frontmatter: {}, body: text || '' };
  const end = text.indexOf('\n---', 3);
  if (end === -1) return { frontmatter: {}, body: text };
  const raw = text.slice(3, end).replace(/^\n/, '');
  const body = text.slice(end + 4).replace(/^\n/, '');
  const frontmatter = parseFrontmatter(raw);
  return { frontmatter, body };
}

function parseFrontmatter(text) {
  // Minimal YAML: scalar and folded (>-) string values only — sufficient for SKILL.md frontmatter.
  const out = {};
  const lines = text.split('\n');
  for (let i = 0; i < lines.length; i += 1) {
    const line = lines[i];
    const match = line.match(/^([A-Za-z0-9_-]+):\s*(.*)$/);
    if (!match) continue;
    const key = match[1];
    let value = match[2];
    if (value === '>-' || value === '>' || value === '|') {
      const folded = [];
      let j = i + 1;
      while (j < lines.length && (lines[j].startsWith('  ') || lines[j].trim() === '')) {
        folded.push(lines[j].replace(/^\s+/, ''));
        j += 1;
      }
      value = folded.join(' ').replace(/\s+/g, ' ').trim();
      i = j - 1;
    } else {
      value = value.replace(/^["']|["']$/g, '');
    }
    out[key] = value;
  }
  return out;
}

function hasTriggerPhrases(description) {
  const lower = description.toLowerCase();
  return ['use when', 'use this when', 'when the user', 'triggered by', 'use for'].some((p) =>
    lower.includes(p)
  );
}

function isThirdPerson(description) {
  // First-person markers that violate third-person voice.
  return (
    !/^\s*(i\b|i'm\b|i'll\b|my\b|we\b|our\b)/i.test(description) &&
    !/\byou should\b/i.test(description)
  );
}

function hasNegativeCase(description) {
  return /do\s+not\s+use|don['’]t\s+use|not\s+for[: ]/i.test(description);
}

function countNumberedUnder(text, sectionRegex, stopRegex) {
  if (!text) return 0;
  const lines = text.split('\n');
  let inSection = false;
  let count = 0;
  for (const line of lines) {
    const heading = line.match(/^#+\s+(.*)$/);
    if (heading) {
      if (inSection && stopRegex && stopRegex.test(heading[1])) break;
      if (sectionRegex.test(heading[1])) {
        // Only enter on the first matching header that is NOT also a stop header.
        if (stopRegex && stopRegex.test(heading[1])) continue;
        inSection = true;
        continue;
      }
      // A new top-level section (## or #) that doesn't match keeps us inside subsections.
      // We only stop when we hit the stop header or a sibling-level non-matching header.
      if (inSection && /^##\s+/.test(line) && !sectionRegex.test(heading[1])) {
        break;
      }
    }
    if (inSection && /^\s*\d+\.\s+/.test(line)) count += 1;
  }
  return count;
}

// -------- I/O helpers --------

export function parseArgs(argv) {
  const out = { _: [] };
  for (let i = 0; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith('--')) {
      out._.push(token);
      continue;
    }
    const [rawKey, inlineValue] = token.slice(2).split('=', 2);
    const key = rawKey.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
    if (inlineValue !== undefined) out[key] = inlineValue;
    else if (argv[i + 1] && !argv[i + 1].startsWith('--')) {
      out[key] = argv[i + 1];
      i += 1;
    } else out[key] = true;
  }
  return out;
}

export async function exists(filePath) {
  try {
    await access(filePath);
    return true;
  } catch {
    return false;
  }
}

async function readMaybe(filePath) {
  try {
    return await readFile(filePath, 'utf8');
  } catch {
    return null;
  }
}

async function listShallow(dir, regex) {
  try {
    const entries = await readdir(dir, { withFileTypes: true });
    return entries
      .filter((e) => e.isFile() && regex.test(e.name))
      .map((e) => path.join(dir, e.name));
  } catch {
    return [];
  }
}

export async function writeText(filePath, contents) {
  await mkdir(path.dirname(filePath), { recursive: true });
  await writeFile(filePath, contents, 'utf8');
}

// -------- Reporting --------

export function formatScoreReport(result, root = '.') {
  const lines = [
    `Skill validation for ${root}`,
    `Overall: ${result.overall}/100`,
    `Bottleneck: ${result.bottleneck}`,
    '',
  ];
  for (const [name, subsystem] of Object.entries(result.subsystems)) {
    lines.push(
      `${name}: ${subsystem.score}/5 (${subsystem.passed}/${subsystem.total} checks passed)`
    );
    for (const check of subsystem.checks) {
      lines.push(`  ${check.pass ? 'PASS' : 'FAIL'} ${check.message}`);
    }
    lines.push('');
  }
  return lines.join('\n');
}

export function htmlReport(result, title = 'Skill Assessment') {
  const rows = Object.entries(result.subsystems)
    .map(([name, subsystem]) => {
      const items = subsystem.checks
        .map(
          (c) =>
            `<li class="${c.pass ? 'pass' : 'fail'}">${c.pass ? 'PASS' : 'FAIL'} ${escapeHtml(c.message)}</li>`
        )
        .join('');
      return `<section>
      <h2>${escapeHtml(name)} <span>${subsystem.score}/5</span></h2>
      <ul>${items}</ul>
    </section>`;
    })
    .join('\n');

  return `<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>${escapeHtml(title)}</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; color: #172026; background: #f7f8fa; }
    main { max-width: 960px; margin: 0 auto; }
    header { margin-bottom: 24px; }
    h1 { margin: 0 0 8px; font-size: 32px; }
    .summary { display: flex; gap: 16px; flex-wrap: wrap; margin: 20px 0; }
    .metric { background: white; border: 1px solid #d9dee5; border-radius: 8px; padding: 16px 18px; min-width: 180px; }
    .metric strong { display: block; font-size: 28px; margin-top: 4px; }
    section { background: white; border: 1px solid #d9dee5; border-radius: 8px; margin: 14px 0; padding: 16px 18px; }
    h2 { margin: 0 0 10px; font-size: 20px; display: flex; justify-content: space-between; }
    ul { margin: 0; padding-left: 20px; }
    li { margin: 6px 0; }
    .pass { color: #126c43; }
    .fail { color: #a23020; }
  </style>
</head>
<body>
  <main>
    <header>
      <h1>${escapeHtml(title)}</h1>
      <p>Five-subsystem skill validation report.</p>
      <div class="summary">
        <div class="metric">Overall<strong>${result.overall}/100</strong></div>
        <div class="metric">Bottleneck<strong>${escapeHtml(result.bottleneck)}</strong></div>
      </div>
    </header>
    ${rows}
  </main>
</body>
</html>
`;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll('&', '&amp;')
    .replaceAll('<', '&lt;')
    .replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;')
    .replaceAll("'", '&#39;');
}
