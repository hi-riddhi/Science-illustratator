
import json
from pathlib import Path

from concepts import CONCEPTS
from generator import generate_diagram


BASE_DIR = Path(__file__).resolve().parent
RESULTS_FILE = BASE_DIR / "results.json"


def load_results():
    """Load previously saved diagram results."""

    if not RESULTS_FILE.exists():
        return []

    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("results.json must contain a JSON list.")

        return data

    except (json.JSONDecodeError, ValueError) as error:
        raise RuntimeError(
            f"Could not read results.json: {error}"
        ) from error


def save_results(results):
    """Save diagram results to JSON."""

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4, ensure_ascii=False)


def update_result(results, new_result):
    """Update an existing concept or add a new result."""

    concept_name = new_result["concept"]

    for index, old_result in enumerate(results):
        if old_result.get("concept") == concept_name:

            # Preserve reviewer information during regeneration.
            new_result.setdefault(
                "review_status",
                old_result.get("review_status", "Pending")
            )
            new_result.setdefault(
                "review_note",
                old_result.get("review_note", "")
            )

            results[index] = new_result
            return

    new_result.setdefault("review_status", "Pending")
    new_result.setdefault("review_note", "")

    results.append(new_result)


def generate_and_save(concept_data):
    """Generate one diagram and save its result."""

    results = load_results()

    result = generate_diagram(concept_data)

    update_result(results, result)
    save_results(results)

    return result


def run_all():
    """Generate all five science diagrams."""

    results = load_results()

    for concept_data in CONCEPTS:
        concept_name = concept_data["concept"]

        already_passed = any(
            item.get("concept") == concept_name
            and item.get("passed") is True
            for item in results
        )

        if already_passed:
            print(f"SKIPPED: {concept_name} (already passed)")
            continue

        print(f"\nGenerating: {concept_name}")

        try:
            result = generate_and_save(concept_data)

            # Refresh local results after saving.
            results = load_results()

            if result.get("passed"):
                print(f"SUCCESS: {concept_name}")
            else:
                print(f"VALIDATION FAILED: {concept_name}")

        except Exception as error:
            print(f"GENERATION ERROR: {concept_name}")
            print(error)

            # Stop to avoid repeated API calls if service or quota fails.
            break

    print("\nGeneration workflow finished.")
    print(f"Saved results: {RESULTS_FILE}")


if __name__ == "__main__":
    run_all()
