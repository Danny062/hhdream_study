import json
import shutil
import time
from pathlib import Path
from typing import Iterable

import gradio as gr

from info_extraction.result_to_excel import generate_reports
from main_flow import extract_data

EXCEL_SUFFIXES = {".xlsx", ".xls"}
TEMP_DIR = Path("./temp_uploads")
DOWNLOADS_DIR = Path("./downloads")


def save_to_temp(file_path: Path) -> Path:
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    dest_path = TEMP_DIR / file_path.name
    dest_path.write_bytes(file_path.read_bytes())
    return dest_path.resolve()


def coerce_to_path(uploaded) -> Path:
    """
    Gradio's `type="filepath"` returns raw strings, but other configurations
    may return objects with a `.name` attribute. This helper normalizes both.
    """
    if isinstance(uploaded, (str, Path)):
        return Path(uploaded)
    if hasattr(uploaded, "name"):
        return Path(uploaded.name)
    raise TypeError(f"Unsupported file reference type: {type(uploaded)}")


def get_list_path(files: Iterable) -> dict:
    if not files:
        return {"message": "No files were provided.", "saved_paths": []}

    saved_paths: list[str] = []
    for uploaded in files:
        source_path = coerce_to_path(uploaded)

        if not source_path.is_file():
            continue

        if source_path.suffix.lower() not in EXCEL_SUFFIXES:
            continue

        saved_paths.append(str(save_to_temp(source_path)))

    if not saved_paths:
        return {"message": "No valid Excel files were saved.", "saved_paths": []}

    return {
        "message": f"Saved {len(saved_paths)} Excel file(s) to {TEMP_DIR.resolve()}",
        "saved_paths": saved_paths,
    }


def package_output(output_folder: Path) -> Path:
    """
    Compresses the entire output directory into a ZIP archive and returns the archive path.
    """
    output_folder = output_folder.resolve()
    output_folder.parent.mkdir(parents=True, exist_ok=True)

    zip_base = output_folder.parent / output_folder.name  # without suffix
    zip_path = zip_base.with_suffix(".zip")

    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(
        base_name=str(zip_base),
        format="zip",
        root_dir=output_folder,
    )
    return zip_path


async def run_extraction(files):
    if Path("temp_data").is_dir():
        shutil.rmtree("temp_data")

    upload_info = get_list_path(files)
    if not upload_info["saved_paths"]:
        # No valid files — hide download button
        # return upload_info, gr.update(value=None, visible=False)
        failure_log = json.dumps(upload_info, indent=2)
        return (
            f"**Upload failed**\n\n```json\n{failure_log}\n```",
            gr.update(value=None, visible=False),
            gr.update(interactive=True),
        )

    timestamp = time.strftime("%Y%m%d_%H%M%S")
    output_folder = DOWNLOADS_DIR / timestamp
    output_folder.mkdir(parents=True, exist_ok=True)

    # Clean up old data
    current_date = int(time.strftime("%Y%m%d"))
    for subfolder in DOWNLOADS_DIR.iterdir():
        if subfolder.is_dir():
            try:
                folder_date = int(subfolder.name.split("_")[0])
                if folder_date < current_date - 7:  # older than 7 days
                    shutil.rmtree(subfolder)
            except ValueError:
                continue

    vv = await extract_data(upload_info["saved_paths"], output_folder=output_folder)
    if not vv:
        # upload_info["message"] = "No Material number found in the Excel. :("
        # return upload_info, gr.update(value=None, visible=False)
        upload_info["message"] = "No Material number found in the Excel."
        failure_log = json.dumps(upload_info, indent=2)
        return (
            f"**Extraction failed** -- No Material number found in the Excel.\n\n```json\n{failure_log}\n```",
            gr.update(value=None, visible=False),
            gr.update(interactive=True),
        )

    generate_reports(output_folder)

    # response = {
    #     **upload_info,
    #     "output_folder": str(output_folder.resolve()),
    # }

    response = "# ✅ **Your file is ready! :)**"

    summary_dir = output_folder / "summary"
    zip_path = package_output(summary_dir)

    if Path("temp_data").is_dir():
        shutil.rmtree("temp_data")

    return response, gr.update(
        value=str(zip_path),
        visible=True,
        label="Download Reports (ZIP)",
    ), gr.update(interactive=True),


with gr.Blocks() as demo:
    gr.Markdown("# Extract Material Data from Amgreeting")
    gr.Markdown(
        "Select one or more `.xlsx` / `.xls` files, then press **Upload** to process them."
    )

    with gr.Row():
        file_input = gr.Files(
            label="Select Excel workbooks",
            file_types=[".xlsx", ".xls"],
            type="filepath",
        )

    # output = gr.JSON(label="Upload result")
    output = gr.Markdown(label="Upload result")
    upload_button = gr.Button("Upload")
    download_button = gr.DownloadButton("Download Reports", visible=False)

    # upload_button.click(
    #     fn=run_extraction,
    #     inputs=file_input,
    #     outputs=[output, download_button],
    # )

    upload_button.click(
        fn=lambda: (
            "⏳ Processing your files… please wait.",
            gr.update(value=None, visible=False),
            gr.update(interactive=False),
        ),
        inputs=None,
        outputs=[output, download_button, upload_button],
    ).then(
        fn=run_extraction,
        inputs=file_input,
        outputs=[output, download_button, upload_button],
    )

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
