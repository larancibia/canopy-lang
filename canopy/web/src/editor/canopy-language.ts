// Monaco Editor language definition for Canopy

import type { languages } from 'monaco-editor';

export const canopyLanguageConfig: languages.LanguageConfiguration = {
  comments: {
    lineComment: '//',
    blockComment: ['/*', '*/'],
  },
  brackets: [
    ['{', '}'],
    ['[', ']'],
    ['(', ')'],
  ],
  autoClosingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" },
  ],
  surroundingPairs: [
    { open: '{', close: '}' },
    { open: '[', close: ']' },
    { open: '(', close: ')' },
    { open: '"', close: '"' },
    { open: "'", close: "'" },
  ],
};

export const canopyTokensProvider: languages.IMonarchLanguage = {
  defaultToken: '',
  tokenPostfix: '.canopy',

  keywords: [
    'strategy',
    'buy',
    'sell',
    'when',
    'plot',
    'and',
    'or',
    'not',
    'true',
    'false',
  ],

  indicators: [
    'sma',
    'ema',
    'rsi',
    'macd',
    'bbands',
    'atr',
    'stoch',
    'adx',
    'cci',
    'mfi',
    'obv',
    'vwap',
    'psar',
  ],

  functions: [
    'crossover',
    'crossunder',
    'highest',
    'lowest',
    'abs',
    'max',
    'min',
    'round',
    'floor',
    'ceil',
  ],

  operators: [
    '=',
    '>',
    '<',
    '!',
    '~',
    '?',
    ':',
    '==',
    '<=',
    '>=',
    '!=',
    '&&',
    '||',
    '++',
    '--',
    '+',
    '-',
    '*',
    '/',
    '&',
    '|',
    '^',
    '%',
    '<<',
    '>>',
    '>>>',
    '+=',
    '-=',
    '*=',
    '/=',
    '&=',
    '|=',
    '^=',
    '%=',
    '<<=',
    '>>=',
    '>>>=',
  ],

  // Symbols
  symbols: /[=><!~?:&|+\-*\/\^%]+/,

  // Escapes
  escapes: /\\(?:[abfnrtv\\"']|x[0-9A-Fa-f]{1,4}|u[0-9A-Fa-f]{4}|U[0-9A-Fa-f]{8})/,

  // Tokenizer rules
  tokenizer: {
    root: [
      // Identifiers and keywords
      [
        /[a-z_$][\w$]*/,
        {
          cases: {
            '@keywords': 'keyword',
            '@indicators': 'type.identifier',
            '@functions': 'predefined',
            '@default': 'identifier',
          },
        },
      ],
      [/[A-Z][\w\$]*/, 'type.identifier'], // Constants

      // Whitespace
      { include: '@whitespace' },

      // Delimiters and operators
      [/[{}()\[\]]/, '@brackets'],
      [/[<>](?!@symbols)/, '@brackets'],
      [
        /@symbols/,
        {
          cases: {
            '@operators': 'operator',
            '@default': '',
          },
        },
      ],

      // Numbers
      [/\d*\.\d+([eE][\-+]?\d+)?/, 'number.float'],
      [/0[xX][0-9a-fA-F]+/, 'number.hex'],
      [/\d+/, 'number'],

      // Delimiter: after number because of .\d floats
      [/[;,.]/, 'delimiter'],

      // Strings
      [/"([^"\\]|\\.)*$/, 'string.invalid'], // non-terminated string
      [/'([^'\\]|\\.)*$/, 'string.invalid'], // non-terminated string
      [/"/, 'string', '@string_double'],
      [/'/, 'string', '@string_single'],
    ],

    whitespace: [
      [/[ \t\r\n]+/, ''],
      [/\/\*/, 'comment', '@comment'],
      [/\/\/.*$/, 'comment'],
    ],

    comment: [
      [/[^\/*]+/, 'comment'],
      [/\*\//, 'comment', '@pop'],
      [/[\/*]/, 'comment'],
    ],

    string_double: [
      [/[^\\"]+/, 'string'],
      [/@escapes/, 'string.escape'],
      [/\\./, 'string.escape.invalid'],
      [/"/, 'string', '@pop'],
    ],

    string_single: [
      [/[^\\']+/, 'string'],
      [/@escapes/, 'string.escape'],
      [/\\./, 'string.escape.invalid'],
      [/'/, 'string', '@pop'],
    ],
  },
};

// Theme configuration is already handled by canopyLanguageConfig above
// This export is kept for future reference but not currently used
export const canopyThemeConfig = {
  tokenPostfix: '.canopy',
  ignoreCase: false,
  brackets: [
    { open: '{', close: '}', token: 'delimiter.curly' },
    { open: '[', close: ']', token: 'delimiter.bracket' },
    { open: '(', close: ')', token: 'delimiter.parenthesis' },
  ],
};

// Completion items for autocomplete
export const canopyCompletionItems = [
  // Keywords
  { label: 'strategy', kind: 14, insertText: 'strategy "${1:name}"', documentation: 'Define a new trading strategy' },
  { label: 'buy', kind: 14, insertText: 'buy when ${1:condition}', documentation: 'Buy signal condition' },
  { label: 'sell', kind: 14, insertText: 'sell when ${1:condition}', documentation: 'Sell signal condition' },
  { label: 'plot', kind: 14, insertText: 'plot ${1:variable}', documentation: 'Plot a variable on the chart' },
  { label: 'when', kind: 14, insertText: 'when ${1:condition}', documentation: 'Condition clause' },

  // Indicators
  { label: 'sma', kind: 3, insertText: 'sma(close, ${1:20})', documentation: 'Simple Moving Average' },
  { label: 'ema', kind: 3, insertText: 'ema(close, ${1:20})', documentation: 'Exponential Moving Average' },
  { label: 'rsi', kind: 3, insertText: 'rsi(close, ${1:14})', documentation: 'Relative Strength Index' },
  { label: 'macd', kind: 3, insertText: 'macd(close, ${1:12}, ${2:26}, ${3:9})', documentation: 'MACD Indicator' },
  { label: 'bbands', kind: 3, insertText: 'bbands(close, ${1:20}, ${2:2})', documentation: 'Bollinger Bands' },
  { label: 'atr', kind: 3, insertText: 'atr(${1:14})', documentation: 'Average True Range' },
  { label: 'stoch', kind: 3, insertText: 'stoch(${1:14}, ${2:3}, ${3:3})', documentation: 'Stochastic Oscillator' },
  { label: 'adx', kind: 3, insertText: 'adx(${1:14})', documentation: 'Average Directional Index' },

  // Functions
  { label: 'crossover', kind: 3, insertText: 'crossover(${1:series1}, ${2:series2})', documentation: 'Detect crossover' },
  { label: 'crossunder', kind: 3, insertText: 'crossunder(${1:series1}, ${2:series2})', documentation: 'Detect crossunder' },
  { label: 'highest', kind: 3, insertText: 'highest(${1:series}, ${2:period})', documentation: 'Highest value over period' },
  { label: 'lowest', kind: 3, insertText: 'lowest(${1:series}, ${2:period})', documentation: 'Lowest value over period' },

  // Built-in variables
  { label: 'close', kind: 4, insertText: 'close', documentation: 'Closing price' },
  { label: 'open', kind: 4, insertText: 'open', documentation: 'Opening price' },
  { label: 'high', kind: 4, insertText: 'high', documentation: 'High price' },
  { label: 'low', kind: 4, insertText: 'low', documentation: 'Low price' },
  { label: 'volume', kind: 4, insertText: 'volume', documentation: 'Trading volume' },
];
