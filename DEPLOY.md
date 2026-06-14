# Deploying Ransbet IIMS live (PythonAnywhere, free)

This puts the system online so anyone can log in from any device. Your live
address will be **`https://YOURUSERNAME.pythonanywhere.com`**.

> Tip: when you sign up, choose the username **`ransbetiims`** so your URL reads
> `ransbetiims.pythonanywhere.com`.

You only do this once. Updating later is just `git pull` + **Reload** (step 6).

---

## 0. Before you start
- Code pushed to GitHub: `https://github.com/acquayejames49-droid/ransbet-iims`
- A free PythonAnywhere account: https://www.pythonanywhere.com/registration/register/beginner/

## 1. Create the MySQL database
PythonAnywhere → **Databases** tab:
1. Set a MySQL password (remember it).
2. Under "Create a database", type **`ransbet_iims`** → Create.
   It becomes **`YOURUSERNAME$ransbet_iims`**.

## 2. Get the code + install packages
PythonAnywhere → **Consoles** → start a **Bash** console:
```bash
git clone https://github.com/acquayejames49-droid/ransbet-iims.git
cd ransbet-iims
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-deploy.txt
```

## 3. Load the data into the live database
Still in the Bash console (replace YOURUSERNAME, enter your DB password when asked):
```bash
mysql -u YOURUSERNAME -h YOURUSERNAME.mysql.pythonanywhere-services.com \
      -p 'YOURUSERNAME$ransbet_iims' < deploy/ransbet_iims.sql
```

## 4. Create the web app
PythonAnywhere → **Web** tab → **Add a new web app**:
1. Framework: **Manual configuration** (NOT "Flask").
2. Python version: **3.11**.
3. After it's created, set **Virtualenv** to:
   `/home/YOURUSERNAME/ransbet-iims/.venv`
4. Under **Static files**, add:  URL `/static/`  →  Directory `/home/YOURUSERNAME/ransbet-iims/app/static`

## 5. Configure the WSGI file
On the **Web** tab, click the **WSGI configuration file** link. Delete all of it
and paste in the contents of `deploy/pythonanywhere_wsgi.py` from this repo, then
change `USERNAME` and `DB_PASSWORD` near the top. Save.

Click the big green **Reload** button. Visit **`https://YOURUSERNAME.pythonanywhere.com`**
and log in (manager@ransbet.com / manager123).

## 6. Updating the live site later
After you push changes to GitHub, in a PythonAnywhere Bash console:
```bash
cd ransbet-iims && git pull && source .venv/bin/activate && pip install -r requirements-deploy.txt
```
Then hit **Reload** on the Web tab.

## Notes
- The free tier shows your app at `*.pythonanywhere.com`. A custom domain like
  `ransbetiims.com` needs a paid plan (~$5/mo) + buying the domain (~$12/yr).
- Free accounts must click "Run until 3 months from today" occasionally to keep
  the app alive — PythonAnywhere emails you a reminder.
