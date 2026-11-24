
import re
import xml.etree.ElementTree as ET


def get_tag(element):
    """Remove the SVG namespace from an element tag."""
    return element.tag.split("}")[-1]


def parse_number(value):
    """Convert an SVG numeric attribute into a float."""

    if value is None:
        raise ValueError("Missing coordinate")

    value = str(value).strip()

    if not re.fullmatch(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)", value):
        raise ValueError(f"Unsupported coordinate: {value}")

    return float(value)


def validate_svg(svg_code):
    """Validate SVG structure, boundaries, labels, animation and safety."""

    results = {
        "valid_svg": False,
        "viewbox_bounds": False,
        "title_and_labels": False,
        "animation": False,
        "custom_check": False
    }

    # CHECK 1: SVG must be valid XML.
    try:
        root = ET.fromstring(svg_code)

        if get_tag(root) != "svg":
            raise ValueError("Root element must be SVG.")

        results["valid_svg"] = True

    except (ET.ParseError, ValueError, AttributeError):
        return results

    # CHECK 2: ViewBox and drawing boundaries.
    bounds_pass = True

    try:
        viewbox = root.attrib.get("viewBox")

        if not viewbox:
            raise ValueError("Missing viewBox.")

        values = [
            parse_number(value)
            for value in viewbox.replace(",", " ").split()
        ]

        if len(values) != 4:
            raise ValueError("Invalid viewBox.")

        min_x, min_y, width, height = values

        if width <= 0 or height <= 0:
            raise ValueError("Invalid viewBox dimensions.")

        max_x = min_x + width
        max_y = min_y + height

        drawable_tags = {
            "rect", "circle", "ellipse",
            "line", "polygon", "polyline", "text"
        }

        allowed_non_drawing = {
            "svg", "g", "defs", "title", "desc",
            "style", "metadata", "animate",
            "animateTransform", "animateMotion",
            "set", "stop", "linearGradient",
            "radialGradient", "clipPath", "mask",
            "pattern", "filter", "feGaussianBlur"
        }

        for element in root.iter():
            tag = get_tag(element)

            if tag in allowed_non_drawing:
                continue

            if tag not in drawable_tags:
                raise ValueError(
                    f"Unsupported drawing element: {tag}"
                )

            if element.attrib.get("transform"):
                raise ValueError(
                    "Transform attributes are not supported by boundary checking."
                )

            if tag == "rect":
                x = parse_number(element.get("x", "0"))
                y = parse_number(element.get("y", "0"))
                w = parse_number(element.get("width"))
                h = parse_number(element.get("height"))

                if w < 0 or h < 0:
                    raise ValueError("Negative rectangle dimensions.")

                box = (x, y, x + w, y + h)

            elif tag == "circle":
                x = parse_number(element.get("cx"))
                y = parse_number(element.get("cy"))
                r = parse_number(element.get("r"))

                if r < 0:
                    raise ValueError("Negative circle radius.")

                box = (x - r, y - r, x + r, y + r)

            elif tag == "ellipse":
                x = parse_number(element.get("cx"))
                y = parse_number(element.get("cy"))
                rx = parse_number(element.get("rx"))
                ry = parse_number(element.get("ry"))

                if rx < 0 or ry < 0:
                    raise ValueError("Negative ellipse radius.")

                box = (x - rx, y - ry, x + rx, y + ry)

            elif tag == "line":
                x1 = parse_number(element.get("x1"))
                y1 = parse_number(element.get("y1"))
                x2 = parse_number(element.get("x2"))
                y2 = parse_number(element.get("y2"))

                box = (
                    min(x1, x2), min(y1, y2),
                    max(x1, x2), max(y1, y2)
                )

            elif tag in {"polygon", "polyline"}:
                numbers = [
                    float(number)
                    for number in re.findall(
                        r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)",
                        element.get("points", "")
                    )
                ]

                if len(numbers) < 4 or len(numbers) % 2:
                    raise ValueError("Invalid polygon points.")

                xs = numbers[0::2]
                ys = numbers[1::2]

                box = (min(xs), min(ys), max(xs), max(ys))

            elif tag == "text":
                x = parse_number(element.get("x", "0"))
                y = parse_number(element.get("y", "0"))

                # Checks the text anchor position, not glyph dimensions.
                box = (x, y, x, y)

            if (
                box[0] < min_x or
                box[1] < min_y or
                box[2] > max_x or
                box[3] > max_y
            ):
                raise ValueError(f"{tag} extends outside the viewBox.")

    except (ValueError, TypeError) as error:
        bounds_pass = False
        print("Boundary validation:", error)

    results["viewbox_bounds"] = bounds_pass

    # CHECK 3: Title and at least three text labels.
    title_found = any(
        get_tag(element) == "title"
        and (element.text or "").strip()
        for element in root.iter()
    )

    labels = [
        element for element in root.iter()
        if get_tag(element) == "text"
        and "".join(element.itertext()).strip()
    ]

    results["title_and_labels"] = (
        title_found and len(labels) >= 3
    )

    # CHECK 4: At least one animation.
    animation_found = any(
        get_tag(element) in {
            "animate", "animateTransform",
            "animateMotion", "set"
        }
        for element in root.iter()
    )

    style_content = "".join(
        element.text or ""
        for element in root.iter()
        if get_tag(element) == "style"
    )

    if re.search(r"@keyframes", style_content, re.IGNORECASE):
        animation_found = True

    results["animation"] = animation_found

    # CHECK 5: Custom security check.
    custom_pass = True

    for element in root.iter():
        tag = get_tag(element).lower()

        if tag in {"script", "foreignobject", "iframe", "object", "embed"}:
            custom_pass = False

        for attribute, value in element.attrib.items():
            attribute_name = attribute.split("}")[-1].lower()
            value_lower = value.strip().lower()

            # Reject event-handler attributes.
            if attribute_name.startswith("on"):
                custom_pass = False

            # Only allow local SVG fragment references.
            if attribute_name in {"href", "src"}:
                if value_lower and not value.startswith("#"):
                    custom_pass = False

            # Reject dangerous CSS and external URL references.
            if (
                "javascript:" in value_lower
                or "@import" in value_lower
                or re.search(r"url\s*\(", value_lower)
            ):
                custom_pass = False

    style_lower = style_content.lower()

    if (
        "javascript:" in style_lower
        or "@import" in style_lower
        or re.search(r"url\s*\(", style_lower)
    ):
        custom_pass = False

    results["custom_check"] = custom_pass

    return results


def all_checks_passed(results):
    """Return True only when every validation check passes."""
    required_checks = {
        "valid_svg",
        "viewbox_bounds",
        "title_and_labels",
        "animation",
        "custom_check"
    }

    return (
        required_checks.issubset(results.keys())
        and all(results[key] is True for key in required_checks)
    )
