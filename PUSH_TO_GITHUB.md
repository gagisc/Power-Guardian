# Pushing to GitHub (replace YOUR_ORG with your GitHub org / username)

## 1 — Create the remote repository (GitHub CLI)
gh repo create YOUR_ORG/pdu-power-guardian --public --description "Eaton ePDU G3 / APC Smart-UPS / Schneider Galaxy power anomaly detector"

## 2 — Initialise git, commit, and push
cd pdu-power-guardian
git init
git add -A
git commit -m "feat: initial scaffold — v0.1.0

- Device collector stubs (FLIR A310 / DS18B20 / Eaton / APC / Schneider /
  gNMI / iDRAC / iLO / RAPL / DCGM / Pi HQ Camera / FLIR Lepton)
- Simulation mode active by default; production mode enabled via env vars
- Docker Compose demo environment
- Smoke experiment runner (CI-safe, CPU-only, < 60 s)
- GitHub Actions CI workflow
- CASE_STUDY.md with simulated baseline vs intervention metrics
- MIT License

No real credentials included. Use .env (see .env.example)."

git remote add origin https://github.com/YOUR_ORG/pdu-power-guardian.git
git branch -M main
git push -u origin main
git tag v0.1.0 -m "Release v0.1.0 — initial scaffold"
git push origin v0.1.0
