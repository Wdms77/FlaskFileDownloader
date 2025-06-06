import os
import time
import requests

BASE_URL = "http://localhost:5000"
DATA_FOLDER = "/data"
TEST_FILENAME = "hellotest.txt"
TEST_CONTENT = "Prometheus test content"
TEST_FILEPATH = os.path.join(DATA_FOLDER, TEST_FILENAME)


def setup_module(module):
    """Créer le fichier de test partagé avant les tests"""
    with open(TEST_FILEPATH, "w") as f:
        f.write(TEST_CONTENT)
    time.sleep(2)


def teardown_module(module):
    """Supprimer le fichier après tous les tests"""
    if os.path.exists(TEST_FILEPATH):
        os.remove(TEST_FILEPATH)


def test_index_page():
    r = requests.get(f"{BASE_URL}/")
    assert r.status_code == 200
    assert "<html" in r.text.lower()


def test_file_appears_in_api():
    r = requests.get(f"{BASE_URL}/api/files")
    assert r.status_code == 200
    files = r.json()
    assert any(f["name"] == TEST_FILENAME for f in files)


def test_download_file():
    r = requests.get(f"{BASE_URL}/download/{TEST_FILENAME}")
    assert r.status_code == 200
    assert r.text == TEST_CONTENT


def test_metrics_endpoint():
    r = requests.get(f"{BASE_URL}/metrics")
    assert r.status_code == 200
    assert TEST_FILENAME in r.text  # Vérifie que Prometheus a observé une requête liée au fichier
