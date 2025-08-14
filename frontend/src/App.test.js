import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from './App';

// Mock fetch globally
global.fetch = jest.fn();

// Mock TextDecoder for Node.js environment
global.TextDecoder = class TextDecoder {
  constructor() {}
  decode(value) {
    return value ? String.fromCharCode.apply(null, new Uint8Array(value)) : '';
  }
};

// Mock console.error to reduce noise in tests
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    const message = args[0];
    
    // Filter out expected warnings and errors during testing
    if (typeof message === 'string') {
      if (message.includes('Warning: ReactDOM.render is deprecated')) return;
      if (message.includes('Failed to fetch:')) return;
      if (message.includes('Network error')) return;
    }
    
    // Only log unexpected errors
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

describe('App Component', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('renders chat interface', () => {
    render(<App />);
    
    expect(screen.getByPlaceholderText('Ask me anything...')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /send/i })).toBeInTheDocument();
  });

  test('handles user input', async () => {
    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask me anything...');
    await userEvent.type(input, 'Hello, world!');
    
    expect(input.value).toBe('Hello, world!');
  });

  test('sends message and displays it', async () => {
    // Mock successful response
    const mockResponse = {
      body: {
        getReader: () => ({
          read: jest.fn().mockResolvedValue({ done: true })
        })
      }
    };
    fetch.mockResolvedValueOnce(mockResponse);
    
    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask me anything...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      await userEvent.type(input, 'Test message');
      await userEvent.click(sendButton);
    });
    
    expect(screen.getByText('Test message')).toBeInTheDocument();
    expect(input.value).toBe('');
  });

  test('prevents sending empty messages', async () => {
    render(<App />);
    
    const sendButton = screen.getByRole('button', { name: /send/i });
    await userEvent.click(sendButton);
    
    expect(fetch).not.toHaveBeenCalled();
  });

  test('handles API errors gracefully', async () => {
    fetch.mockRejectedValueOnce(new Error('Network error'));
    
    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask me anything...');
    const sendButton = screen.getByRole('button', { name: /send/i });
    
    await act(async () => {
      await userEvent.type(input, 'Test message');
      await userEvent.click(sendButton);
    });
    
    await waitFor(() => {
      expect(screen.getByText('Error: Could not connect to the server.')).toBeInTheDocument();
    });
  });

  test('submits form with Enter key', async () => {
    const mockResponse = {
      body: {
        getReader: () => ({
          read: jest.fn().mockResolvedValue({ done: true })
        })
      }
    };
    fetch.mockResolvedValueOnce(mockResponse);
    
    render(<App />);
    
    const input = screen.getByPlaceholderText('Ask me anything...');
    await act(async () => {
      await userEvent.type(input, 'Test message');
      await userEvent.keyboard('{Enter}');
    });
    
    expect(fetch).toHaveBeenCalled();
  });
});
