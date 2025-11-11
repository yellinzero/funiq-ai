import path from 'node:path'
import { fileURLToPath } from 'node:url'
import antfu from '@antfu/eslint-config'
import { FlatCompat } from '@eslint/eslintrc'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const compat = new FlatCompat({
  baseDirectory: __dirname,
})

export default antfu({
  ignores: ['**/node_modules/*', '**/.next/*', '**/.vscode/*', '**/output/*', '**/dist/*', '**/out/*'],
  react: {
    overrides: {
      'react-refresh/only-export-components': 'off',
      'react/no-array-index-key': 'off',
    },
  },
  stylistic: true,
  typescript: {
    overrides: {
      'ts/no-unused-vars': ['warn', {
        argsIgnorePattern: '^_',
        varsIgnorePattern: '^_',
        caughtErrorsIgnorePattern: '^_',
        ignoreRestSiblings: true,
      }],
      'ts/no-empty-object-type': ['warn', {
        allowInterfaces: 'always',
      }],
      'ts/consistent-type-imports': ['warn', {
        fixStyle: 'inline-type-imports',
      }],
      'ts/no-unused-expressions': ['error', {
      }],
    },
  },
  rules: {
    'no-array-index-key': 'off',
    'import/no-duplicates': ['warn', {
      'prefer-inline': true,
    }],
    'no-console': ['warn', {
      allow: ['info', 'error'],
    }],
    'unused-imports/no-unused-vars': 'off',
    'node/prefer-global/process': 'off',
  },
}).append(
  ...compat.extends('plugin:@next/next/recommended'),
  {
    rules: {
      '@next/next/no-img-element': 'off',
    },
  },
)
