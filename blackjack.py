from enum import Enum, auto
import random


class GameState(Enum):
    PRE_GAME = auto()
    PLAYER_TURN = auto()
    DEALER_TURN = auto()
    EVALUATION = auto()
    REPLAY_PROMPT = auto()
    QUIT = auto()


class Player:
    def __init__(self, name):
        self.name = name
        self.money = 100
        self.bet = 0
        self.hand = []
    
    @property
    def hand_total(self):
        value = 0
        ace = 0

        for card in self.hand:
            rank = card[0]
            if rank == "Ace":
                ace += 1
                value += 11
            elif rank in ["Jack", "Queen", "King"]:
                value += 10
            else:
                value += rank

        while value > 21 and ace:
            ace -= 1
            value -= 10

        return value

    def is_blackjack(self):
        return len(self.hand) == 2 and self.hand_total == 21
        
    def place_bet(self, bet):
        self.bet += bet
        self.money -= bet

    def show_hand(self):
        hand_str = ", ".join(f"{card[0]} of {card[1]}" for card in self.hand)
        print(f"{self.name}'s hand: {hand_str} ({self.hand_total})")
        
    def reset(self):
        self.bet = 0
        self.hand = []


class Dealer(Player):
    name = "Dealer"
    deck_num = 4

    def __init__(self):
        self.shoe = self.gen_shoe()
        self.hand = []

    def gen_shoe(self):
        shoe = []
        for _ in range(self.deck_num):
            shoe += gen_deck()
        random.shuffle(shoe)

        return shoe

    def deal_card(self, receiver, initial=False):
        if initial:
            receiver.hand.append(self.shoe.pop())
        else:
            receiver.hand.append(self.shoe.pop())
            receiver.show_hand()
            if receiver.hand_total > 21:
                print(f"{receiver.name} bust!")

            
def print_card(card):
    rank, suit = card
    return f"{rank} of {suit}"


def gen_deck():
    RANKS = [2, 3, 4, 5, 6, 7, 8, 9, 10, "Jack", "Queen", "King", "Ace"]
    SUITS = ["Diamonds", "Clubs", "Spades", "Hearts"]

    deck = [(rank, suit) for rank in RANKS for suit in SUITS]
    return deck


def main():

    name = input("Name? ")
    p1 = Player(name)
    dealer = Dealer()
    discard = []

    # Rules: european, S17, split not allowed, surrender not allowed

    game_state = GameState.PRE_GAME
    
    print(f"Money: {p1.money}")

    while game_state != GameState.QUIT:
        print()
        match game_state:
            case GameState.PRE_GAME:
                p1_score = None
                dealer_score = None
                bet = 0
                while bet > 100 or bet < 10:
                    try:
                        bet = int(input("How much do you want to bet? (Min: 10, Max: 100): ").strip())
                        if bet > 100:
                            print("Table maximum is 100.")
                        elif bet < 0:
                            print("Table minimum is 10.")
                    except ValueError:
                        print("Please enter a valid number.")
                p1.place_bet(bet)
                print("Dealer is shuffling, please wait warmly...")
                for _ in range(2):
                    dealer.deal_card(p1, initial=True)
                    dealer.deal_card(dealer, initial=True)
                game_state = GameState.PLAYER_TURN

            case GameState.PLAYER_TURN:
                print(f"Dealer's upcard: {print_card(dealer.hand[0])}")
                p1.show_hand()
                if p1.hand_total == 21:
                    print(f"{p1.name} has blackjack!")
                else:
                    while p1.hand_total <= 21:
                        opt = input(f"{p1.name}'s move (h, s, dd): ").lower()
                        if opt == "h":
                            dealer.deal_card(p1)
                        elif opt == "s":
                            break
                        elif opt == "dd":
                            if len(p1.hand) == 2:
                                p1.place_bet(p1.bet)
                                dealer.deal_card(p1)
                                break
                            else:
                                print("You can only double down if you have 2 cards.")
                        else:
                            print("Invalid input")
                game_state = GameState.DEALER_TURN

            case GameState.DEALER_TURN:
                dealer.show_hand()
                if dealer.hand_total == 21:
                    print(f"{dealer.name} has blackjack!")
                else:
                    while dealer.hand_total < 17:
                        dealer.deal_card(dealer)
                game_state = GameState.EVALUATION

            case GameState.EVALUATION:
                player_total = p1.hand_total
                dealer_total = dealer.hand_total
                
                if dealer_total > 21:
                    dealer_score = "Bust"
                elif dealer.is_blackjack():
                    dealer_score = "Blackjack"
                else:
                    dealer_score = dealer_total
                    
                if player_total > 21:
                    player_score = "Bust"
                elif p1.is_blackjack():
                    player_score = "Blackjack"
                else:
                    player_score = player_total
                
                print(f"{p1.name}: {player_score}")
                print(f"Dealer: {dealer_score}\n")

                if player_total > 21:
                    print(f"{p1.name} busts. {dealer.name} wins.")
                elif p1.is_blackjack() and dealer.is_blackjack():
                    p1.bet, p1.money = 0, p1.bet + p1.money
                    print("Push. It's a tie.")
                elif player_total == 21 and len(p1.hand) == 2:
                    p1.bet = int(p1.bet * 2.5)
                    p1.bet, p1.money = 0, p1.bet + p1.money
                    print(f"{p1.name} has Blackjack! {p1.name} wins.")
                elif dealer_total == 21 and len(dealer.hand) == 2:
                    print("Dealer has Blackjack! Dealer wins.")
                elif dealer_total > 21:
                    p1.bet *= 2
                    p1.bet, p1.money = 0, p1.bet + p1.money
                    print(f"{dealer.name} busts. {p1.name} wins.")
                elif player_total == dealer_total:
                    p1.bet, p1.money = 0, p1.bet + p1.money
                    print("Push. It's a tie.")
                elif player_total > dealer_total:
                    p1.bet *= 2
                    p1.bet, p1.money = 0, p1.bet + p1.money
                    print(f"{p1.name} wins.")
                else:
                    print("Dealer wins.")

                print(f"Money: {p1.money}")
                game_state = GameState.REPLAY_PROMPT

            case GameState.REPLAY_PROMPT:
                again = input("Do you want to try again? (y/n) ").lower()
                while again not in {"y", "n"}:
                    print("Invalid input. Enter 'y' or 'n'.")
                    again = input("Do you want to try again? (y/n) ").lower()
                if again == "n":
                    game_state = GameState.QUIT
                    print("See you next time!")
                else:
                    discard.extend(p1.hand + dealer.hand)
                    p1.reset()
                    dealer.hand.clear()

                    # reshuffles if shoe reaches half cards
                    if len(dealer.shoe) < 52 * (dealer.deck_num / 2):
                        dealer.shoe.extend(discard)
                        discard.clear()
                        print("Shoe reshuffled.")

                    game_state = GameState.PRE_GAME


main()