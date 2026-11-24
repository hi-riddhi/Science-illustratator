# Science Diagram Maker

An AI-powered web application that generates educational science diagrams as animated SVGs. The application uses AI to create diagrams, validates the generated SVG markup, and allows reviewers to approve or reject each result with notes.

## 1. Project Overview

The Science Diagram Maker generates diagrams for five educational concepts:

1. Pythagoras' theorem
2. Parts of a circle
3. Series circuit
4. Photosynthesis
5. States of matter

Each generated diagram is checked for SVG validity, required labels, animation, drawing boundaries and basic security restrictions.

## 2. Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML, CSS, JavaScript
- **AI providers:** Google Gemini and Groq
- **AI model currently configured:** `openai/gpt-oss-120b` through Groq
- **SVG validation:** Python XML parsing and custom validation rules
- **Data storage:** JSON (`results.json`)

## 3. Project Structure

```text
ProjectSVG2/
│
├── app.py
├── generator.py
├── validator.py
├── concepts.py
├── prompts.py
├── run_gen.py
├── results.json
│
├── templates/
│   └── index.html
│
├── static/
│   ├── style.css
│   └── script.js
│
├── requirements.txt
├── README.md
├── .env
└── .gitignore
```

## 4. Features

### AI Diagram Generation
- Generates SVG diagrams using a selected AI provider.
- Supports Gemini and Groq through an environment configuration.
- Uses concept-specific prompts.
- Requests one correction attempt if SVG validation fails.

### SVG Validation
- Checks whether the SVG is valid XML.
- Checks for a valid SVG root and viewBox.
- Checks drawing boundaries.
- Requires a title and at least three text labels.
- Checks for animation.
- Applies custom security and unsupported-element checks.

### Reviewer Workflow
- Displays generated diagrams.
- Allows reviewers to approve or reject diagrams.
- Supports reviewer notes.
- Saves review decisions in `results.json`.

### Usage Tracking
Records:
- AI provider and model
- Input tokens
- Output tokens
- Estimated API cost
- API retries
- Validation retries
- Validation results

## 5. Installation and Setup

### Prerequisites

- Python 3.10 or later
- pip
- An API key for the selected AI provider

### Create a virtual environment

```powershell
python -m venv venv
```

Activate it on Windows:

```powershell
venv\Scripts\activate
```

### Install dependencies

```powershell
pip install -r requirements.txt
```

### Configure environment variables

Create a `.env` file in the project root.

For Groq:

```env
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-120b
```

For Gemini:

```env
AI_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=your_gemini_model
```

Never commit `.env` or expose API keys publicly.

## 6. Run the Application

Start Flask:

```powershell
python app.py
```

Open the application:

```text
http://127.0.0.1:5000
```

The application provides endpoints:

| Endpoint | Purpose |
|---|---|
| `/` | Main application |
| `/api/concepts` | Lists the five concepts |
| `/api/results` | Returns saved results |
| `/api/generate/<id>` | Generates one diagram |
| `/api/review/<id>` | Saves reviewer decisions |

## 7. Run Batch Generation

To generate concepts through the Python batch workflow:

```powershell
python run_gen.py
```

Previously generated successful results are skipped by the batch workflow.

## 8. Results and Data Storage

Generated diagrams and their metadata are stored in:

```text
results.json
```

The file contains SVG markup, validation results, model information, token usage, estimated cost, retry counts and reviewer decisions.

Results are stored locally in JSON format.

## 9. Testing Performed

### Completed checks

- Python syntax compilation.
- Python module import verification.
- Results JSON loading.
- Flask homepage response.
- Concepts API response.
- Results API response.
- Five concepts returned successfully.
- Frontend loading.
- Groq provider configuration.
- One live Groq diagram generation.
- SVG validation passed for the generated Pythagoras diagram.
- Reviewer approval/rejection workflow tested.

### Remaining verification

- Generate and validate the other four concepts.
- Complete final cross-browser and UI checks.
- Verify reviewer notes persist after refresh.
- Test deployment and production configuration.

## 10. Known Limitations

- AI-generated SVGs may require correction if they fail validation.
- Free API tiers have rate limits and availability restrictions.
- SVG validation checks geometry and markup but cannot guarantee perfect visual or scientific accuracy.
- JSON storage is suitable for this assignment but is not intended for concurrent multi-user production use.
- Local JSON data must be migrated to persistent storage for a reliable hosted deployment.

## 11. Future Improvements

With additional development time, the application could include:

- Database-backed result storage.
- User authentication and reviewer roles.
- More detailed scientific accuracy checks.
- Additional educational concepts.
- More robust SVG rendering and sanitization.
- Deployment monitoring and error logging.
- Automated tests for backend and frontend workflows.

## 12. Security

- API keys are stored in `.env`.
- `.env` and the virtual environment are excluded through `.gitignore`.
- API keys must be configured as deployment environment variables.
- Never expose provider credentials in frontend JavaScript.

---

**Project:** Science Diagram Maker  
**Purpose:** AI-assisted educational diagram generation and review  
**Backend:** Flask  
**AI providers:** Gemini and Groq