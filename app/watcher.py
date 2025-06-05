import os
import time
import logging

DATA_FOLDER = os.environ.get("DATA_FOLDER", "/data")


# ================================
# Background File Watcher
# ================================
def start_background_watcher():
    """
    Surveille en tâche de fond les ajouts, suppressions et modifications
    de fichiers dans le dossier DATA_FOLDER.
    """
    try:
        last_snapshot = {
            f: (
                os.stat(os.path.join(DATA_FOLDER, f)).st_size,
                os.stat(os.path.join(DATA_FOLDER, f)).st_mtime,
            )
            for f in os.listdir(DATA_FOLDER)
            if os.path.isfile(os.path.join(DATA_FOLDER, f))
        }
    except FileNotFoundError:
        last_snapshot = {}

    while True:
        current_snapshot = {}

        try:
            for filename in os.listdir(DATA_FOLDER):
                filepath = os.path.join(DATA_FOLDER, filename)
                if os.path.isfile(filepath):
                    stat = os.stat(filepath)
                    current_snapshot[filename] = (stat.st_size, stat.st_mtime)
        except FileNotFoundError:
            current_snapshot = {}

        # Détection des changements
        added = current_snapshot.keys() - last_snapshot.keys()
        removed = last_snapshot.keys() - current_snapshot.keys()
        common = current_snapshot.keys() & last_snapshot.keys()

        for f in added:
            logging.info(f"[+] Nouveau fichier détecté : {f}")
        for f in removed:
            logging.info(f"[-] Fichier supprimé : {f}")
        for f in common:
            old_size, old_mtime = last_snapshot[f]
            new_size, new_mtime = current_snapshot[f]
            if old_size != new_size or old_mtime != new_mtime:
                logging.info(f"[~] Fichier modifié : {f}")

        last_snapshot = current_snapshot
        time.sleep(2)
