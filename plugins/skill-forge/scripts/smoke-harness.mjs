#!/usr/bin/env node
// Smoke test for create-harness.mjs. Runs the scaffolder end-to-end against a
// fixture for each major stack and asserts the generated init.sh carries the
// right verification commands. Guards against the class of bug where a ported
// script fails at runtime (e.g. a wrong template path) while the structural
// validators — which never execute it — still report green.
//
// Pure Node built-ins. No test framework, no install. Exits non-zero on failure.
import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const script = path.join(here, 'create-harness.mjs');
const REQUIRED = ['AGENTS.md', 'feature_list.json', 'progress.md', 'session-handoff.md', 'init.sh'];

let failures = 0;
function check(label, condition) {
  console.log(`  ${condition ? 'ok  ' : 'FAIL'} ${label}`);
  if (!condition) failures += 1;
}

const cases = [
  {
    name: 'php-laravel (composer.json wins over a Vite package.json)',
    files: {
      'composer.json': JSON.stringify({
        require: { 'laravel/framework': '^11.0' },
        'require-dev': { 'laravel/pint': '^1.0' },
      }),
      artisan: '',
      'package.json': JSON.stringify({ dependencies: { vite: '^5.0' } }),
    },
    assert: ({ stdout, init }) => {
      check('detects php-laravel, not node', stdout.includes('php-laravel'));
      check('init.sh runs composer install', init.includes('composer install'));
      check('init.sh runs php artisan test', init.includes('php artisan test'));
      check('init.sh has no npm/pytest commands', !/\bnpm\b|pytest/.test(init));
    },
  },
  {
    name: 'python-django + uv',
    files: {
      'pyproject.toml':
        '[project]\nname = "x"\ndependencies = ["django", "fastapi", "ruff", "ty"]\n[tool.uv]\n',
      'uv.lock': '',
      'manage.py': '',
    },
    assert: ({ stdout, init }) => {
      check('detects python-django', stdout.includes('python-django'));
      check('init.sh uses uv sync', init.includes('uv sync'));
      check(
        'init.sh uses uv run python manage.py test',
        init.includes('uv run python manage.py test')
      );
      check('init.sh avoids bare python -m pytest / npm', !/python -m pytest|\bnpm\b/.test(init));
    },
  },
  {
    name: 'node (typescript-react)',
    files: {
      'package.json': JSON.stringify({
        dependencies: { react: '^18' },
        scripts: { typecheck: 'tsc', test: 'vitest' },
      }),
    },
    assert: ({ stdout, init }) => {
      check('detects typescript-react', stdout.includes('typescript-react'));
      check('init.sh runs npm test', init.includes('npm test'));
      check('init.sh has no php/pytest commands', !/composer|artisan|pytest/.test(init));
    },
  },
  {
    name: 'generic (no manifest)',
    files: { 'README.md': '# nothing' },
    assert: ({ stdout, init }) => {
      check('detects generic', stdout.includes('Detected stack: generic'));
      check(
        'init.sh has the no-manifest placeholder',
        init.includes('No package manifest detected')
      );
    },
  },
];

console.log('create-harness smoke test\n');
for (const testCase of cases) {
  console.log(testCase.name);
  const dir = mkdtempSync(path.join(tmpdir(), 'fh-smoke-'));
  try {
    for (const [name, contents] of Object.entries(testCase.files)) {
      const full = path.join(dir, name);
      mkdirSync(path.dirname(full), { recursive: true });
      writeFileSync(full, contents);
    }

    let stdout = '';
    try {
      stdout = execFileSync('node', [script, '--target', dir], { encoding: 'utf8' });
    } catch (error) {
      check(`create-harness exits 0 (${error.message.split('\n')[0]})`, false);
      continue;
    }

    for (const file of REQUIRED) check(`writes ${file}`, existsSync(path.join(dir, file)));
    const initPath = path.join(dir, 'init.sh');
    const init = existsSync(initPath) ? readFileSync(initPath, 'utf8') : '';
    testCase.assert({ stdout, init });
  } finally {
    rmSync(dir, { recursive: true, force: true });
  }
  console.log('');
}

if (failures > 0) {
  console.error(`smoke test FAILED — ${failures} assertion(s) failed`);
  process.exit(1);
}
console.log('smoke test PASSED');
