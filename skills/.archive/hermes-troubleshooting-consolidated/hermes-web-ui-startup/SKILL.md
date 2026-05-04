---
name: hermes-web-ui-startup
description: Start and troubleshoot the Hermes Agent Web UI (Vite + React frontend with Python backend)
---

# Hermes Web UI Startup & Troubleshooting

## Architecture Overview

Hermes Web UI consists of two components:
1. **Frontend**: Vite + React (`hermes-agent/web/`) - Port 5173
2. **Backend**: Python web server (`hermes_cli/web_server.py`) - Port 9119

Frontend proxies `/api/*` requests to the backend.

## Quick Start

### Start Frontend Dev Server
```bash
cd ~/.hermes/hermes-agent/web
npm run dev
# or directly: npx vite
```

Access at: `http://localhost:5173`

### Start Backend Dashboard
```bash
cd ~/.hermes
hermes dashboard
# or directly: python3 -m hermes_cli.web_server --port 9119
```

Access at: `http://localhost:9119`

## Common Issues & Fixes

### Issue 1: TypeScript Build Errors

**Symptom**: `npm run build` fails with TS errors like:
```
src/components/ModelPickerDialog.tsx(285,22): error TS2552: Cannot find name 'loadProviders'
```

**Fix**: Skip TypeScript check and start dev server directly:
```bash
# TypeScript errors don't prevent dev server from running
npx vite --no-open
```

### Issue 2: Python 3.9 Compatibility

**Symptom**: Backend fails with:
```
TypeError: unsupported operand type(s) for |: 'type' and 'NoneType'
```

**Cause**: Code uses Python 3.10+ type union syntax (`Path | None`)

**Fix**:
```bash
# Option 1: Upgrade to Python 3.10+
brew install python@3.10

# Option 2: Use frontend only (some features may not work)
# Frontend dev server still works standalone
npx vite
```

### Issue 3: Backend Connection Warnings

**Symptom**: Browser console shows warnings about dashboard unreachable:
```
[hermes] Dashboard at http://127.0.0.1:9119 unreachable
```

**Fix**: Start the backend separately or ignore if you only need UI preview:
```bash
# In separate terminal
cd ~/.hermes && hermes dashboard
```

### Issue 4: Dependencies Not Installed

**Symptom**: `npm run dev` fails immediately

**Fix**:
```bash
cd ~/.hermes/hermes-agent/web
npm install
npm run sync-assets
```

## Verification Steps

1. **Check frontend running**:
   ```bash
   curl -s http://localhost:5173 | head -5
   # Should return HTML doctype
   ```

2. **Check backend running**:
   ```bash
   curl -s http://localhost:9119/health
   # Should return OK or JSON status
   ```

3. **Check processes**:
   ```bash
   ps aux | grep -E "(vite|hermes.*dashboard)" | grep -v grep
   ```

## Development vs Production

### Development
- Frontend: `npm run dev` (port 5173)
- Backend: `hermes dashboard` (port 9119)
- Hot reload enabled
- CORS handled via Vite proxy

### Production
- Build frontend: `npm run build` (outputs to `hermes_cli/web_dist/`)
- Backend serves static files directly
- Single port (9119) for both UI and API

## Troubleshooting Checklist

- [ ] Node.js 20+ installed (`node --version`)
- [ ] Python 3.10+ installed (`python3 --version`)
- [ ] npm dependencies installed (`cd web && npm install`)
- [ ] Assets synced (`npm run sync-assets`)
- [ ] No other process using ports 5173 or 9119
- [ ] Backend running before making API calls
- [ ] Session token properly injected (handled by Vite plugin)

## Background Process Management

When running in background:
```bash
# Start frontend in background
cd ~/.hermes/hermes-agent/web && npx vite --no-open &

# Verify startup (may take 2-3 seconds)
sleep 3 && curl -s http://localhost:5173 > /dev/null && echo "Frontend OK"
```
