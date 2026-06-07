from modules.compare import compare_fractals



def test_compare_fractals():


    first = {

        "dimension": 1.72,

        "lacunarity": .45,

        "entropy": .88,

        "symmetry": .62

    }


    second = {

        "dimension": 1.75,

        "lacunarity": .50,

        "entropy": .84,

        "symmetry": .60

    }


    result = compare_fractals(
        first,
        second
    )


    assert result["similarity"] > .9


    assert (
        result["interpretation"]
        ==
        "near_identical_fractal_structure"
    )
