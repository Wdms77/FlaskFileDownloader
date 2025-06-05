import os
import sys
import logging
import threading
from flask import Flask
from flask_talisman import Talisman
from .watcher import start_background_watcher
from prometheus_flask_exporter import PrometheusMetrics


# ================================
# Content Security Policy (CSP)
# ================================
csp = {
    "default-src": "'self'",
    "style-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
    "script-src": ["'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net"],
    "font-src": ["'self'", "https://cdn.jsdelivr.net"],
    "img-src": ["'self'", "data:"],
    "connect-src": ["'self'"],
}


# ================================
# Logging Setup
# ================================
def setup_logging():
    log_dir = "/logs"
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    root_logger.handlers = []  # Clear existing handlers
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    logging.info("✅ Logging configured. Logs in %s", log_file)


# ================================
# Flask App Factory
# ================================
def create_app() -> Flask:
    setup_logging()

    app = Flask(__name__)
    metrics = PrometheusMetrics(app)  # Initialize Prometheus monitoring

    # Apply security headers via Talisman
    Talisman(app, content_security_policy=csp, frame_options="DENY", force_https=False)

    # Register blueprints
    from .routes import main_bp
    app.register_blueprint(main_bp)

    # Start background file watcher thread
    watcher_thread = threading.Thread(target=start_background_watcher, daemon=True)
    watcher_thread.start()

    logging.info("🚀 Flask application started.")
    return app