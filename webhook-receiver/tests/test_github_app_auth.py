import unittest
from unittest.mock import patch

import github_app_auth


class GitHubAppAuthTests(unittest.TestCase):

    @patch("github_app_auth.github_request")
    @patch("github_app_auth.generate_jwt")
    def test_token_with_repository_and_permissions(
        self,
        mock_generate_jwt,
        mock_github_request,
    ):
        # Simular la generación del JWT.
        mock_generate_jwt.return_value = "jwt-falso"

        # Simular la respuesta de GitHub.
        mock_github_request.return_value = {
            "token": "token-falso"
        }

        token = github_app_auth.get_installation_token(
            "app-id",
            "installation-id",
            "/ruta/clave.pem",
            repositories=["repositorio-central"],
            permissions={
                "contents": "write"
            },
        )

        # Comprobar que se devuelve el token recibido.
        self.assertEqual(token, "token-falso")

        # Verificar que GitHub recibe las restricciones solicitadas.
        mock_github_request.assert_called_once_with(
            f"{github_app_auth.API_URL}/app/installations/"
            "installation-id/access_tokens",
            "jwt-falso",
            method="POST",
            data={
                "repositories": ["repositorio-central"],
                "permissions": {
                    "contents": "write"
                },
            },
        )

    @patch("github_app_auth.github_request")
    @patch("github_app_auth.generate_jwt")
    def test_token_without_optional_restrictions(
        self,
        mock_generate_jwt,
        mock_github_request,
    ):
        # Simular la generación del JWT.
        mock_generate_jwt.return_value = "jwt-falso"

        # Simular la respuesta de GitHub.
        mock_github_request.return_value = {
            "token": "token-falso"
        }

        token = github_app_auth.get_installation_token(
            "app-id",
            "installation-id",
            "/ruta/clave.pem",
        )

        # Comprobar que se devuelve el token recibido.
        self.assertEqual(token, "token-falso")

        # Verificar que la función conserva su comportamiento anterior.
        mock_github_request.assert_called_once_with(
            f"{github_app_auth.API_URL}/app/installations/"
            "installation-id/access_tokens",
            "jwt-falso",
            method="POST",
            data=None,
        )


if __name__ == "__main__":
    unittest.main()
