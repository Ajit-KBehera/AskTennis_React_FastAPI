"""Entrypoint for Appwrite auth function."""

from app.functions.app_factory import create_auth_function_app

app = create_auth_function_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
