"""Entrypoint for Appwrite query function."""

from app.functions.app_factory import create_query_function_app

app = create_query_function_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
