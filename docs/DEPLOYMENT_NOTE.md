# Deployment & database note

A short, honest note on which database runs where, and why — so the project, the
report, and the live demo all line up.

## The database design is MySQL 8.0

As specified in the project report (Chapter 3), the system's database is a
**MySQL 8.0** relational database. The development/primary system runs on real
**MySQL 8.0** on the team's machine, and the schema, queries and ORM models are all
written for it. This is the database to inspect during the demonstration (via the
**SQLTools** connection in VS Code).

## The free public demo runs on SQLite — and why

The live site (**https://aizen004.pythonanywhere.com**) is hosted on
**PythonAnywhere's free tier**, which:

- **does not provide MySQL** on free accounts (it is a paid feature), and
- **blocks outbound connections** to an external MySQL server.

So for the cost‑free public deployment we use **SQLite**, a self‑contained
file‑based database that needs no separate server and works on the free tier.

**Crucially, this required no change to the application code.** The app accesses the
database through the **SQLAlchemy ORM**, so the database is selected by a single
configuration value (`DATABASE_URL` in `.env` / the WSGI file):

```
# Local development (and the report's design):
DATABASE_URL=mysql+pymysql://root:password@127.0.0.1:3306/ransbet_iims

# Free public deployment:
DATABASE_URL=    (blank -> falls back to a local SQLite file)
```

The same code, models, queries and features run on both — only this one line differs.

## Summary

| Environment | Database | Reason |
|-------------|----------|--------|
| Development / report design | **MySQL 8.0** | Matches the report; the "real" system database |
| Free public demo (PythonAnywhere) | **SQLite** | Free tier has no MySQL; SQLite needs no server; identical code via the ORM |

## Matching the report's MySQL in the cloud (optional, future work)

To run MySQL online as well (as the report's AWS RDS design intended), the options are:

- A small **paid** plan (PythonAnywhere paid, or AWS RDS as originally designed), or
- A **free cloud MySQL** (e.g. TiDB Cloud) paired with a host that allows outbound
  database connections (e.g. Render).

For an academic prototype, MySQL in development plus a free SQLite public demo is a
deliberate, defensible choice that demonstrates correct use of database abstraction.

> **One‑line version for the report:** *"MySQL 8.0 is the system database, as
> specified. For the cost‑free public deployment, SQLite is substituted for a paid
> cloud MySQL instance; because the application uses the SQLAlchemy ORM, this requires
> only a configuration change and no code change."*
