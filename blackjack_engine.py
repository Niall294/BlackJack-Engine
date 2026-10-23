import random

def main():
    """This program runs a blackjack simulation where the bot plays perfectly optimal blackjack, using the possible outcomes
    in each position to chose weither to hit or stand on any given hand. There isn't splitting or betting although BlackJack
    itself is implemented. Fully randomized games can be played or the deck can be specifically set for testing / finding
    the optimal play in certain situations."""
    
    player_cards: list[Card] = []

    #? Comment out these lines to test specific edge cases.
    deck = create_and_shuffle_deck([])
    player_cards.append(deck.pop())
    player_cards.append(deck.pop())
    dealer_cards = [deck.pop()]

    #? Uncomment these lines to test specific edge cases.
    # player_cards.append(Card("2", "Spades"))
    # player_cards.append(Card("2", "Clubs"))
    # dealer_cards = [Card("A", "Hearts")]
    # deck = create_and_shuffle_deck(player_cards + dealer_cards)


    # Go through and play the game, printing along the way.
    print("\nStarting Cards:")
    print(f"Player Cards: {player_cards[0].get_card()}, {player_cards[1].get_card()}")
    print(f"Dealer Up Card: {dealer_cards[0].get_card()}")
    print("\nPlayer's Action:")

    for _ in range(0, 10, 1):
        if get_total_value(player_cards) > 21:
            print(f"Player busts.")
        
        # Decide on weither the player should hit or stand based on the percentage differential.
        output = player_choice(player_cards, dealer_cards, 1000)
        if output > 0:
            top_card = deck.pop()
            print(f"Player draws card: {top_card.get_card()}. ({output} %)")
            player_cards.append(top_card)
        else:
            print(f"Player stands. ({output} %)")
            break
    
    print("\nDealer's Action:")
    result = dealer_choice(deck, player_cards, dealer_cards, True)
    if result == True:      print("\nThe Player Wins!")
    elif result == None:    print("\nPush! (Tie)")
    elif result == False:   print("\nThe Dealer Wins!")

def player_choice(player_cards, dealer_cards, num_sims):
    """This funciton determines the optimal action for the player using the percetnage chance that the player will win if
    they decided to hit vs stand.
    
    Args:
        players_cards: The players cards thus far.
        dealer_card_value: The dealer's up card's value.
        num_sims: The number of simulations run for each hand.
    
     Returns:
         bool: hit (True) or stand (False).
    """
    
    # Check the winrate if the player stands.
    stand_win_rate = calculate_win_rate(player_cards, dealer_cards, num_sims)

    # Check the average winrate if the player hits.
    new_deck = create_and_shuffle_deck(player_cards + dealer_cards)
    sum = 0
    for item in new_deck:
        new_player_cards = player_cards.copy() # Copy player cards so they don't get stuffed with extra cards
        new_player_cards.append(item)
        sum += calculate_win_rate(new_player_cards, dealer_cards, num_sims)
    hit_win_rate = sum / len(new_deck)

    win_rate_differential = round(hit_win_rate - stand_win_rate, 4)
    return win_rate_differential

def calculate_win_rate(player_cards, dealer_cards, num_sims):
    """Helper funciton that calculates the approximate win rate in the given position."""

    wins: int = 0
    for _ in range(0, num_sims, 1):
        # Make new_deck so that we can simulate a multitude of different decks without cheating by using the actual deck.
        new_deck = create_and_shuffle_deck(player_cards + dealer_cards)
        # We must do .copy() on dealer_cards because it is a list (a mutable data type).
        value = dealer_choice(new_deck, player_cards, dealer_cards.copy(), False)
        if value:   wins += 1
    
    return (wins / num_sims) * 100

