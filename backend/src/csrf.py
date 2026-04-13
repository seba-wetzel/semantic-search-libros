import secrets
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

CSRF_COOKIE = "csrf_token"
CSRF_HEADER = "x-csrf-token"

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def generate_csrf_token() -> str:
    return secrets.token_urlsafe(32)


def set_csrf_cookie(response: JSONResponse, token: str) -> None:
    response.set_cookie(
        key=CSRF_COOKIE,
        value=token,
        httponly=False,   # El frontend necesita leerla con JS
        samesite="strict",
        secure=True,
    )


async def verify_csrf(request: Request) -> None:
    """Verifica el token CSRF en requests que modifican estado."""
    if request.method in SAFE_METHODS:
        return

    cookie_token = request.cookies.get(CSRF_COOKIE)
    header_token = request.headers.get(CSRF_HEADER)

    if not cookie_token or not header_token:
        raise HTTPException(status_code=403, detail="CSRF token faltante.")

    if not secrets.compare_digest(cookie_token, header_token):
        raise HTTPException(status_code=403, detail="CSRF token inválido.")
