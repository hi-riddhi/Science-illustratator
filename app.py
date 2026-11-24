
from flask import Flask, render_template, jsonify, request

from concepts import CONCEPTS
from run_gen import load_results, generate_and_save


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/concepts", methods=["GET"])
def get_concepts():
    return jsonify(CONCEPTS)


@app.route("/api/results", methods=["GET"])
def get_results():
    try:
        return jsonify(load_results())
    except Exception as error:
        app.logger.exception("Could not load results")
        return jsonify({"error": str(error)}), 500


@app.route("/api/generate/<int:concept_id>", methods=["POST"])
def generate_one(concept_id):

    concept = next(
        (item for item in CONCEPTS if item["id"] == concept_id),
        None
    )

    if concept is None:
        return jsonify({"error": "Concept not found."}), 404

    try:
        # Shared generation and saving workflow.
        result = generate_and_save(concept)

        return jsonify(result)

    except Exception as error:
        app.logger.exception("Diagram generation failed")

        return jsonify({
            "error": str(error)
        }), 500


@app.route("/api/review/<int:concept_id>", methods=["POST"])
def review_one(concept_id):

    data = request.get_json(silent=True) or {}

    status = data.get("status")
    note = data.get("note", "")

    if status not in ("Approved", "Rejected"):
        return jsonify({"error": "Invalid review status."}), 400

    concept = next(
        (item for item in CONCEPTS if item["id"] == concept_id),
        None
    )

    if concept is None:
        return jsonify({"error": "Concept not found."}), 404

    try:
        results = load_results()

        for result in results:
            if result.get("concept") == concept["concept"]:

                if not result.get("svg"):
                    return jsonify({
                        "error": "Generate this diagram before reviewing."
                    }), 404

                result["review_status"] = status
                result["review_note"] = note

                from run_gen import save_results
                save_results(results)

                return jsonify({
                    "message": "Review saved.",
                    "result": result
                })

        return jsonify({
            "error": "Generate this diagram before reviewing."
        }), 404

    except Exception as error:
        app.logger.exception("Review saving failed")
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(debug=True)
