import numpy as np
import pandas as pd


class Simulate:
    def __init__(self):
        self.poor_performance = {
            "6": 3,
            "5": 4,
            "4": 5,
            "3": 6,
            "2": 7,
            "1": 8,
        }

    def run_simulation(self, data):
        race_class = str(data[data["data_type"] == "today"]["race_class"].iloc[0])
        padded_df = self._simulate_padding_horse_performance(data, race_class)
        results = self._run_simulation(padded_df, race_class)
        results_odds = (
            results[["simulated_price"]]
            .reset_index()
            .rename(columns={"index": "horse_name"})
        )
        data_with_odds = pd.merge(data, results_odds, on="horse_name", how="left")

        data_with_odds["simulated_price"] = data_with_odds["simulated_price"].replace(
            [np.inf, -np.inf], 999.0
        )
        data_with_odds["simulated_price"] = data_with_odds["simulated_price"].round(1)
        return data_with_odds

    def _simulate_padding_horse_performance(self, horse_data, race_class):
        simulated_performances = []
        median_race_rating = float(horse_data["rating"].median())
        median_speed_figure = float(horse_data["speed_figure"].median())
        horse_counts = horse_data["horse_id"].value_counts()
        horses_with_few_runs = horse_counts[horse_counts < 15].index.tolist()

        for horse in horses_with_few_runs:
            horse_data_single = horse_data[horse_data["horse_id"] == horse]
            print(f"Processing horse ID: {horse}")

            current_runs = horse_data_single["number_of_runs"].iloc[0]
            runs_to_add = 15 - current_runs

            # Calculate 90% of max rating and speed figure
            max_rating = 1 * horse_data_single["rating"].max()
            max_speed = 1 * horse_data_single["speed_figure"].max()

            for i in range(runs_to_add):
                is_poor_performance = (i + 1) % self.poor_performance.get(
                    race_class, 9
                ) == 0

                if is_poor_performance:
                    final_rating = final_speed = 0
                else:
                    if current_runs <= 5:
                        # Use 90% of max rating for horses with 5 or fewer runs
                        base_rating = max_rating
                        base_speed = max_speed
                    else:
                        base_rating = horse_data_single["rating"].mean()
                        base_speed = horse_data_single["speed_figure"].mean()

                    std_dev_rating = max(1, horse_data_single["rating"].std())
                    std_dev_speed = max(1, horse_data_single["speed_figure"].std())
                    simulated_rating = np.random.normal(base_rating, std_dev_rating)
                    simulated_speed = np.random.normal(base_speed, std_dev_speed)
                    final_rating = 0.7 * simulated_rating + 0.3 * median_race_rating
                    final_speed = 0.7 * simulated_speed + 0.3 * median_speed_figure

                place_chance = np.random.rand()
                first_place = (
                    1 if place_chance < 0.25 and not is_poor_performance else 0
                )
                second_place = (
                    1 if 0.25 <= place_chance < 0.5 and not is_poor_performance else 0
                )
                third_place = (
                    1 if 0.5 <= place_chance < 0.75 and not is_poor_performance else 0
                )
                fourth_place = (
                    1 if 0.75 <= place_chance and not is_poor_performance else 0
                )

                simulated_performances.append(
                    {
                        "horse_name": horse_data_single["horse_name"].iloc[0],
                        "horse_id": horse,
                        "rating": final_rating,
                        "speed_figure": final_speed,
                        "todays_days_since_last_ran": 14,
                        "todays_first_places": first_place,
                        "todays_second_places": second_place,
                        "todays_third_places": third_place,
                        "todays_fourth_places": fourth_place,
                        "number_of_runs": current_runs + i + 1,
                    }
                )

        simulated_df = pd.DataFrame(simulated_performances)
        return pd.concat([horse_data, simulated_df], ignore_index=True)

    def _simulate_horse_performance(self, horse_data, race_class):
        placed_efforts = (
            horse_data[
                [
                    "todays_first_places",
                    "todays_second_places",
                    "todays_third_places",
                    "todays_fourth_places",
                ]
            ]
            .sum(axis=1)
            .iloc[0]
        )
        mean_rating = horse_data["rating"].mean()
        std_rating = horse_data["rating"].std()
        adjusted_std = std_rating * (
            1 - (placed_efforts / horse_data["number_of_runs"].iloc[0])
        )

        is_poor_performance = np.random.rand() < 1 / self.poor_performance.get(
            race_class, 9
        )

        return 0 if is_poor_performance else np.random.normal(mean_rating, adjusted_std)

    def _run_simulation(self, horse_data, race_class):
        n_simulations = 1000
        horse_names = horse_data.set_index("horse_id")["horse_name"].to_dict()
        race_results = {
            name: {"wins": 0, "seconds": 0, "thirds": 0}
            for name in horse_names.values()
        }

        for _ in range(n_simulations):
            round_results = [
                (
                    horse,
                    self._simulate_horse_performance(
                        horse_data[horse_data["horse_id"] == horse], race_class
                    ),
                )
                for horse in horse_data.horse_id.unique()
            ]
            top_three = sorted(round_results, key=lambda x: x[1], reverse=True)[:3]
            for i, (horse_id, _) in enumerate(top_three):
                horse_name = horse_names[horse_id]
                if i == 0:
                    race_results[horse_name]["wins"] += 1
                elif i == 1:
                    race_results[horse_name]["seconds"] += 1
                else:
                    race_results[horse_name]["thirds"] += 1

        results_df = pd.DataFrame(race_results).T
        results_df["win_percentage"] = results_df["wins"] / n_simulations * 100
        results_df = results_df.sort_values("win_percentage", ascending=False)
        results_df = results_df.rename(
            columns={"wins": "first", "seconds": "second", "thirds": "third"}
        )
        results_df["win_percentage"] = results_df["win_percentage"].round(2)
        results_df["simulated_price"] = 100 / results_df["win_percentage"]

        return results_df
