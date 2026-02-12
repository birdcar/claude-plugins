import { readdir, readFile, writeFile, mkdir } from 'fs/promises';
import { join, resolve } from 'path';
import { createInterface } from 'readline';

const ROOT = resolve(import.meta.dirname, '..');
const PLUGINS_DIR = join(ROOT, 'plugins');

interface LocalConfig {
  pluginName: string;
  filePath: string;
  prompts: ConfigPrompt[];
}

interface ConfigPrompt {
  key: string;
  question: string;
  validate?: (value: string) => string | null;
}

/**
 * Registry of plugins that require local configuration.
 * Add new entries here when a plugin needs per-machine settings.
 */
const CONFIG_REGISTRY: LocalConfig[] = [
  {
    pluginName: 'customer-voice',
    filePath: 'config.local.md',
    prompts: [
      {
        key: 'workos_monorepo_path',
        question: 'Path to your local WorkOS monorepo checkout',
        validate: (value) => {
          if (!value.startsWith('/') && !value.startsWith('~')) {
            return 'Path must be absolute (start with / or ~)';
          }
          return null;
        },
      },
    ],
  },
];

function createReadline() {
  return createInterface({
    input: process.stdin,
    output: process.stdout,
  });
}

function ask(rl: ReturnType<typeof createReadline>, question: string): Promise<string> {
  return new Promise((resolve) => {
    rl.question(question, (answer) => resolve(answer.trim()));
  });
}

async function pluginExists(name: string): Promise<boolean> {
  try {
    await readFile(join(PLUGINS_DIR, name, 'plugin.json'), 'utf-8');
    return true;
  } catch {
    return false;
  }
}

async function readExistingConfig(filePath: string): Promise<Record<string, string>> {
  try {
    const content = await readFile(filePath, 'utf-8');
    const frontmatterMatch = content.match(/^---\n([\s\S]*?)\n---/);
    if (!frontmatterMatch) return {};

    const pairs: Record<string, string> = {};
    for (const line of frontmatterMatch[1].split('\n')) {
      const [key, ...rest] = line.split(':');
      if (key && rest.length > 0) {
        pairs[key.trim()] = rest.join(':').trim();
      }
    }
    return pairs;
  } catch {
    return {};
  }
}

function generateConfigContent(values: Record<string, string>): string {
  const lines = Object.entries(values).map(([k, v]) => `${k}: ${v}`);
  return `---\n${lines.join('\n')}\n---\n`;
}

async function bootstrapPlugin(
  config: LocalConfig,
  rl: ReturnType<typeof createReadline>
): Promise<void> {
  const exists = await pluginExists(config.pluginName);
  if (!exists) {
    console.log(`  Skipping ${config.pluginName} (not found)`);
    return;
  }

  const configPath = join(PLUGINS_DIR, config.pluginName, config.filePath);
  const existing = await readExistingConfig(configPath);

  console.log(`\n  Configuring ${config.pluginName}...`);

  const values: Record<string, string> = {};
  for (const prompt of config.prompts) {
    const currentValue = existing[prompt.key];
    const defaultHint = currentValue ? ` [${currentValue}]` : '';

    let value = '';
    let valid = false;
    while (!valid) {
      value = await ask(rl, `    ${prompt.question}${defaultHint}: `);

      if (!value && currentValue) {
        value = currentValue;
      }

      if (!value) {
        console.log('    Value is required.');
        continue;
      }

      if (prompt.validate) {
        const error = prompt.validate(value);
        if (error) {
          console.log(`    ${error}`);
          continue;
        }
      }

      valid = true;
    }

    values[prompt.key] = value;
  }

  await writeFile(configPath, generateConfigContent(values));
  console.log(`  Wrote ${configPath}`);
}

async function main() {
  console.log('Bootstrapping local plugin configuration...\n');
  console.log(`  Plugin directory: ${PLUGINS_DIR}`);

  const rl = createReadline();

  try {
    for (const config of CONFIG_REGISTRY) {
      await bootstrapPlugin(config, rl);
    }
  } finally {
    rl.close();
  }

  console.log("\nDone. Local config files are gitignored and won't be committed.");
}

main().catch(console.error);
