# Baselines

## Menu Navigation Baseline

- Fixed snapshot tag: `menu-nav-v1`
- Long-lived baseline branch: `feature/mixed-nav-base`

This baseline contains:

- mixed navigation mode based on top navigation + contextual left sidebar
- white sidebar background adjustments
- top navigation interaction updates
- hidden preview page `/main` for night super stock cards

## Recommended Usage

Create a new project branch from the reusable baseline:

```bash
git checkout feature/mixed-nav-base
git checkout -b project-xxx
```

Return to the exact milestone snapshot:

```bash
git checkout menu-nav-v1
```

## Notes

- `menu-nav-v1` is used to preserve the exact milestone state.
- `feature/mixed-nav-base` is used for continued iteration and reuse.
- Build artifacts such as `dist.zip` should not be committed.
