import type { Meta, StoryObj } from '@storybook/react';
import Map from './Map';

const meta = {
  id: 'components-map-story',
  title: 'Components/Map',
  component: Map,
  parameters: {
    layout: 'fullscreen',
  },
  tags: ['autodocs'],
} satisfies Meta<typeof Map>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
