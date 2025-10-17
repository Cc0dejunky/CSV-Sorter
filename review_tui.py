import requests
import pandas as pd
from rich.console import Console
from rich.table import Table
import os
import subprocess
import atexit
import time

# --- Server Management ---
server_process = None

def start_server():
    """Starts the FastAPI server as a background process."""
    global server_process
    if server_process:
        print("Server is already running.")
        return
    try:
        # Correct path to the venv python executable
        python_executable = os.path.abspath(".venv/Scripts/python.exe")
        if not os.path.exists(python_executable):
            print(f"Error: Python executable not found at {python_executable}")
            print("Please ensure the virtual environment is set up correctly.")
            return

        # Command to run uvicorn
        command = [python_executable, "-m", "uvicorn", "main:app"]
        
        # Start the server as a background process
        server_process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("Starting FastAPI server in the background...")
    except Exception as e:
        print(f"Failed to start server: {e}")


def stop_server():
    """Stops the FastAPI server if it's running."""
    global server_process
    if server_process:
        print("Stopping FastAPI server...")
        server_process.terminate()
        try:
            # Wait for a short period for the process to terminate
            server_process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            # If it doesn't terminate, force kill it
            print("Server did not terminate gracefully, forcing shutdown.")
            server_process.kill()
        server_process = None
        print("Server stopped.")
    else:
        print("Server is not running.")

# Register the stop_server function to be called on script exit
atexit.register(stop_server)
# --- End Server Management ---


API_BASE_URL = "http://127.0.0.1:8000"  # The address of our FastAPI server

console = Console()


def export_products_to_html(products):
    """Saves the current list of products to an HTML file."""
    if not products:
        console.print("[yellow]No products to export.[/yellow]")
        return

    export_table = Table(
        title="Products Awaiting Review",
        header_style="bold magenta",
        show_lines=True,
    )
    export_table.add_column("ID", style="dim")
    export_table.add_column("Product Name")
    export_table.add_column("Raw Color")
    export_table.add_column("ML Prediction")

    for p in products:
        export_table.add_row(
            str(p["id"]),
            p["product_name"],
            p["raw_value"],
            p["ml_prediction"],
        )

    console.save_html("product_review_export.html", clear=False)
    console.print(f"[bold green]Exported table to product_review_export.html[/bold green]")


def handle_review_products():
    """
    Fetches products needing review from the server, displays them, and guides the
    user through the correction process.
    """
    console.print("[bold cyan]Fetching products for review...[/bold cyan]")
    try:
        # P-6: Call the new GET endpoint
        response = requests.get(f"{API_BASE_URL}/get_products_for_review")
        response.raise_for_status()  # Raise an exception for bad status codes
        products = response.json()

        if not products:
            console.print("[yellow]No products are currently in the review queue.[/yellow]")
            return

        while True:
            table = Table(
                title="Products Awaiting Review",
                header_style="bold magenta",
                show_lines=True,
            )
            table.add_column("ID", style="dim")
            table.add_column("Product Name")
            table.add_column("Raw Color")
            table.add_column("ML Prediction")

            valid_ids = [str(p["id"]) for p in products]
            for p in products:
                table.add_row(
                    str(p["id"]),
                    p["product_name"],
                    p["raw_value"],
                    p["ml_prediction"],
                )

            console.print(table)
            console.print(
                "Enter a Product ID to correct, 'e' to export, or 'q' to return to the main menu."
            )
            user_input = console.input("[bold]Product ID > [/bold]")

            if user_input.lower() == "q":
                break

            if user_input in valid_ids:
                product_id = int(user_input)
                # Find the full product details
                product = next((p for p in products if p["id"] == product_id), None)
                if product:
                    get_and_submit_correction(product)
                    # Refresh the list after a correction
                    console.print(
                        "[bold cyan]Refreshing review queue...[/bold cyan]"
                    )
                    response = requests.get(f"{API_BASE_URL}/get_products_for_review")
                    response.raise_for_status()
                    products = response.json()
                    if not products:
                        console.print(
                            "[yellow]Review queue is now empty.[/yellow]"
                        )
                        break
                else:
                    console.print("[red]Error: Could not find product details.[/red]")
            elif user_input.lower() == 'e':
                export_products_to_html(products)
            else:
                console.print("[red]Invalid ID. Please try again.[/red]")

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error: Could not connect to the server: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred: {e}[/bold red]")


