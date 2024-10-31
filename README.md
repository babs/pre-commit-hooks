pre-commit hooks
===

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->

- [Usage](#usage)
- [Hooks](#hooks)
  - [`check-argocd-app`](#check-argocd-app)
- [Dev notes](#dev-notes)
  - [Run specific hook by its id](#run-specific-hook-by-its-id)
  - [Live test component](#live-test-component)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Usage

```yaml
  - repo: https://github.com/babs/pre-commit-hooks
    rev: v0.0.1 # use the proper revision
    hooks:
    - id: check-argocd-app
    - id: ...
```

## Hooks

### `check-argocd-app`

Hook to validate some readability and maintainability rules for ArgoCD Application manifests.

For Application manifest, rules are:
* `spec.source` or `spec.sources` must be the last `spec` section
* if `spec.source` or any `spec.sources[*]` is of `helm` type, then `values` and `valuesObject` must be last(s) key(s)

This ensures that most relevant `spec` declarations are at the top of the file, preventing them from being obscured by large `values` or `valuesObject` sections.

## Dev notes

### Run specific hook by its id

```bash
pre-commit run check-argocd-app --all-files
```

### Live test component

```bash
pre-commit try-repo CHECKOUT_LOCATION check-argocd-app --files FILE.yaml
```
