import { readdir, readFile, writeFile } from 'fs/promises';
import { join } from 'path';

interface PluginEntry {
  name: string;
  source: string;
  description: string;
  version: string;
}

interface MarketplaceMeta {
  name: string;
  owner: {
    name: string;
  };
  version: string;
  description: string;
  plugins: PluginEntry[];
}

async function discoverPlugins(pluginsDir: string): Promise<PluginEntry[]> {
  const plugins: PluginEntry[] = [];
  const entries = await readdir(pluginsDir, { withFileTypes: true });

  for (const entry of entries) {
    if (!entry.isDirectory()) continue;

    const pluginPath = join(pluginsDir, entry.name);
    const pluginJsonPath = join(pluginPath, 'plugin.json');

    try {
      const content = await readFile(pluginJsonPath, 'utf-8');
      const pluginJson = JSON.parse(content);

      plugins.push({
        name: pluginJson.name || entry.name,
        source: `./${pluginsDir}/${entry.name}`,
        description: pluginJson.description || '',
        version: pluginJson.version || '0.1.0',
      });

      console.log(`✓ Discovered: ${entry.name}`);
    } catch (error) {
      console.warn(`⚠ Skipped ${entry.name}: invalid or missing plugin.json`);
    }
  }

  // Sort alphabetically for deterministic output across platforms
  return plugins.sort((a, b) => a.name.localeCompare(b.name));
}

async function updateMarketplace(plugins: PluginEntry[]): Promise<void> {
  const marketplacePath = '.claude-plugin/marketplace.json';

  let marketplace: MarketplaceMeta;
  try {
    const content = await readFile(marketplacePath, 'utf-8');
    marketplace = JSON.parse(content);
  } catch {
    marketplace = {
      name: 'birdcar-plugins',
      owner: {
        name: 'birdcar',
      },
      version: '0.1.0',
      description: 'Personal Claude Code plugin marketplace',
      plugins: [],
    };
  }

  marketplace.plugins = plugins;
  await writeFile(marketplacePath, JSON.stringify(marketplace, null, 2) + '\n');
  console.log(`\n✓ Updated marketplace with ${plugins.length} plugins`);
}

async function main() {
  console.log('Syncing plugins...\n');
  const plugins = await discoverPlugins('plugins');
  await updateMarketplace(plugins);
}

main().catch(console.error);