def get_and_submit_correction(product):
    """
    Handles getting the user's correction for a single product and submitting it.
    """
    console.print(f"Correcting product: [bold]{product['product_name']}[/bold]")
    console.print(f"  - Raw Value: [yellow]{product['raw_value']}[/yellow]")
    console.print(f"  - ML Prediction: [cyan]{product['ml_prediction']}[/cyan]")

    human_correction = console.input("[bold]Enter the correct normalized value > [/bold]")

    # P-7: Prepare the feedback payload
    feedback_payload = {
        "product_id": product["id"],
        "raw_value": product["raw_value"],
        "ml_prediction": product["ml_prediction"],
        "human_correction": human_correction,
    }

    try:
        # P-7: POST the correction to the server
        response = requests.post(
            f"{API_BASE_URL}/submit_feedback", json=feedback_payload
        )

        # The server returns a 201 on success, but requests.raise_for_status()
        # only checks for >=400. We handle the success message based on the detail.
        if response.status_code == 201:
            console.print(
                f"[bold green]Success:[/bold green] {response.json().get('detail')}"
            )
        else:
            # This will catch 4xx and 5xx errors
            response.raise_for_status()

    except requests.exceptions.RequestException as e:
        # Try to get a more specific error from the server response
        error_detail = "No response from server."
        if e.response:
            error_detail = e.response.json().get("detail", e.response.text)
        console.print(f"[bold red]Error submitting feedback: {error_detail}[/bold red]")


def handle_csv_upload():
    """
    Manages the CSV upload process, including file validation and sending data
    to the server.
    """
    console.print("[bold cyan]Manual CSV Upload[/bold cyan]")
    # file_path = console.input(
    #     "[bold]Enter the absolute path to your CSV file > [/bold]"
    # )
    file_path = "C:\\Users\\C3rb3ru5\\Desktop\\CSV-Sorter\\AI_Project_Root\\data\\raw\\product.csv"


    if not os.path.exists(file_path):
        console.print(f"[red]Error: The file '{file_path}' does not exist.[/red]")
        return

    try:
        df = pd.read_csv(file_path)
        
        # Create a mapping from lowercase column names to original column names
        lower_to_original_cols = {col.lower(): col for col in df.columns}

        required_lower_cols = {"handle", "title"}
        if not required_lower_cols.issubset(lower_to_original_cols.keys()):
            console.print(
                f"[red]Error: CSV must contain the columns: {', '.join(required_lower_cols)}[/red]"
            )
            return

        # Create a new DataFrame with the correct column names
        new_df = pd.DataFrame()
        new_df['handle'] = df[lower_to_original_cols['handle']]
        new_df['product_name'] = df[lower_to_original_cols['title']]
        
        if 'raw_color' in lower_to_original_cols:
            new_df['raw_color'] = df[lower_to_original_cols['raw_color']]
        else:
            new_df['raw_color'] = None

        products_to_upload = new_df.to_dict(orient="records")
        upload_payload = {"products": products_to_upload}

        console.print(f"Found {len(products_to_upload)} products. Uploading to server...")

        response = requests.post(
            f"{API_BASE_URL}/bulk_stage_data", json=upload_payload
        )
        response.raise_for_status()

        response_data = response.json()
        console.print(
            f"[bold green]Success:[/bold green] {response_data.get('message')}"
        )

    except pd.errors.EmptyDataError:
        console.print(f"[red]Error: The CSV file '{file_path}' is empty.[/red]")
    except Exception as e:
        console.print(f"[bold red]An error occurred during the upload: {e}[/bold red]")


def trigger_model_retraining():
    """
    Sends a request to the server to reload the ML model.
    """
    console.print("[bold cyan]Triggering model retraining...[/bold cyan]")
    try:
        # P-9: Call the reload_model endpoint
        response = requests.post(f"{API_BASE_URL}/reload_model")
        response.raise_for_status()
        console.print(
            f"[bold green]Success:[/bold green] {response.json().get('message')}"
        )
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Error triggering retraining: {e}[/bold red]")


def main_menu():
    """
    The main user interface loop for the TUI.
    """
    while True:
        console.print("\n" + "=" * 40)
        console.print("[bold yellow]      Product Normalization TUI[/bold yellow]")
        console.print("=" * 40)
        console.print("  [1] Start Server")
        console.print("  [2] Review Products in Queue (P-6)")
        console.print("  [3] Upload a CSV for Staging (P-11)")
        console.print("  [4] Trigger Model Retraining (P-9)")
        console.print("  [5] Stop Server")
        console.print("  [q] Quit")
        console.print("-" * 40)

        choice = console.input("[bold]Choose an option > [/bold]")

        if choice == "1":
            start_server()
            time.sleep(3) # Give the server a moment to start
        elif choice == "2":
            handle_review_products()
        elif choice == "3":
            handle_csv_upload()
        elif choice == "4":
            trigger_model_retraining()
        elif choice == "5":
            stop_server()
        elif choice.lower() == "q":
            console.print("[bold]Exiting. Goodbye![/bold]")
            break
        else:
            console.print("[red]Invalid option. Please try again.[/red]")


if __name__ == "__main__":
    main_menu()