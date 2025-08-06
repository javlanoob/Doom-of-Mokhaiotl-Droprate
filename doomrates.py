import math

# Drop rates per delve level for each item
drop_rates = {
    "Mokhaiotl Cloth": {
        2: 1/2500, 3: 1/2000, 4: 1/1350, 5: 1/810, 6: 1/765,
        7: 1/720, 8: 1/630, 9: 1/540
    },
    "Eye of Ayak": {
        3: 1/2000, 4: 1/1350, 5: 1/810, 6: 1/765,
        7: 1/720, 8: 1/630, 9: 1/540
    },
    "Avernic Treads": {
        4: 1/1350, 5: 1/810, 6: 1/765,
        7: 1/720, 8: 1/630, 9: 1/540
    },
    "Pet": {
        6: 1/1000, 7: 1/750, 8: 1/500, 9: 1/250
    }
}

# Unique table hit chance per delve level
unique_table_hit = {
    2: 1/2500,
    3: 1/2000,
    4: 1/1350,
    5: 1/810,
    6: 1/255,
    7: 1/255,
    8: 1/255,
    9: 1/255,
}

def get_input_waves():
    waves = {}
    print("Enter how many waves you've cleared at each delve level (enter 0 if none):")
    for lvl in range(1, 10):
        key = 9 if lvl == 9 else lvl
        val = input(f"Delve level {key}+ waves cleared: ")
        try:
            waves[key] = int(val)
        except ValueError:
            waves[key] = 0
    return waves

def get_owned_items():
    owned = {}
    print("Enter how many of each item you already own:")
    for item in drop_rates.keys():
        val = input(f"{item}: ")
        try:
            owned[item] = int(val)
        except ValueError:
            owned[item] = 0
    return owned

def calculate_results(waves, owned_counts):
    results = {}
    for item, rates in drop_rates.items():
        # Calculate probability of NOT getting the item in one wave of each delve level
        p_no_item_total = 1.0
        expected_total = 0.0
        for lvl, count in waves.items():
            p = rates.get(lvl, 0)
            # total probability of getting item in one wave at that lvl
            p_no_item_total *= (1 - p) ** count
            expected_total += p * count
        p_at_least_one = 1 - p_no_item_total
        results[item] = {
            "probability": p_at_least_one,
            "expected": expected_total,
            "owned": owned_counts.get(item, 0),
            "rates": rates
        }
    return results


def binomial_probability(n, k, p):
    # Binomial probability P(X = k) for k successes in n trials with success probability p
    if p == 0:
        return 1.0 if k == 0 else 0.0
    if k > n or k < 0:
        return 0.0
    comb = math.comb(n, k)
    return comb * (p ** k) * ((1 - p) ** (n - k))

def safe_inv(prob):
    if prob <= 0:
        return "∞"
    return f"1/{(1/prob):.1f}"

def main():
    print("=== OSRS Doom of Mokhaiotl Drop Calculator ===")
    waves = get_input_waves()
    owned_counts = get_owned_items()

    results = calculate_results(waves, owned_counts)
    total_expected = 0
    total_owned = 0
    
    # Count uniques without Pet
    for item, data in results.items():
        if item.lower() != "pet":
            total_expected += data["expected"]
            total_owned += data["owned"]

    print("\n--- Total drop chance ---")
    total_owned_drops = sum(owned_counts.values())
    total_waves_done = sum(waves.values())
    combined_p_total = 0
    for lvl, count in waves.items():
        combined_p_level = 0
        for item, data in results.items():
            combined_p_level += data["rates"].get(lvl, 0)
        combined_p_total += combined_p_level * count
    combined_p_avg = combined_p_total / total_waves_done if total_waves_done > 0 else 0

    n = total_waves_done
    owned = total_owned_drops
    if n == 0 or combined_p_avg == 0:
        print("No waves or combined drop chance is 0, cannot calculate total drops probabilities.")
    else:
        p_exactly_k = binomial_probability(n, owned, combined_p_avg)
        p_less_than_k = sum(binomial_probability(n, i, combined_p_avg) for i in range(owned)) if owned > 0 else 0
        p_more_than_k = 1 - p_exactly_k - p_less_than_k

        print(f"Total drops:")
        print(f"  {p_exactly_k*100:.2f}% chance ({safe_inv(p_exactly_k)}) of getting exactly {owned} total drop(s)")
        if owned > 0:
            print(f"  {p_less_than_k*100:.2f}% chance ({safe_inv(p_less_than_k)}) of getting less than {owned} total drop(s)")
        print(f"  {p_more_than_k*100:.2f}% chance ({safe_inv(p_more_than_k)}) of getting more than {owned} total drop(s)")

    print("\n--- Unique Chance per Item ---")
    for item, data in results.items():
        owned = data["owned"]
        n = total_waves_done

        p_total = 0
        for lvl, count in waves.items():
            p_total += count * data["rates"].get(lvl, 0)
        p_avg = p_total / n if n > 0 else 0

        if n == 0 or p_avg == 0:
            print(f"{item}: No waves or drop chance 0, cannot calculate probabilities.")
            continue

        p_exactly_k = binomial_probability(n, owned, p_avg)
        p_less_than_k = sum(binomial_probability(n, i, p_avg) for i in range(owned)) if owned > 0 else 0
        p_more_than_k = 1 - p_exactly_k - p_less_than_k

        print(f"{item}:")
        print(f"  {p_exactly_k*100:.2f}% chance ({safe_inv(p_exactly_k)}) of getting exactly {owned} drop(s)")
        if owned > 0:
            print(f"  {p_less_than_k*100:.2f}% chance ({safe_inv(p_less_than_k)}) of getting less than {owned} drop(s)")
        print(f"  {p_more_than_k*100:.2f}% chance ({safe_inv(p_more_than_k)}) of getting more than {owned} drop(s)")

    print("\n--- Summary ---")
    print(f"Expected uniques: {total_expected:.2f}")
    print(f"Actual uniques:   {total_owned}")

if __name__ == "__main__":
    main()
