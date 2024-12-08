import os

def upload_file(filepath):
    name = Path(filepath).name
    return [gr.UploadButton(visible=False), gr.DownloadButton(label=f"Download {name}", value=filepath, visible=True)]
