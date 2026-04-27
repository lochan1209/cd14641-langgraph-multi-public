
# External Data

This folder contains **external customer‑provided data** used to populate and test the Agentic AI system.

The primary customer in this project is **CultPass**, the first adopter of Uda‑Hub.

---

## Included Files

### `cultpass_articles.jsonl`
- Knowledge base articles for CultPass
- Expanded to **14+ records** as required
- Covers topics such as:
  - Reservations
  - Subscriptions
  - Policies
  - App usage
  - Event attendance

### `cultpass_experiences.jsonl`
- Sample cultural experiences
- Used to simulate booking and participation logic

### `cultpass_users.jsonl`
- Sample user profiles
- Used to generate subscriptions and reservations

---

## Data Usage
This data is ingested by:
01_external_db_setup.ipynb

Which:
- Creates the external database
- Populates experience, subscription, and reservation tables
- Simulates realistic user activity

---

## Version Control Policy
- JSONL files are tracked
- Generated databases (`*.db`) are excluded via `.gitignore`