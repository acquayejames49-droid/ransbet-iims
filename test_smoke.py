"""
Smoke test — a quick health check before the presentation.

Run it the DAY BEFORE (and the morning of) to confirm everything works. It logs
in and opens every important page, API and report, checking each responds
correctly. Green [ OK ] = good; red [FAIL] = something to look at.

It only READS data (the one POST is the login), so it is safe to run against
the live site.

Usage (from the project folder):
  python test_smoke.py
        -> checks your LOCAL site at http://127.0.0.1:5000
           (start it first with START_RANSBET.bat)

  python test_smoke.py https://aizen004.pythonanywhere.com
        -> checks the LIVE site (no local server needed)
"""
import sys
import re
import json
import urllib.request
import urllib.parse
import urllib.error
import http.cookiejar

BASE = (sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000").rstrip("/")

MANAGER = ("manager@ransbet.com", "manager123")
STAFF = ("staff@ransbet.com", "staff123")

results = []


def check(name, ok, detail=""):
    results.append(bool(ok))
    mark = "[ OK ]" if ok else "[FAIL]"
    line = f"  {mark}  {name}"
    if detail and not ok:
        line += f"   <- {detail}"
    print(line)


def new_session():
    jar = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))


def fetch(opener, path, data=None, referer=None):
    """GET (or POST if data given). Returns (status_code, body_text)."""
    url = BASE + path
    headers = {"Referer": referer} if referer else {}
    req = urllib.request.Request(url, data=data, headers=headers)
    try:
        with opener.open(req, timeout=40) as r:
            return r.getcode(), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # connection refused, timeout, etc.
        return 0, str(e)


def login(opener, email, password):
    """Log in the way a browser does (grab the CSRF token, then POST)."""
    code, html = fetch(opener, "/login")
    m = re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html)
    if not m:
        return False
    data = urllib.parse.urlencode({
        "csrf_token": m.group(1),
        "email": email,
        "password": password,
        "submit": "Sign in",
    }).encode()
    fetch(opener, "/login", data=data, referer=BASE + "/login")
    # We are logged in if a protected API now returns 200 instead of 401.
    code, _ = fetch(opener, "/api/overview")
    return code == 200


def main():
    print(f"\nSmoke test against: {BASE}")
    print("=" * 52)

    # 1) Login
    print("\nLogin & authentication")
    mgr = new_session()
    manager_ok = login(mgr, *MANAGER)
    check("manager can log in", manager_ok)
    if not manager_ok:
        print("\n  Could not log in — is the server running / URL correct?")
        print("=" * 52)
        sys.exit(1)

    # 2) Pages a manager should be able to open (expect 200)
    print("\nManager pages (expect HTTP 200)")
    pages = ["/dashboard", "/products", "/sales", "/movements", "/suppliers",
             "/reports", "/scan", "/categories", "/audit", "/data"]
    for p in pages:
        code, _ = fetch(mgr, p)
        check(f"GET {p}", code == 200, f"got {code}")

    # 3) Dashboard data APIs (expect 200 JSON)
    print("\nDashboard APIs (expect HTTP 200)")
    apis = ["/api/overview", "/api/reminders", "/api/monthly-trend",
            "/api/inventory-intelligence", "/api/kpis", "/api/top-items",
            "/api/stock-status", "/api/anomalies", "/api/products"]
    first_pid = None
    for p in apis:
        code, body = fetch(mgr, p)
        check(f"GET {p}", code == 200, f"got {code}")
        if p == "/api/products" and code == 200:
            try:
                arr = json.loads(body)
                if arr:
                    first_pid = arr[0]["id"]
            except Exception:
                pass
    if first_pid is not None:
        code, _ = fetch(mgr, f"/api/forecast/{first_pid}")
        check(f"GET /api/forecast/{first_pid}", code == 200, f"got {code}")

    # 4) Report downloads (expect 200)
    print("\nReport downloads (expect HTTP 200)")
    reports = ["/reports/inventory.pdf", "/reports/inventory.csv",
               "/reports/sales.pdf", "/reports/sales.csv",
               "/reports/forecast.pdf", "/reports/forecast.csv"]
    for p in reports:
        code, _ = fetch(mgr, p)
        check(f"GET {p}", code == 200, f"got {code}")

    # 5) Role security — staff must be BLOCKED from manager-only pages (expect 403)
    print("\nRole security (staff must be blocked = HTTP 403)")
    stf = new_session()
    staff_ok = login(stf, *STAFF)
    check("staff can log in", staff_ok)
    if staff_ok:
        for p in ["/data", "/categories", "/audit"]:
            code, _ = fetch(stf, p)
            check(f"staff blocked from {p}", code == 403, f"got {code}, expected 403")

    # Summary
    total = len(results)
    passed = sum(results)
    print("\n" + "=" * 52)
    if passed == total:
        print(f"  ALL {total} CHECKS PASSED  -  you're good to go!")
    else:
        print(f"  {passed}/{total} passed  -  {total - passed} FAILED (see red marks above)")
    print("=" * 52 + "\n")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    main()
