# tsconfig.json Template

Generate `tsconfig.json` for a GitHub Action package.

## Template (Extending Root)

When the monorepo has a root tsconfig.json:

```json
{
  "extends": "../../tsconfig.json",
  "compilerOptions": {
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Template (Standalone)

When no root tsconfig exists or extending isn't appropriate:

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "NodeNext",
    "moduleResolution": "NodeNext",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "outDir": "dist",
    "rootDir": "src",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": false
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## Determining Which to Use

1. Check if root `tsconfig.json` exists
2. Check if other actions in the monorepo extend it
3. If yes to both, use extending template
4. If no root config or other packages don't extend, use standalone

## Adjusting Extends Path

The `extends` path depends on action location:

| Action Location            | Extends Path             |
| -------------------------- | ------------------------ |
| `packages/action-name/`    | `../../tsconfig.json`    |
| `actions/action-name/`     | `../../tsconfig.json`    |
| `src/actions/action-name/` | `../../../tsconfig.json` |

## Notes

- `declaration: true` generates `.d.ts` files (useful for testing)
- Target ES2022 for modern Node.js features
- NodeNext module resolution works best with Bun
- Always exclude `node_modules` and `dist`
