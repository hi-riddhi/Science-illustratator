
import os
import re
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors
from groq import Groq

from prompts import build_prompt
from validator import validate_svg, all_checks_passed


load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "gemini").strip().lower()

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()

GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b").strip()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()

INPUT_PRICE = float(os.getenv("INPUT_PRICE_PER_MILLION", "0"))
OUTPUT_PRICE = float(os.getenv("OUTPUT_PRICE_PER_MILLION", "0"))


def extract_svg(response_text):
    if not response_text:
        raise ValueError("The AI provider returned an empty response.")

    text = response_text.strip()

    text = re.sub(
        r"^```(?:svg|xml)?\s*",
        "",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"\s*```$", "", text)

    start = text.find("<svg")
    end = text.rfind("</svg>")

    if start == -1 or end == -1:
        raise ValueError("The AI response did not contain complete SVG markup.")

    return text[start:end + len("</svg>")]


def estimate_cost(input_tokens, output_tokens):
    if AI_PROVIDER == "groq":
        # Groq free-tier usage is not charged per token.
        return 0.0

    input_cost = (input_tokens / 1_000_000) * INPUT_PRICE
    output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE

    return round(input_cost + output_cost, 8)


def is_daily_quota_error(message):
    message = message.lower()

    return (
        "daily quota" in message
        or "per day" in message
        or "requests per day" in message
    )


def call_gemini(prompt):
    if not GEMINI_API_KEY or not GEMINI_MODEL:
        raise RuntimeError(
            "Gemini configuration is missing from the .env file."
        )

    client = genai.Client(api_key=GEMINI_API_KEY)

    retry_count = 0
    wait_times = [10, 30, 60]

    while True:
        try:
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt
            )

            usage = response.usage_metadata

            input_tokens = getattr(
                usage, "prompt_token_count", 0
            ) or 0

            output_tokens = getattr(
                usage, "candidates_token_count", 0
            ) or 0

            svg = extract_svg(response.text)

            return (
                svg,
                input_tokens,
                output_tokens,
                retry_count,
                GEMINI_MODEL
            )

        except errors.APIError as error:
            message = str(error)
            code = str(getattr(error, "code", ""))

            if is_daily_quota_error(message):
                raise RuntimeError(
                    "Gemini daily quota reached. Stopping generation."
                ) from error

            if code not in ("429", "503"):
                raise

            if retry_count >= len(wait_times):
                raise RuntimeError(
                    "Gemini temporary service error. Retry limit reached."
                ) from error

            wait = wait_times[retry_count]
            retry_count += 1

            print(f"Gemini temporary error. Waiting {wait} seconds...")
            time.sleep(wait)


def call_groq(prompt):
    if not GROQ_API_KEY or not GROQ_MODEL:
        raise RuntimeError(
            "Groq configuration is missing from the .env file."
        )

    # Disable SDK retries so our application controls the retry limit.
    client = Groq(
        api_key=GROQ_API_KEY,
        max_retries=0
    )

    retry_count = 0
    wait_times = [10, 30, 60]

    while True:
        try:
            response = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an educational SVG diagram generator. "
                            "Return only complete SVG markup."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.2,
                max_completion_tokens=6000
            )

            usage = response.usage

            input_tokens = getattr(
                usage, "prompt_tokens", 0
            ) or 0

            output_tokens = getattr(
                usage, "completion_tokens", 0
            ) or 0

            svg = extract_svg(
                response.choices[0].message.content
            )

            return (
                svg,
                input_tokens,
                output_tokens,
                retry_count,
                GROQ_MODEL
            )

        except Exception as error:
            from groq import APIStatusError

            if not isinstance(error, APIStatusError):
                raise

            code = getattr(error, "status_code", 0)
            message = str(error)

            if is_daily_quota_error(message):
                raise RuntimeError(
                    "Groq daily quota reached. Stopping generation."
                ) from error

            if code not in (429, 503):
                raise

            if retry_count >= len(wait_times):
                raise RuntimeError(
                    "Groq temporary service error. Retry limit reached."
                ) from error

            wait = wait_times[retry_count]
            retry_count += 1

            print(f"Groq temporary error. Waiting {wait} seconds...")
            time.sleep(wait)


def call_provider(prompt):
    if AI_PROVIDER == "gemini":
        return call_gemini(prompt)

    if AI_PROVIDER == "groq":
        return call_groq(prompt)

    raise RuntimeError(
        "Invalid AI_PROVIDER. Choose 'gemini' or 'groq' in .env."
    )


def generate_diagram(concept_data):
    total_input_tokens = 0
    total_output_tokens = 0
    total_api_retries = 0
    validation_retries = 0

    validation_feedback = None
    checks = {}
    svg = None
    passed = False
    model_used = ""

    for attempt in range(2):

        prompt = build_prompt(
            concept_data,
            validation_feedback
        )

        (
            svg,
            input_tokens,
            output_tokens,
            api_retries,
            model_used
        ) = call_provider(prompt)

        total_input_tokens += input_tokens
        total_output_tokens += output_tokens
        total_api_retries += api_retries

        checks = validate_svg(svg)
        passed = all_checks_passed(checks)

        if passed:
            break

        if attempt == 0:
            validation_retries += 1

            validation_feedback = (
                "The previous SVG failed these validation checks. "
                "Correct the SVG and return the complete corrected SVG:\n"
                + str(checks)
            )

            print("SVG validation failed. Requesting one correction.")

    total_cost = estimate_cost(
        total_input_tokens,
        total_output_tokens
    )

    return {
        "concept": concept_data["concept"],
        "subject": concept_data["subject"],
        "model": model_used,
        "provider": AI_PROVIDER,
        "svg": svg,
        "checks": checks,
        "passed": passed,
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "estimated_cost_usd": total_cost,
        "api_retries": total_api_retries,
        "validation_retries": validation_retries,
        "retries": total_api_retries + validation_retries
    }
