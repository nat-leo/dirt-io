import type { StorybookConfig } from '@storybook/react-vite';
import { mergeConfig } from 'vite';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import tailwindcss from '@tailwindcss/postcss';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const config: StorybookConfig = {
  stories: [
    '../app/**/*.stories.@(js|jsx|mjs|ts|tsx)',
  ],
  addons: [
    '@storybook/addon-docs',
    '@storybook/addon-a11y',
  ],
  framework: {
    name: '@storybook/react-vite',
    options: {},
  },
  async viteFinal(config) {
    return mergeConfig(config, {
      resolve: {
        alias: {
          '@': path.resolve(__dirname, '..'),
        },
      },
      css: {
        postcss: {
          plugins: [tailwindcss()],
        },
      },
      define: {
        'process.env.GOOGLE_MAPS_API_KEY': JSON.stringify(
          process.env.GOOGLE_MAPS_API_KEY
        ),
        'process.env.NEXT_PUBLIC_MAPBOX_TOKEN': JSON.stringify(
          process.env.NEXT_PUBLIC_MAPBOX_TOKEN
        ),
      },
    });
  },
};

export default config;
