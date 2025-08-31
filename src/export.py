import json
from .utils import log


def export_to_json(data, output_path: str):
    """
    Export scraped data to a JSON file.
    """
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        log(f"💾 Data exported to {output_path}")
    except Exception as e:
        log(f"❌ Failed to export data: {e}")



