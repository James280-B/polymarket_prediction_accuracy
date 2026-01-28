from polymarket_prediction_accuracy.scr.data_handler.poly_data_handler import PolyDataHandler

class ComputePolyProbAccuracy(PolyDataHandler):

    def __init__(
            self,
            num_markets: int | str,
            input_labels: list,
            resolution: int,
            horizon: str

    ) -> None:
        super().__init__(
            num_markets=num_markets,
            input_labels=input_labels,
            resolution=resolution,
            horizon=horizon
        )


    def run(self) -> float:
        data_set = super().build_data_set()
        avg_prob = data_set["price"].mean()

        return avg_prob

