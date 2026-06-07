"""
UUON Fractal Compare Module

Compares two fractal analysis results.

No renderer access.
No GLSL access.
Only mathematical fingerprints.
"""


def difference(a, b):

    try:
        return abs(
            float(a) - float(b)
        )

    except Exception:
        return None



def similarity_score(delta):

    if delta is None:
        return None


    score = 1.0 - delta


    if score < 0:
        score = 0


    return round(score, 4)



def compare_fractals(
    fractal_a: dict,
    fractal_b: dict
) -> dict:


    dimension_delta = difference(
        fractal_a.get("dimension"),
        fractal_b.get("dimension")
    )


    lacunarity_delta = difference(
        fractal_a.get("lacunarity"),
        fractal_b.get("lacunarity")
    )


    entropy_delta = difference(
        fractal_a.get("entropy"),
        fractal_b.get("entropy")
    )


    symmetry_delta = difference(
        fractal_a.get("symmetry"),
        fractal_b.get("symmetry")
    )


    available = [
        x for x in [

            dimension_delta,
            lacunarity_delta,
            entropy_delta,
            symmetry_delta

        ]

        if x is not None
    ]


    if available:

        average_difference = (
            sum(available)
            /
            len(available)
        )

    else:

        average_difference = None



    return {


        "similarity":

            similarity_score(
                average_difference
            ),


        "differences": {


            "dimension":
                dimension_delta,


            "lacunarity":
                lacunarity_delta,


            "entropy":
                entropy_delta,


            "symmetry":
                symmetry_delta

        },


        "interpretation":

            interpret_similarity(
                average_difference
            )

    }




def interpret_similarity(delta):


    if delta is None:

        return "insufficient_data"



    if delta < 0.05:

        return "near_identical_fractal_structure"



    if delta < 0.20:

        return "related_fractal_family"



    if delta < 0.50:

        return "different_variation"



    return "unrelated_structure"
