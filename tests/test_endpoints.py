import os
import tempfile
import pytest
from app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True

    # Créer un dossier temporaire avec un fichier
    with tempfile.TemporaryDirectory() as tmpdir:
        app.config["DATA_FOLDER"] = tmpdir
        # Créer un fichier test
        file_path = os.path.join(tmpdir, "testfile.txt")
        with open(file_path, "w") as f:
            f.write("contenu test")

        yield app.test_client()


def test_index(client):
    res = client.get("/")
    assert res.status_code == 200
    assert b"Fichiers disponibles" in res.data


def test_api_files(client):
    res = client.get("/api/files")
    assert res.status_code == 200
    data = res.get_json()
    assert isinstance(data, list)
    assert any(f["name"] == "testfile.txt" for f in data)


def test_download_existing_file(client):
    res = client.get("/download/testfile.txt")
    assert res.status_code == 200
    assert res.data == b"contenu test"


def test_download_nonexistent_file(client):
    res = client.get("/download/nofile.txt")
    assert res.status_code == 404
