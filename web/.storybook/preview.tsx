import type { Preview } from '@storybook/react';
import '../app/globals.css';
import { ApiClientProvider } from '../app/components/apiClientContext';

const preview: Preview = {
  decorators: [
    (Story) => (
      <ApiClientProvider>
        <Story />
      </ApiClientProvider>
    ),
  ],
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
  },
};

export default preview;
