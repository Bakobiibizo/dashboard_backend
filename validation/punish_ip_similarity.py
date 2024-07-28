def process_addresses(addresses):
    unique_ips = {}
    for _, value in addresses.items():
        if value != "None:None" and not value.startswith("localhost"):
            ip, _ = value.split(":")
            ip_parts = ip.split(".")
            for i in range(1, len(ip_parts) + 1):
                partial_ip = ".".join(ip_parts[:i])
                if partial_ip not in unique_ips:
                    unique_ips[partial_ip] = set()
                unique_ips[partial_ip].add(ip)

    return unique_ips


def calculate_score(miner_ip, unique_ips):
    score_reduction = 0
    miner_parts = miner_ip.split(".")

    for i in range(3, len(miner_parts) + 1):
        partial_ip = ".".join(miner_parts[:i])
        if partial_ip in unique_ips:
            if i == 3:
                score_reduction += 1  # Penalty for 3 matching segments
            elif i == 4:
                score_reduction += 3  # Higher penalty for 4 matching segments

    return score_reduction


def punish_ips(miner_addresses):
    # Process the addresses
    unique_ips = process_addresses(miner_addresses)
    print("Unique IPs:", unique_ips)

    miner_data_dict = {}
    # Now, let's calculate the score for each miner
    for miner_id, address in miner_addresses.items():
        if address != "None:None" and not address.startswith("localhost"):
            ip, port = address.split(":")
            score_reduction = calculate_score(ip, unique_ips)
            print(f"Miner {miner_id} (IP: {ip}): Score reduction = {score_reduction}")
            miner_data_dict[miner_id] = (score_reduction, address)
    return miner_data_dict


if __name__ == "__main__":

    miner_addresses = {
        "0": "None:None",
        "18": "213.108.196.111:43100",
        "3": "None:None",
        "14": "213.108.196.111:43100",
        "2": "None:None",
        "21": "44.230.245.252:55555",
        "4": "localhost:8080",
    }

    print(punish_ips(miner_addresses))
