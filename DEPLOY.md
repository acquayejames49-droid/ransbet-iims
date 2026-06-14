# Deploying Ransbet IIMS live (PythonAnywhere, free)

This puts the system online so anyone can log in from any device. Your live
address will be **`https://aizen004.pythonanywhere.com`**.

> The free tier no longer includes MySQL, so the hosted copy uses the SQLite
> database file (`iims.db`) that ships with this repo — fully loaded with the
> catalogue, 2 years of sales, forecasts and anomalies. Your LOCAL system still
> runs on real MySQL 8.0. (To use MySQL online too, upgrade to a paid plan.)

You only do this once. Updating later = `git pull` + **Reload** (step 5).

---

## 0. Before you start
- Code on GitHub: `https://github.com/acquayejames49-droid/ransbet-iims`
- A free PythonAnywhere account (username `aizen004`).

## 1. Get the code + install packages
PythonAnywhere → **Consoles** → start a **Bash** console:
```bash
git clone https://github.com/acquayejames49-droid/ransbet-iims.git
cd ransbet-iims
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-deploy.txt
```
(If you already cloned earlier, run `cd ransbet-iims && git pull` instead of cloning.)

## 2. Create the web app
PythonAnywhere → **Web** tab → **Add a new web app**:
1. Framework: **Manual configuration** (NOT "Flask").
2. Python version: **3.11**.
3. After it's created, set **Virtualenv** to:
   `/home/aizen004/ransbet-iims/.venv`
4. Under **Static files**, add:  URL `/static/`  →  Directory `/home/aizen004/ransbet-iims/app/static`

## 3. Configure the WSGI file
On the **Web** tab, click the **WSGI configuration file** link. Delete everything
in it and paste the contents of `deploy/pythonanywhere_wsgi.py` from this repo.
Change `SECRET_KEY` to any long random string. Save.

## 4. Go live
Click the big green **Reload** button, then visit
**`https://aizen004.pythonanywhere.com`** and log in:
- manager@ransbet.com / manager123  (or owner@… / staff@…)

## 5. Updating the live site later
After you push changes to GitHub, in a PythonAnywhere Bash console:
```bash
cd ransbet-iims && git pull
source .venv/bin/activate && pip install -r requirements-deploy.txt
```
Then hit **Reload** on the Web tab.

## Notes
- Free accounts must click **"Run until 3 months from today"** on the Web tab
  occasionally to keep the app alive — PythonAnywhere emails you a reminder.
- A custom domain like `ransbetiims.com` needs a paid plan (~$5/mo) + buying the
  domain (~$12/yr).