def dealer_choice(deck, player_cards, dealer_cards, should_print):
    """Plays out the dealers turn using the given deck. This funciton can be called multiple times to determine the numebr
    of times that the player would win or lose in a given positon.
    
    Args:
        deck: The cards still in the deck (not directly looked at just used to draw each hit).
        player_cards: The players cards
        dealer_cards: The dealers cards
        should_print: Weither to print the outputs for when the dealer actually plays the hand out.
    
     Returns:
         A bool: win (True) or loss (False).
    """

    # Get the value of both sides' cards and make a list of used_cards to pass into create_and_shuffle_deck.
    player_sum: int = get_total_value(player_cards)
    dealer_sum: int = dealer_cards[0].get_value(True)

    # (0) Player has already busted - Loss
    if player_sum > 21: return False

    for i in range(0, 10, 1):
        # (1) Dealer busts - Win
        if dealer_sum > 21:
            if should_print: print(f"Dealer busts.") # Print the value if True.
            return True

        # (2) Dealer hits - (stands on a soft 17)
        if dealer_sum < 17:
            dealer_cards.append(deck.pop()) # Take the top card off the deck and add it to the dealers hand.
            if should_print: print(f"Dealer draws card: {dealer_cards[-1].get_card()}.") # Print the value if True.
            new_dealer_sum = get_total_value(dealer_cards) # Update the dealers cards sum.
            # Check if the ace should be hard or soft, first check that there is an ace, and it is in the right range then
            #  add 10 to make it a soft total that is now done hitting.
            for item in dealer_cards:
                if item.get_rank() == "A" and new_dealer_sum <= 11:
                    new_dealer_sum += 10
                    break

        # (3) Checking for BlackJacks
        if i == 0:
            # Assign variabels to help with the following checks for BlackJacks
            dealer_ranks = [dealer_cards[0].get_value(False), dealer_cards[1].get_value(False)]
            player_ranks = [player_cards[0].get_value(False), player_cards[1].get_value(False)]
            dealer_BJ = (1 in dealer_ranks) and (10 in dealer_ranks)
            player_BJ = (1 in player_ranks) and (10 in player_ranks)

            # Check for BlackJacks using the previusly assigned variables.
            if player_BJ and dealer_BJ:         return None # Tie, both have BJ
            elif player_BJ and (not dealer_BJ): return True # Win, only the player has BJ
            elif (not player_BJ) and dealer_BJ: return False # Loss, only the dealer has BJ

        # (4) Dealer Stands
        if dealer_sum >= 17:
            if should_print: print(f"Dealer stands.") # Print the value if True.
            if player_sum == dealer_sum:    return None # Equal totals - Tie
            elif dealer_sum < player_sum:   return True # Player beats dealer outright - Win
            elif dealer_sum > player_sum:   return False # Dealer beats player outright - Loss
        
        # (5) If the dealer hits, continue.
        dealer_sum = new_dealer_sum

def get_total_value(cards):
    """This is a helper function that gets the hard value of any hand that is passed in."""

    sum: int = 0
    for card in cards:
        sum += card.get_value(False)

    return sum

def create_and_shuffle_deck(excluded_cards):
    """Creates a deck and shuffles it using a clever sytem where each card is assigned a random value and then .sort()
    is used to shuffle the deck.
    
    Args:
        excluded_cards: The cards that should be excluded from the new test (used in the simulations).
    
    Returns:
        list[Card]: The shuffled deck.
    """

    # Creates the parameters for the deck and the list that will hold and shuffle it.
    deck: list[(float, Card)] = []
    ranks = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]
    suits = ["Clubs", "Diamonds", "Hearts", "Spades"]

    # Convert excluded cards to a checkable version and not as an object.
    check_excluded_cards: list[str] = []
    for item in excluded_cards:
        check_excluded_cards.append(item.get_card())

    # Creates a list with a random value for each card and prepares it to be shuffled.
    for rank in ranks:
        for suit in suits:
            rand = random.random()
            card = Card(rank, suit)
            deck.append((rand, card))

    # Actually shuffle the deck and then copy over the Cards without their random values as they are no longer needed.
    deck.sort()
    clean_deck: list[Card] = []
    for item in deck:
        if item[1].get_card() not in check_excluded_cards:
            clean_deck.append(item[1])
    
    return clean_deck

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def get_card(self):
        return self.rank + " of " + self.suit

    def get_value(self, ace_choice):
        # Get the value of all of the cards, returns ace values based on the parameter ace_choice (True is 11).
        if self.rank == "A":
            value = 1
            if ace_choice:  value += 10
        elif self.rank in ("J", "Q", "K"):
            value = 10
        else:
            value = int(self.rank)

        return value

    def get_rank(self):
        return self.rank
    
    def get_suit(self):
        return self.suit

if __name__ == "__main__":
    main()