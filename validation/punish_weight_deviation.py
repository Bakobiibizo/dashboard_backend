import json
import statistics


def detect_outliers(data, threshold=2):
    outliers = {}
    for validator, weights in data.items():
        if weights:  # Check if the list is not empty
            if flat_weights := [
                w for sublist in weights for w in sublist if isinstance(w, (int, float))
            ]:
                mean = statistics.mean(flat_weights)
                stdev = statistics.stdev(flat_weights)
                for i, sublist in enumerate(weights):
                    for j, weight in enumerate(sublist):
                        if isinstance(weight, (int, float)):
                            z_score = (weight - mean) / stdev
                            if abs(z_score) > threshold:
                                if validator not in outliers:
                                    outliers[validator] = []
                                outliers[validator].append((i, j, weight))
    return outliers


def identify_boosted_miners(data, outliers):
    boosted_miners = {}
    for validator, outlier_weights in outliers.items():
        for i, j, weight in outlier_weights:
            miner = data[validator][i][0]  # Assuming miner ID is at index 0
            if miner not in boosted_miners:
                boosted_miners[miner] = []
            boosted_miners[miner].append((validator, weight))
    return boosted_miners


def punish_weight_deviation(data_path):
    # Load your data
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Detect outliers
    outliers = detect_outliers(data)

    # Identify boosted miners
    boosted_miners = identify_boosted_miners(data, outliers)

    # Print results
    print("Outliers detected:")
    for validator, outlier_weights in outliers.items():
        print(f"Validator {validator}:")
        for i, j, weight in outlier_weights:
            print(f"  Position [{i}][{j}]: Weight {weight}")

    data_dict = None
    print("\nBoosted miners:")
    for miner, boosts in boosted_miners.items():
        print(f"Miner {miner}:")
        for validator, weight in boosts:
            print(f"  Boosted by Validator {validator} with weight {weight}")


if __name__ == "__main__":
    data_path = "subnets/eden-subnet/data/2/query_map_weights.json"
    punish_weight_deviation(data_path)
