from core_module.utils.util import debug_print
from core_module.utils.file_utils import load_json_file


def calculate_expected_value(card_data, grading_cost=29):
    """
    Calculate the expected value of the card.

    Parameters:
        card_data (dict): Dictionary containing card information.
        grading_cost (float): Cost of grading a card.

    Returns:
        float: The expected value of the card.
    """
    # Extract relevant fields from the card data
    raw_price = card_data["raw_price"]
    psa_10_price = card_data["psa_10_price"]
    gem_rate = card_data["gem_rate"]

    # Calculate the expected value
    # expected_value = -grading_cost + (gem_rate * psa_10_price) + raw_price

    wager_amount = grading_cost + raw_price
    probability = gem_rate
    payout = psa_10_price
    loss_payout = raw_price

    expected_value = calculate_wager_ev(wager_amount, probability, payout, loss_payout)

    return expected_value


def calculate_wager_ev(wager_amount, probability, payout, loss_payout):
    # Calculate the probability of loss
    probability_of_loss = 1 - probability

    # Calculate the expected value
    expected_value = (probability * payout) + (probability_of_loss * loss_payout)

    return expected_value


def calculate_net_gain(card_data, grading_cost=29):
    """
    Calculate the net gain/loss if the card is bought and graded.

    Parameters:
        card_data (dict): Dictionary containing card information.
        grading_cost (float): Cost of grading a card.

    Returns:
        tuple: Expected value, total grading cost, and net gain/loss.
    """
    # Step 1: Calculate expected value
    expected_value = calculate_expected_value(card_data, grading_cost)

    # Step 2: Calculate total grading cost (raw_price + grading_cost)
    total_grading_cost = card_data["raw_price"] + grading_cost

    # Step 3: Calculate net gain/loss
    net_gain = expected_value - total_grading_cost

    # Step 4:
    lucrative_factor = float(net_gain) / total_grading_cost

    return expected_value, total_grading_cost, net_gain, lucrative_factor


if __name__ == '__main__':
    candidates = load_json_file("cache/candidates.json")
    for card in candidates:
        ev, total_cost, net_gain = calculate_net_gain(card, grading_cost=29)
        debug_print(f"Card: {card['name']}")
        debug_print(f"Card raw: {card['raw_price']:.2f}")
        debug_print(f"Card PSA 10: {card['psa_10_price']:.2f}")
        debug_print(f"Gem Rate: {card['gem_rate']:.2f}")
        debug_print(f"Total Grading Cost: ${total_cost:.2f}")
        debug_print(f"Expected Value (EV): ${ev:.2f}")
        debug_print(f"Net Gain/Loss: ${net_gain:.2f}")
        debug_print()
