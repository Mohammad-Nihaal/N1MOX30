# N1MOX30 — Quick Start

## Windows

1. Extract this ZIP.
2. Open PowerShell in the extracted `N1mox30_work` folder.
3. Run:

```powershell
Set-ExecutionPolicy -Scope Process Bypass
.\start_n1mox30.ps1
```

The launcher creates the backend virtual environment, installs dependencies, initializes the database, installs frontend dependencies, and starts both services.

## Local demo account

Run the seed command once if you want pre-populated creator context:

```powershell
cd .\backend
.\.venv\Scripts\Activate.ps1
python .\scripts\seed_demo.py
```

Demo login:

- Email: `demo@n1mox30.local`
- Password: `N1MOX30-Demo-2026!`

## Important boundary

The application includes provider-neutral integrations and deterministic local fallbacks. Real Google/YouTube publishing, paid AI providers, and other external services require the user's own credentials and account authorization. Those credentials are intentionally not included in the ZIP.
