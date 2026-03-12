# Analytics Workspace

This folder is for local data work that feeds portfolio stories.

## Folder layout
- `data/raw/` source exports (do not publish)
- `data/processed/` cleaned/joined data (still private)
- `scripts/` Python merge and analysis scripts
- `outputs/` charts/tables used to build story metrics
- `stories/` markdown drafts for portfolio writeups

## Workflow
1. Put source files in `data/raw/`.
2. Run merge/clean scripts from `scripts/`.
3. Save aggregates in `outputs/` (no customer-level IDs).
4. Write story bullets in `stories/`.
5. Add only safe summary numbers/visuals to `index.html`.

## Privacy rule
Never publish raw customer data, emails, shipto IDs, or account-level rows.
Only publish aggregated metrics and anonymized insights.
