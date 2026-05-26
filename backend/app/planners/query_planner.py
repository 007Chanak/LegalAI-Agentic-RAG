def plan_query(user_query: str):

    query = user_query.lower()

    retrieval_queries = []

    # -------------------------------
    # COMPARISON QUERIES
    # -------------------------------

    if "compare" in query:

        retrieval_queries.extend([

            f"{user_query} summary",

            f"{user_query} differences",

            f"{user_query} important clauses",

            f"{user_query} judgement",

        ])

    # -------------------------------
    # SUMMARY QUERIES
    # -------------------------------

    elif "summarize" in query:

        retrieval_queries.extend([

            f"{user_query} main points",

            f"{user_query} legal findings",

            f"{user_query} final outcome",

        ])

    # -------------------------------
    # DEFAULT
    # -------------------------------

    else:

        retrieval_queries.append(
            user_query
        )

    return retrieval_queries