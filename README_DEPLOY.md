
# Deploy to Streamlit Community Cloud (Mobile-friendly Web App)

This folder is ready to deploy your PT app as a **mobile-friendly web app** using Streamlit Community Cloud.

## Quick Deploy (5–10 min)

1. Create a **new GitHub repository** (public or private).
2. Upload these files to the repo (the entire `pt_app_web` contents):
   - `app.py`
   - `templates.py`
   - `equipment.json`
   - `requirements.txt`
   - *(Do NOT commit `pt.db`; it will be created at runtime.)*
3. Go to **https://streamlit.io/cloud** → Sign in → **New app**.
4. Select your repo/branch and set **app file** to `app.py`, then **Deploy**.

Streamlit will build and give you a public URL like `https://your-app.streamlit.app/` — open it on your phone and **Add to Home Screen** to use it like an app.

> Tip: If you want a custom subdomain, set it in the app settings after deploy.

## Notes on Data Persistence

- The app stores workouts in `pt.db` (SQLite). On Streamlit Cloud, the filesystem can reset on **rebuild/redeploy**.
- If you want guaranteed persistent storage, connect a **cloud database** (e.g., Supabase or Neon/Postgres) and replace the SQLite connection in `app.py`.
- Easiest interim option: **Export/backup** data periodically (add a simple export button) or keep the app stable (avoid frequent redeploys).

## Mobile Use

- The UI is responsive. In Chrome/Safari on your phone:
  - Open your app URL → Share → **Add to Home Screen** for an app-like icon & full-screen experience.

## Local dev

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

If you need help wiring to a cloud DB for permanent storage, let me know — I can add a Postgres connector and migration for you.
