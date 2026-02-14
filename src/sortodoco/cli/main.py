from .app import build_app

def main() -> None:
    app = build_app()
    app()
