def extract_clause_tool(
    context,
    clause_type
):

    extracted_sections = []

    clause_keywords = {

        "termination": [
            "termination",
            "terminate",
            "ended"
        ],

        "payment": [
            "payment",
            "fees",
            "amount"
        ],

        "liability": [
            "liability",
            "damages",
            "responsibility"
        ]
    }

    keywords = clause_keywords.get(
        clause_type,
        []
    )

    for line in context.split("\n"):

        lower_line = line.lower()

        if any(
            keyword in lower_line
            for keyword in keywords
        ):

            extracted_sections.append(
                line
            )

    return "\n".join(
        extracted_sections
    )