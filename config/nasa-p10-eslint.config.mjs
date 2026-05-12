// NASA Power of 10 Rules — ESLint Configuration
// Non-negotiable code stability rules for agent output

export default [
  {
    rules: {
      // Rule 1: No complex flow constructs
      "no-labels": "error",
      "no-continue": "error",

      // Rule 4: Functions stay under 60 lines
      "max-lines-per-function": ["error", {
        max: 60,
        skipBlankLines: true,
        skipComments: true,
      }],

      // Cyclomatic complexity cap
      "complexity": ["error", 10],

      // Max nesting depth
      "max-depth": ["error", 4],

      // Rule 6: Restrict data scope
      "no-var": "error",
      "prefer-const": "error",
      "block-scoped-var": "error",

      // Rule 8: No eval or dynamic code execution
      "no-eval": "error",
      "no-implied-eval": "error",
      "no-new-func": "error",

      // Rule 9: No dangerous mutations
      "no-param-reassign": "error",

      // TypeScript-specific (requires typescript-eslint)
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-misused-promises": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unused-vars": "error",
      "@typescript-eslint/strict-boolean-expressions": "error",
    },
  },
];
