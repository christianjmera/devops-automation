#!/usr/bin/env python3

import base64
import json
import os
import subprocess
import time
import urllib.error
import urllib.request


API_URL = "https://api.github.com"
REPOSITORY = "christianjmera/devops-automation"


def base64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def generate_jwt(app_id, private_key):
    now = int(time.time())

    header = {"alg": "RS256", "typ": "JWT"}
    payload = {
        "iat": now - 60,
        "exp": now + 540,
        "iss": app_id,
    }

    message = (
        base64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + base64url(json.dumps(payload, separators=(",", ":")).encode())
    )

    signature = subprocess.run(
        ["openssl", "dgst", "-sha256", "-sign", private_key],
        input=message.encode(),
        capture_output=True,
        check=True,
    ).stdout

    return message + "." + base64url(signature)

def github_request(url, token, method="GET", data=None):
    body = (
        json.dumps(data).encode()
        if data is not None
        else None
    )

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    if data is not None:
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers=headers,
    )

    with urllib.request.urlopen(request, timeout=20) as response:
        return json.loads(response.read())

def get_installation_token(
    app_id,
    installation_id,
    private_key,
    repositories=None,
    permissions=None,
):
    jwt = generate_jwt(app_id, private_key)

    payload = {}

    if repositories:
        payload["repositories"] = repositories

    if permissions:
        payload["permissions"] = permissions

    response = github_request(
        f"{API_URL}/app/installations/{installation_id}/access_tokens",
        jwt,
        method="POST",
        data=payload or None,
    )

    return response["token"]

def main():
    app_id = os.environ["GITHUB_APP_ID"]
    installation_id = os.environ["GITHUB_INSTALLATION_ID"]
    private_key = os.path.expanduser(os.environ["GITHUB_PRIVATE_KEY"])

    print("1. Generando JWT...")
    token = get_installation_token(
        app_id, installation_id, private_key
    )
    print("   JWT generado e intercambio realizado correctamente.")

    print("2. Validando acceso al repositorio...")
    repository = github_request(
        f"{API_URL}/repos/{REPOSITORY}/contents/README.md",
        token,
    )

    print(f"   Repositorio: {REPOSITORY}")
    print(f"   Archivo: {repository['name']}")
    print("   Acceso al contenido: correcto")
    print("3. Token de instalación obtenido correctamente.")
    print("   El token no se ha mostrado ni almacenado.")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as error:
        print(f"ERROR HTTP: {error.code} - {error.reason}")
        print(error.read().decode(errors="replace"))
        raise SystemExit(1)
    except Exception as error:
        print(f"ERROR: {type(error).__name__}: {error}")
        raise SystemExit(1)
