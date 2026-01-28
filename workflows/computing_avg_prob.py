from polymarket_prediction_accuracy.scr.poly_prob_model.compute_poly_prob_accuracy import ComputePolyProbAccuracy


def main(
        num_markets: int,
        input_labels: list,
        horizon: str
) -> float:
    poly_prob_accuracy = ComputePolyProbAccuracy(
        num_markets=num_markets,
        horizon=horizon,
        labels=input_labels
    )

    output = poly_prob_accuracy.run()

    return output


if __name__ == "__main__":
    main(
        num_markets=5,  # int: num markets per tag
        input_labels=["investing"],  # specific tags
        horizon="1w"  # choose from 1w, 1m
    )
