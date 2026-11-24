
def build_prompt(concept_data, validation_feedback=None):
    concept_name = concept_data["concept"]
    subject = concept_data["subject"]
    description = concept_data["description"]

    prompt = f"""
You are an expert educational science diagram designer.

Create one accurate, visually clear, animated SVG diagram.

CONCEPT: {concept_name}
SUBJECT: {subject}
EDUCATIONAL DESCRIPTION: {description}

SVG REQUIREMENTS:

1. Return ONLY valid SVG markup.
2. Use an SVG viewBox of "0 0 800 600".
3. Use width="800" and height="600".
4. Include a descriptive SVG title using a <title> element.
5. Include at least 3 meaningful visible text labels.
6. Make the diagram educationally accurate.
7. Use clear shapes, lines and arrows where appropriate.
8. Keep all elements inside the viewBox boundaries.
9. Use readable text sizes and avoid overlapping labels.
10. Include at least one visible animation.
11. Use simple SVG elements: rect, circle, ellipse, line,
    polygon, polyline and text.
12. Do not use transforms, external images, external fonts,
    JavaScript, scripts or external resources.
13. Do not use SVG path elements.
14. Use simple coordinates rather than complicated geometry.
15. Make the design attractive and suitable for students.

ANIMATION:
Use an SVG-compatible CSS @keyframes animation inside
the SVG to animate at least one visible element.
The animation should help explain the concept.

OUTPUT:
Return a complete SVG document beginning with <svg>
and ending with </svg>.
Do not include Markdown code fences or explanations.
"""

    if validation_feedback:
        prompt += f"""

IMPORTANT: Your previous SVG failed validation.

Fix the following problems:
{validation_feedback}

Return a completely corrected SVG.
"""

    return prompt.strip()
