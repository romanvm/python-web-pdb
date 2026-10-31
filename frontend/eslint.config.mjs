import js from "@eslint/js";
import stylistic from "@stylistic/eslint-plugin";
import globals from "globals";

export default [
  {
    ignores: ["eslint.config.mjs", "webpack.config.js"]
  },
  js.configs.recommended,
  {
    languageOptions: {
      ecmaVersion: "latest",
      sourceType: "module",
      globals: globals.browser
    },
    plugins: {
      "@stylistic": stylistic
    },
    rules: {
      "accessor-pairs": "error",
      "array-callback-return": "error",
      "arrow-body-style": "error",
      "block-scoped-var": "error",
      "camelcase": "off",
      "capitalized-comments": [
        "error",
        "always"
      ],
      "class-methods-use-this": "error",
      "complexity": "error",
      "consistent-return": "off",
      "consistent-this": "error",
      "curly": "error",
      "default-case": "error",
      "dot-notation": "error",
      "eqeqeq": "off",
      "for-direction": "error",
      "func-name-matching": "error",
      "func-names": "error",
      "func-style": [
        "error",
        "declaration"
      ],
      "guard-for-in": "error",
      "id-denylist": "error",
      "id-length": "off",
      "id-match": "error",
      "init-declarations": "error",
      "max-depth": "error",
      "max-lines": "error",
      "max-nested-callbacks": "error",
      "max-params": "error",
      "max-statements": "off",
      "new-cap": "error",
      "no-alert": "error",
      "no-array-constructor": "error",
      "no-await-in-loop": "error",
      "no-bitwise": "error",
      "no-caller": "error",
      "no-continue": "error",
      "no-div-regex": "error",
      "no-duplicate-imports": "error",
      "no-else-return": "error",
      "no-empty-function": "error",
      "no-eq-null": "error",
      "no-eval": "error",
      "no-extend-native": "error",
      "no-extra-bind": "error",
      "no-extra-label": "error",
      "no-implicit-coercion": "error",
      "no-implicit-globals": "error",
      "no-implied-eval": "error",
      "no-inline-comments": "error",
      "no-invalid-this": "error",
      "no-iterator": "error",
      "no-label-var": "error",
      "no-labels": "error",
      "no-lone-blocks": "error",
      "no-lonely-if": "error",
      "no-loop-func": "error",
      "no-magic-numbers": "off",
      "no-multi-assign": "error",
      "no-multi-str": "error",
      "no-negated-condition": "error",
      "no-nested-ternary": "error",
      "no-new": "error",
      "no-new-func": "error",
      "no-new-wrappers": "error",
      "no-object-constructor": "error",
      "no-octal-escape": "error",
      "no-param-reassign": "error",
      "no-plusplus": "off",
      "no-proto": "error",
      "no-prototype-builtins": "error",
      "no-restricted-globals": "error",
      "no-restricted-imports": "error",
      "no-restricted-properties": "error",
      "no-restricted-syntax": "error",
      "no-return-assign": "error",
      "no-script-url": "error",
      "no-self-compare": "error",
      "no-sequences": "error",
      "no-shadow": "error",
      "no-shadow-restricted-names": "error",
      "no-template-curly-in-string": "error",
      "no-ternary": "error",
      "no-throw-literal": "error",
      "no-undef-init": "error",
      "no-undefined": "error",
      "no-underscore-dangle": "error",
      "no-unmodified-loop-condition": "error",
      "no-unneeded-ternary": "error",
      "no-unused-expressions": "error",
      "no-use-before-define": "error",
      "no-useless-call": "error",
      "no-useless-computed-key": "error",
      "no-useless-concat": "error",
      "no-useless-constructor": "error",
      "no-useless-rename": "error",
      "no-useless-return": "error",
      "no-var": "off",
      "no-void": "error",
      "no-warning-comments": "error",
      "no-with": "error",
      "object-shorthand": "error",
      "one-var": "error",
      "operator-assignment": "error",
      "prefer-arrow-callback": "error",
      "prefer-const": "off",
      "prefer-numeric-literals": "error",
      "prefer-promise-reject-errors": "error",
      "prefer-rest-params": "error",
      "prefer-spread": "error",
      "prefer-template": "off",
      "radix": "error",
      "require-await": "error",
      "sort-imports": "off",
      "sort-keys": "off",
      "sort-vars": "error",
      "strict": "error",
      "symbol-description": "error",
      "unicode-bom": [
        "error",
        "never"
      ],
      "vars-on-top": "error",
      "yoda": [
        "error",
        "never"
      ],
      "@stylistic/array-bracket-newline": "error",
      "@stylistic/array-bracket-spacing": "error",
      "@stylistic/array-element-newline": "error",
      "@stylistic/arrow-parens": [
        "error",
        "always"
      ],
      "@stylistic/arrow-spacing": [
        "error",
        {
          "after": true,
          "before": true
        }
      ],
      "@stylistic/block-spacing": [
        "error",
        "always"
      ],
      "@stylistic/brace-style": "off",
      "@stylistic/comma-dangle": "off",
      "@stylistic/comma-spacing": [
        "error",
        {
          "after": true,
          "before": false
        }
      ],
      "@stylistic/comma-style": [
        "error",
        "last"
      ],
      "@stylistic/computed-property-spacing": [
        "error",
        "never"
      ],
      "@stylistic/dot-location": [
        "error",
        "property"
      ],
      "@stylistic/eol-last": "error",
      "@stylistic/function-call-spacing": "error",
      "@stylistic/generator-star-spacing": "error",
      "@stylistic/indent": "off",
      "@stylistic/jsx-quotes": "error",
      "@stylistic/key-spacing": "error",
      "@stylistic/keyword-spacing": [
        "error",
        {
          "after": true,
          "before": true
        }
      ],
      "@stylistic/line-comment-position": "error",
      "@stylistic/linebreak-style": [
        "off",
        "unix"
      ],
      "@stylistic/lines-around-comment": "error",
      "@stylistic/max-len": "off",
      "@stylistic/max-statements-per-line": "off",
      "@stylistic/multiline-ternary": "error",
      "@stylistic/new-parens": "error",
      "@stylistic/newline-per-chained-call": "error",
      "@stylistic/no-confusing-arrow": "error",
      "@stylistic/no-extra-parens": "error",
      "@stylistic/no-floating-decimal": "error",
      "@stylistic/no-mixed-operators": "off",
      "@stylistic/no-multi-spaces": "error",
      "@stylistic/no-multiple-empty-lines": "error",
      "@stylistic/no-tabs": "error",
      "@stylistic/no-trailing-spaces": "error",
      "@stylistic/no-whitespace-before-property": "error",
      "@stylistic/nonblock-statement-body-position": "error",
      "@stylistic/object-curly-newline": "off",
      "@stylistic/object-curly-spacing": [
        "error",
        "always"
      ],
      "@stylistic/object-property-newline": "error",
      "@stylistic/one-var-declaration-per-line": "error",
      "@stylistic/operator-linebreak": "error",
      "@stylistic/padded-blocks": "off",
      "@stylistic/padding-line-between-statements": "error",
      "@stylistic/quote-props": "off",
      "@stylistic/quotes": [
        "error",
        "single"
      ],
      "@stylistic/rest-spread-spacing": "error",
      "@stylistic/semi": "off",
      "@stylistic/semi-spacing": "error",
      "@stylistic/semi-style": [
        "error",
        "last"
      ],
      "@stylistic/space-before-blocks": "error",
      "@stylistic/space-before-function-paren": "off",
      "@stylistic/space-in-parens": [
        "error",
        "never"
      ],
      "@stylistic/space-infix-ops": "error",
      "@stylistic/space-unary-ops": "error",
      "@stylistic/spaced-comment": [
        "error",
        "always"
      ],
      "@stylistic/switch-colon-spacing": "error",
      "@stylistic/template-curly-spacing": [
        "error",
        "never"
      ],
      "@stylistic/template-tag-spacing": "error",
      "@stylistic/wrap-iife": "error",
      "@stylistic/wrap-regex": "error",
      "@stylistic/yield-star-spacing": "error"
    }
  }
];
