from pathlib import Path
import shutil


def publish_pages_files(base_dir: Path, output_dir: Path):
    pages_dir = base_dir / 'pages'
    data_dir = pages_dir / 'data'
    mini_app_dir = pages_dir / 'mini_app'
    data_dir.mkdir(parents=True, exist_ok=True)
    mini_app_dir.mkdir(parents=True, exist_ok=True)

    dashboard_src = output_dir / 'dashboard_data.json'
    if dashboard_src.exists():
        shutil.copyfile(dashboard_src, data_dir / 'dashboard_data.json')
