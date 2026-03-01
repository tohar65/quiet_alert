# Deployment Strategy: Quiet Alert

This document outlines the research and final plan for deploying the Quiet Alert web application.

## 1. Research of Deployment Services

The following services were evaluated based on their free tier, CLI support, and ability to handle persistent background processes.

| Service | Free Tier | CLI | Background Process Support | Verdict |
| :--- | :--- | :--- | :--- | :--- |
| **Koyeb** | "Eco" Tier (Free), 512MB RAM, 0.1 vCPU. | Yes (`koyeb`) | **Excellent** (Does not sleep, 24/7 uptime on Eco). | **Winner (Free)** |
| **Railway** | $5 trial credit (one-time). Then $1/mo min for Hobby. | Yes (`railway`) | **Excellent** (Reliable persistent processes). | **Winner (Paid/Easy)** |
| **Fly.io** | 3 shared-cpu-1x 256mb VMs free allowance. | Yes (`flyctl`) | **Excellent** (Standard VMs). Requires CC. | **Strong Contender** |
| **Render** | Free instance. | Yes (`render`) | **Poor** (Sleeps after 15 mins of inactivity). | Rejected |
| **Vercel** | Free hobby plan. | Yes (`vercel`) | **None** (Serverless functions only). | Rejected |

## 2. Selected Best Fit: Koyeb (Primary) & Railway (Alternative)

For a truly free, persistent deployment without auto-sleep, **Koyeb** is the best fit. If ease of use and a more robust CLI are preferred over a long-term free tier, **Railway** is the alternative.

### Why Koyeb?
1.  **No Idling**: Unlike Render, Koyeb Eco instances stay active. This is crucial for our `poll_realtime_alerts` background thread.
2.  **Generous Free Tier**: 512MB RAM is sufficient for this Flask app.
3.  **GitHub Integration**: Seamless auto-deployment.
4.  **CLI**: Feature-rich CLI for management.

---

## 3. Deployment Design

### A. Repository Structure
The deployment will be triggered from the repository root to ensure both the `web_app` and `oref_alert_parser` are available.

### B. Configuration Files

#### `Procfile`
Used by many platforms to define the entry point.
```yaml
web: python web_app/web_server.py
```

#### `requirements.txt` (Root level)
We will create a root `requirements.txt` to handle all dependencies, including the local package.
```text
flask
requests
colorama
-e ./oref_alert_parser
```

#### `runtime.txt`
Specifies the Python version.
```text
python-3.11.x
```

### C. Environment Variables
The following variables should be configured in the deployment platform:
-   `PORT`: (Automatically set by the platform)
-   `DEBUG`: `False`
-   `PYTHONPATH`: `.` (To ensure imports work correctly)
-   `OREF_REALTIME_URL`: (Optional, for overriding)
-   `OREF_HISTORY_URL`: (Optional, for overriding)

---

## 4. Installation of Local Package

The `oref_alert_parser` is a local package. To ensure it is installed correctly during the build process:
1.  **Editable Install**: The root `requirements.txt` will use `-e ./oref_alert_parser`.
2.  **Alternative Build Command**: If the platform allows custom build commands, use:
    `pip install -r web_app/requirements.txt && pip install -e oref_alert_parser`

---

## 5. GitHub Integration

### Steps to Integrate:
1.  Connect the GitHub repository `tohar65/quiet_alert` to the chosen service (Koyeb or Railway).
2.  Select the `main` branch for deployment.
3.  Configure the root directory as the deployment directory.
4.  Set up the Environment Variables (Secrets) in the platform UI.
5.  Auto-deploy will trigger on every `git push`.

---

## 6. Implementation Plan (Next Steps)

1.  Create root-level `requirements.txt`, `Procfile`, and `runtime.txt`.
2.  Test the deployment using the CLI of the chosen service.
3.  Verify that the background polling thread is running (check logs for "[Server] Real-time alerts updated").
4.  Confirm the UI correctly displays the alerts fetched in the background.
