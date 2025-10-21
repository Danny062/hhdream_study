import asyncio
import json
from pathlib import Path

from config import config
from html_parser import parse_qa_requirements
from qb_client import QBClient
from read_write_excel import read_material_numbers_from_excel
from web_scraper import WebScraper


async def process_material(mano: str, scraper: WebScraper, client: QBClient, output_folder: Path):
    """Processes a single material number."""
    print(f"--- Processing Material: {mano} ---")
    material_data = client.get_material_details(mano)
    comp_id = material_data.get("component_id")

    mano_folder = output_folder / f"material_{mano}"
    mano_folder.mkdir(parents=True, exist_ok=True)

    if comp_id:
        try:
            # Ensure component_id is an integer for the URL
            rid = int(comp_id)
            html = await scraper.get_qa_html(rid)
            qa_reqs = parse_qa_requirements(html)
            material_data["qa_requirements"] = qa_reqs
        except (ValueError, TypeError) as e:
            print(f"Invalid component_id '{comp_id}' for material {mano}: {e}")
        except Exception as e:
            print(f"Could not fetch QA requirements for component {comp_id}: {e}")

    # Download images
    image_folder = mano_folder / "images"
    image_folder.mkdir(parents=True, exist_ok=True)
    for i, image_url in enumerate(material_data.get("image_url", []), start=1):
        image_path = image_folder / f"image_{i}.png"
        await scraper.download_image(image_url, image_path)

    # Save all collected data
    json_path = mano_folder / f"material_{mano}_data.json"
    with open(json_path, "w") as f:
        json.dump(material_data, f, indent=4)
    print(f"--- Finished Material: {mano} ---\n\n\n")


async def run_extraction(excel_path: str):
    """Main orchestration function."""
    material_numbers = read_material_numbers_from_excel(excel_path, config.material_number_field)
    if not material_numbers:
        print("No material numbers found in the Excel file.")
        return

    print(f"Found {len(material_numbers)} material numbers to process.")
    output_folder = Path("downloads") / Path(excel_path).stem
    output_folder.mkdir(parents=True, exist_ok=True)

    qb_client = QBClient(config)

    async with WebScraper(config, headless=config.headless) as scraper:
        for mano in material_numbers:
            await process_material(mano, scraper, qb_client, output_folder)


if __name__ == "__main__":
    # Update this path to your actual Excel file location
    parent_dir = Path("/Users/ai/PycharmProjects/POC/hhd_study/ES.C95914")
    for file in parent_dir.glob("*.xls"):
        print(f"Processing file: {file}")
        asyncio.run(run_extraction(str(file)))