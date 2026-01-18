import yaml
from pathlib import Path

def load_rules(version: str) -> dict:
    base_path = Path(__file__).parent.parent / "rules_config"
    file_path = base_path / f"{version.replace('.', '_')}.yaml"

    if not file_path.exists():
        raise FileNotFoundError(f"Rules file not found: {file_path}")

    with open(file_path, "r") as f:
        return yaml.safe_load(f)
