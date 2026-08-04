import os
import socket
import subprocess
import sys
import time
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parents[2]
SEED_SCRIPT = BASE_DIR / "tests" / "ui" / "seed_data.py"


def _wait_for_http(url: str, timeout_s: float = 25.0) -> None:
    import urllib.request

    start = time.time()
    last_err = None
    while time.time() - start < timeout_s:
        try:
            with closing(urllib.request.urlopen(url)) as resp:
                if 200 <= resp.status < 500:
                    return
        except Exception as e:  # noqa: BLE001
            last_err = e
            time.sleep(0.25)
    raise RuntimeError(f"Server not reachable at {url} within {timeout_s}s. Last error: {last_err}")


def _get_free_port(host: str = "127.0.0.1") -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, 0))
        return int(s.getsockname()[1])


@dataclass(frozen=True)
class ServerCtx:
    host: str
    port: int
    base_url: str
    env: dict


@pytest.fixture(scope="session")
def server_ctx(tmp_path_factory) -> ServerCtx:
    host = "127.0.0.1"
    port = _get_free_port(host)
    base_url = f"http://{host}:{port}"

    env = os.environ.copy()
    env["DJANGO_SETTINGS_MODULE"] = "myapp.settings"

    test_db_path = tmp_path_factory.mktemp("db") / "test_ui.sqlite3"
    env["EMS_UI_TEST_DB"] = str(test_db_path)

    return ServerCtx(host=host, port=port, base_url=base_url, env=env)


@pytest.fixture(scope="session")
def live_server_url(server_ctx: ServerCtx):
    # migrate isolated DB
    subprocess.check_call(
        [sys.executable, str(BASE_DIR / "manage.py"), "migrate", "--noinput"],
        cwd=str(BASE_DIR),
        env=server_ctx.env,
    )

    creationflags = 0
    if os.name == "nt":
        creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

    proc = subprocess.Popen(
        [sys.executable, str(BASE_DIR / "manage.py"), "runserver", f"{server_ctx.host}:{server_ctx.port}"],
        cwd=str(BASE_DIR),
        env=server_ctx.env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        creationflags=creationflags,
    )

    try:
        _wait_for_http(server_ctx.base_url + "/emp/home/")
        print(f"[E2E] Base URL: {server_ctx.base_url}")
        print(f"[E2E] EMS_UI_TEST_DB (server): {server_ctx.env['EMS_UI_TEST_DB']}")
        yield server_ctx.base_url
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()


@pytest.fixture(autouse=True)
def seed_employees(server_ctx: ServerCtx, live_server_url):
    # IMPORTANT: reuse the SAME env used by runserver so we seed the same DB file
    env = server_ctx.env.copy()

    seed_code = SEED_SCRIPT.read_text(encoding="utf-8")
    print(f"[E2E] EMS_UI_TEST_DB (seed): {env['EMS_UI_TEST_DB']}")
    subprocess.check_call(
        [sys.executable, str(BASE_DIR / "manage.py"), "shell", "-c", seed_code],
        cwd=str(BASE_DIR),
        env=env,
        text=True,
    )


@pytest.fixture()
def ui(page, live_server_url):
    class UI:
        base = live_server_url

        def goto(self, path: str):
            if not path.startswith("/"):
                path = "/" + path
            return page.goto(self.base + path)

    return UI()