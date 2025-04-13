import os
import requests
from rich.progress import Progress, DownloadColumn, TransferSpeedColumn, TimeRemainingColumn
from rich.console import Console

console = Console()

def download_file(url: str, dest_path: str):
    """Download a file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with Progress(
        "[progress.description]{task.description}",
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        
        task = progress.add_task("[cyan]Downloading model...", total=total_size)
        
        with open(dest_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    size = f.write(chunk)
                    progress.update(task, advance=size)

def main():
    # Create models directory if it doesn't exist
    os.makedirs('models', exist_ok=True)
    
    # Model details
    model_name = "mistral-7b-instruct-v0.2.Q4_K_M.gguf"
    model_url = f"https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/{model_name}"
    dest_path = os.path.join('models', model_name)
    
    if os.path.exists(dest_path):
        console.print(f"[yellow]Model already exists at {dest_path}[/yellow]")
        return
    
    console.print("[green]Starting download of Mistral-7B-Instruct model (Q4_K_M version)[/green]")
    console.print(f"[cyan]This model is about 4.37GB in size[/cyan]")
    
    try:
        download_file(model_url, dest_path)
        console.print(f"[green]✓ Model downloaded successfully to {dest_path}[/green]")
    except Exception as e:
        console.print(f"[red]Error downloading model: {str(e)}[/red]")

if __name__ == "__main__":
    main() 