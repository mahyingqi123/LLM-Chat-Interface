// jest-dom adds custom jest matchers for asserting on DOM nodes.
import '@testing-library/jest-dom';

// Mock console.error to make tests cleaner
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      (args[0].includes('Warning:') || args[0].includes('Failed prop type'))
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Mock scrollIntoView which is not implemented in jsdom
Object.defineProperty(Element.prototype, 'scrollIntoView', {
  value: jest.fn(),
  writable: true,
});

// Mock fetch globally for tests that don't explicitly mock it
if (!global.fetch) {
  global.fetch = jest.fn(() =>
    Promise.resolve({
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(''),
      body: {
        getReader: () => ({
          read: () => Promise.resolve({ done: true })
        })
      }
    })
  );
}

// Reset fetch mock before each test
beforeEach(() => {
  if (global.fetch && global.fetch.mockClear) {
    global.fetch.mockClear();
  }
});

// Clean up after each test
afterEach(() => {
  // Clean up any timers
  jest.clearAllTimers();
  
  // Reset all mocks
  jest.resetAllMocks();
});