from modules.signature import create_signature


def test_signature_creation():

    metrics = {

        "dimension": 1.73423,

        "lacunarity": 0.4219,

        "entropy": 0.8831,

        "symmetry": 0.52

    }


    result = create_signature(metrics)


    assert result["signature"].startswith(
        "UFS1"
    )


    assert result["version"] == "UFS1"
