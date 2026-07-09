# Authentication & Passwords

How users sign in, how passwords are protected, and how access is controlled in IIMS.
Written in plain English, but with the exact mechanisms so any team member can defend it.

---

## The three accounts (roles)

IIMS uses **role-based access control (RBAC)** — three roles, defined in `app/models.py`
(`ROLE_OWNER`, `ROLE_MANAGER`, `ROLE_STAFF`):

| Role | Demo login | Can do |
|------|-----------|--------|
| **Business Owner** (`owner`) | owner@ransbet.com | Everything + analytics, reports, forecasts |
| **Store Manager** (`manager`) | manager@ransbet.com | Manage inventory, suppliers, pricing; approvals |
| **Inventory Staff** (`staff`) | staff@ransbet.com | Record stock movements & sales |

---

## How the accounts were created

The demo accounts are created by **`seed.py`** the first time the database is set up.
It calls `set_password(...)`, which **hashes** the password before saving — the plain
text is never stored:

```python
# seed.py
user = User(name="Business Owner", email="owner@ransbet.com", role=ROLE_OWNER)
user.set_password("owner123")   # stores a hash, not the text
```

---

## How passwords are stored (the important bit)

Passwords are **never** stored as plain text. `set_password()` runs them through
**Werkzeug's `generate_password_hash`**, which in this project uses the **scrypt**
algorithm. A stored value looks like:

```
scrypt:32768:8:1$<random-salt>$<hash>
```

- **scrypt** — a strong, memory-hard hashing algorithm (deliberately slow to brute-force).
- **32768:8:1** — its cost settings (CPU/memory cost, block size, parallelism).
- **random salt** — a unique value per user, so two people with the *same* password
  still get *different* stored hashes.
- It is **one-way** — the hash cannot be turned back into the password.

From `app/models.py`:

```python
def set_password(self, password):
    self.password_hash = generate_password_hash(password)     # -> scrypt hash

def check_password(self, password):
    return check_password_hash(self.password_hash, password)  # compare hashes, no decryption
```

---

## How login works (step by step)

Handled by **Flask-Login** in `app/auth.py`:

1. The user submits the **login form** (email + password). It's a Flask-WTF form, so a
   **CSRF token** is verified automatically.
2. We look up the user by email (lower-cased and trimmed).
3. We call `user.check_password(...)`. If the user doesn't exist **or** the password is
   wrong, we show the **same** message — *"Invalid email or password"* — so an attacker
   can't discover which emails are registered.
4. On success, `login_user()` starts a signed **session cookie**; the user stays logged
   in until logout (or the cookie expires).
5. We redirect to the page the user originally wanted — but only if it's a **safe local
   URL** (an open-redirect guard), otherwise to the dashboard.

---

## How access is controlled

Two layers, both enforced **on the server** (not just hidden in the UI):

- **`@login_required`** — you must be logged in to reach any real page or API
  (used across `api.py`, `inventory.py`, `reports.py`, `main.py`).
- **`@role_required(...)`** — you must have the right role, or the server returns
  **403 Forbidden**. From `app/decorators.py`:
  ```python
  @role_required("manager", "owner")   # a staff user gets 403 here
  def edit_product(...): ...
  ```

Plus **CSRF protection** site-wide (`CSRFProtect()` in `app/__init__.py`); every form
carries a `csrf_token`.

---

## Changing or resetting a password

> **Current status:** there is **no self-service "change password" screen** in this
> version. Passwords are set when accounts are created, and an administrator can reset
> one by calling `set_password()` (which re-hashes the new password) — for example from
> a Flask shell:
>
> ```python
> u = User.query.filter_by(email="staff@ransbet.com").first()
> u.set_password("new-password")
> db.session.commit()
> ```
>
> **Next step:** a self-service *Account → Change Password* page (enter current + new
> password) — small to add, since `User` already has `check_password` and `set_password`.

---

## Where it lives (file map)

| File | Role |
|------|------|
| `app/models.py` | `User` model, `set_password` / `check_password`, role constants |
| `app/auth.py` | Login form + login & logout routes (Flask-Login) |
| `app/decorators.py` | `@role_required` — returns 403 for the wrong role |
| `app/__init__.py` | Login manager + CSRF setup |
| `seed.py` | Creates the demo accounts |
