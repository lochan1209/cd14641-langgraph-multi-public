
# Core Data

This folder contains **core Uda‑Hub application data** used by the Agentic AI system.

The data is stored in a SQLite database that is **created dynamically** using setup notebooks.

---

## Contents

- `udahub.db` (generated locally, not committed)
- SQLAlchemy models representing:
  - Accounts
  - Articles
  - Application‑level entities

---

## Database Creation
The database is created by running:
02_core_db_setup.ipynb

This notebook:
- Resets the existing database
- Creates tables
- Loads article records
- Ensures a minimum number of articles are present

---

## Important Notes
- `.db` files are NOT committed to version control
- Databases are regenerated as needed
- Only setup scripts and input JSONL files are tracked

---

## Purpose
This database serves as the **core knowledge source** for answering questions related to the Uda‑Hub platform.