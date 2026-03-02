"""Launcher for HELM interactive dashboard (Phase 4B)

Usage:
    python run_dashboard.py

This will start Streamlit if installed, otherwise it will run in DEMO_MODE and
exit gracefully.
"""

from helm.config import Config
from helm.ui.dashboard import Dashboard


def main():
    cfg = Config()
    # ensure demo flag does not prevent full Streamlit if available
    cfg.DEVELOPMENT_MODE = True
    # By default, run with whatever weights are in env/config
    dash = Dashboard(config=cfg)
    success = dash.start()
    if not success:
        print("Dashboard failed to start (Streamlit missing?).")
    else:
        print("Dashboard started. Connect via browser to http://{}:{}".format(cfg.dashboard_host, cfg.dashboard_port))


if __name__ == '__main__':
    main()
