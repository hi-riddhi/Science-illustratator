# AI-Powered Science Diagram Maker

An AI-powered Python Flask web application that generates animated science diagrams as SVGs, validates them automatically, and provides an interactive reviewer dashboard to approve or reject the generated diagrams.

## 1. Technology Stack

| Component | Technology |
|---|---|
| Backend | Python 3, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Diagram generation | SVG, CSS animations |
| AI provider | Groq API – GPT-OSS 120B |
| Additional AI integration | Google Gemini API |
| Validation | XML parsing and custom SVG validation |
| Data storage | JSON (`results.json`) |
| API communication | REST APIs |
| Production server | Gunicorn |
| Deployment | Render |
| Version control | Git and GitHub |

## 2. Features

- Generates animated SVG science diagrams using AI.
- Supports five predefined science concepts.
- Validates SVG XML structure and drawing boundaries.
- Checks for a title, at least three text labels, and animation.
- Performs custom security checks on generated SVG content.
- Retries generation once when SVG validation fails, using validation feedback.
- Handles temporary API errors (429 and 503) with retry logic.
- Tracks model name, token usage, estimated cost, and retries.
- Displays validation results and diagrams in a web dashboard.
- Allows reviewers to approve or reject diagrams with notes.
- Saves generation results and review decisions in `results.json`.
- Allows individual concept generation through the interface.

## 3. Science Concepts

1. Pythagoras' Theorem
2. Parts of a Circle
3. Series Circuit
4. Photosynthesis
5. States of Matter

## 4. Run Locally

### Prerequisites

- Python 3.10 or later
- Git
- A Groq API key

### Step 1: Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/science-diagram-maker.git
cd science-diagram-maker
```

### Step 2: Create a virtual environment

Windows:

```powershell
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure environment variables

Create a `.env` file in the project root:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b

GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model
```

Only the API key for the selected provider is required.

**Security:** Never commit `.env` or expose API keys in the repository.

### Step 5: Run the application

```bash
python app.py
```

Open the application in your browser:

```text
http://127.0.0.1:5000
```

## 5. Results

The following table reflects the confirmed testing status. Exact token, cost, and retry figures should be taken from the corresponding records in `results.json`.

| Concept | Result | Estimated Cost (USD) | Retries |
|---|---|---:|---:|
| Pythagoras' Theorem | PASS | See results.json | See results.json |
| Parts of a Circle | PASS | — | — |
| Series Circuit | PASS | — | — |
| Photosynthesis | PASS | — | — |
| States of Matter | PASS | — | — |

The application records generation metadata, including provider, model, token usage, estimated cost, API retries, validation retries, and individual validation checks.

## 6. Issues Encountered and Fixes

| Issue | Resolution |
|---|---|
| Gemini API returned HTTP 503 due to temporary high demand. | Added retry handling and integrated Groq as an alternative AI provider. |
| Provider configuration was not loading as expected. | Corrected environment variable configuration and provider selection. |
| Empty `results.json` caused a JSON decoding error. | Initialized the file with an empty JSON array and added safer loading logic. |
| Python syntax error in the Flask application. | Corrected the route definition and verified Python compilation. |
| Frontend JavaScript errors during integration. | Replaced the affected JavaScript with a clean implementation and verified the application endpoints. |
| API generation could consume unnecessary credits during testing. | Used offline checks and a controlled single-concept generation test before proceeding. |

## 7. AI Tools Used

### Groq – GPT-OSS 120B
Used as the primary AI generation provider to generate SVG science diagrams from structured concept prompts.

### Google Gemini
Integrated as an additional AI provider and used during initial API integration and generation testing.

AI-generated SVG output is treated as untrusted input and passed through the application's validation checks before being presented for review.

## 8. What I Would Do With One More Day

With another day of development, I would focus on:

1. **Improve SVG validation:** Add more robust geometric boundary checks, text visibility checks, and animation validation.
2.**Expand automated testing:** Add unit tests for validation, API error handling, and reviewer workflows.
3.**Improve persistence:** Replace local JSON storage with a database such as PostgreSQL for reliable deployed data persistence.
5. **Improve the reviewer experience:** Add clearer validation feedback, generation history, and better error reporting.
6. **Optimize AI usage:** Compare model output quality, token usage, response time, and generation costs.

## 9. Project Structure

```text
science-diagram-maker/
│
├── app.py
├── generator.py
├── validator.py
├── prompts.py
├── concepts.py
├── run_gen.py
├── results.json
├── requirements.txt
├── .env
├── .gitignore
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    └── script.js
```

## 10. Deployment

The application is deployed as a Python Web Service on Render.

- Build command: `pip install -r requirements.txt`
- Start command: `gunicorn app:app`
- AI credentials are configured through Render environment variables.


---

**Project:** AI-Powered Science Diagram Maker  
**Backend:** Python / Flask  
**AI Generation:** Groq GPT-OSS 120B  
**Deployment:** Render