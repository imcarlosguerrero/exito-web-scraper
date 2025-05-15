import json
from pathlib import Path
import sys
from typing import Dict, List, Optional
import logging
import subprocess

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def load_items_from_json(file_path: str) -> List[Dict]:
    """Load the items data from the input JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Failed to load items file: {e}")
        sys.exit(1)


def find_result_file(
    city: str, item_name: str, base_dir: str = "results"
) -> Optional[str]:
    """
    Check if a result file exists for the item in any subfolder of the city directory.
    Returns the file path if found, None otherwise.
    """
    city_dir = Path(base_dir) / city

    # If city directory doesn't exist, return None
    if not city_dir.exists() or not city_dir.is_dir():
        return None

    # Check all subdirectories in the city directory
    for subdir in [d for d in city_dir.iterdir() if d.is_dir()]:
        file_path = subdir / f"{item_name}.json"
        if file_path.exists():
            return str(file_path)

    return None


def validate_results(items_file: str, results_dir: str = "results") -> Dict:
    """
    Validate that each item in the items file has a corresponding result file.
    Returns a report of the validation results.
    """
    items = load_items_from_json(items_file)

    total_items = len(items)
    found_files = 0
    missing_files = []

    logging.info(f"Starting validation of {total_items} items...")

    for item in items:
        city = item.get("city")
        sipsa_name = item.get("sipsa_name")
        exito_name = item.get("exito_name")

        if not city:
            logging.warning(f"Item missing city: {item}")
            missing_files.append({"item": item, "reason": "Missing city information"})
            continue

        # Try with both sipsa_name and exito_name
        item_names = [name for name in [sipsa_name, exito_name] if name]
        found = False

        for name in item_names:
            file_path = find_result_file(city, name, results_dir)
            if file_path:
                found = True
                found_files += 1
                break

        if not found:
            missing_files.append(
                {
                    "item": item,
                    "reason": f"No result file found in {results_dir}/{city}/*/[{' or '.join(item_names)}].json",
                }
            )

    return {
        "total_items": total_items,
        "found_files": found_files,
        "missing_count": len(missing_files),
        "missing_files": missing_files,
        "success_rate": found_files / total_items if total_items > 0 else 0,
    }


def print_report(report: Dict) -> None:
    """Print a human-readable report of the validation results."""
    print("\n============ VALIDATION REPORT ============")
    print(f"Total items: {report['total_items']}")
    print(f"Files found: {report['found_files']}")
    print(f"Files missing: {report['missing_count']}")
    print(f"Success rate: {report['success_rate'] * 100:.2f}%")

    if report["missing_files"]:
        print("\nMissing files:")
        for i, missing in enumerate(report["missing_files"], 1):
            item = missing["item"]
            print(f"\n{i}. Item:")
            print(f"   City: {item.get('city', 'N/A')}")
            print(f"   TCAC Code: {item.get('tcac_code', 'N/A')}")
            print(f"   SIPSA Name: {item.get('sipsa_name', 'N/A')}")
            print(f"   Exito Name: {item.get('exito_name', 'N/A')}")
            print(f"   Reason: {missing['reason']}")


def export_missing_to_json(
    report: Dict, output_file: str = "missing_items.json"
) -> int:
    """
    Export the list of missing items to a JSON file.
    Returns the number of missing items.
    """
    missing_items = [item["item"] for item in report["missing_files"]]

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(missing_items, f, indent=2, ensure_ascii=False)

    logging.info(f"Missing items exported to {output_file}")
    return len(missing_items)


def rescrape_missing_items(missing_items_file: str) -> bool:
    """
    Re-scrape missing items by calling run.py with the missing items file.
    """
    try:
        logging.info(f"Starting re-scraping process for missing items...")

        # Call run.py with the missing items file and skip cleaning
        result = subprocess.run(
            ["python", "run.py", "--items-file", missing_items_file, "--skip-clean"],
            check=True,
            capture_output=True,
            text=True,
        )

        logging.info("Re-scraping process completed")
        logging.info(result.stdout)

        return True

    except subprocess.CalledProcessError as e:
        logging.error(f"Re-scraping process failed: {e}")
        logging.error(f"STDOUT: {e.stdout}")
        logging.error(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        logging.error(f"Error during re-scraping: {e}")
        return False


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate web scraping results")
    parser.add_argument(
        "--items-file",
        "-i",
        default="data_processing/foods.json",
        help="Path to the JSON file with items data (default: data_processing/foods.json)",
    )
    parser.add_argument(
        "--results-dir",
        "-r",
        default="results",
        help="Path to the results directory (default: results)",
    )
    parser.add_argument(
        "--export-missing",
        "-e",
        action="store_true",
        help="Export missing items to JSON file",
    )
    parser.add_argument(
        "--output-file",
        "-o",
        default="missing_items.json",
        help="Output file for missing items (default: missing_items.json)",
    )
    parser.add_argument(
        "--rescrape",
        "-s",
        action="store_true",
        help="Re-scrape missing items",
    )

    args = parser.parse_args()

    report = validate_results(args.items_file, args.results_dir)
    print_report(report)

    if report["missing_files"]:
        missing_count = 0

        if args.export_missing or args.rescrape:
            missing_count = export_missing_to_json(report, args.output_file)

        if args.rescrape and missing_count > 0:
            logging.info(f"Re-scraping {missing_count} missing items...")
            success = rescrape_missing_items(args.output_file)

            if success:
                logging.info("Re-scraping completed successfully")
                # Re-validate after re-scraping
                new_report = validate_results(args.items_file, args.results_dir)
                print_report(new_report)
            else:
                logging.error("Re-scraping failed")


if __name__ == "__main__":
    main()
