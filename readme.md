# Implementing Solitaire

Solitaire was the first computer game I have played, ages ago, on an ancient Windows 3.1 laptop. I have never actually implemented it. When I say Solitaire, I actually mean the [Klondike](https://en.wikipedia.org/wiki/Klondike_(solitaire)) variant, which I think is the most commonly known amongst the computer players. 

## Tech stack

I like C these days, there's something zen-like about being close to the machine and almost universally portable. The standard library doesn't offer as much convencience as, say, Python, Java or JavaScript, but we won't need too many complicated data structures, so we can roll our own.

There won't initially be a graphical version, but a terminal character-based version seems like a good idea in the spirit of doing one thing at a time - some game logic first, some user interface later and maybe a GUI even later. 

## Architecture

I don't do that much upfront planning for pet projects, they mostly evolve on the go. However, in this game, the plan is to proceed along the following lines:

- Define the basic game object data structure (the cards)
- Implement and test the basic interactions between the cards
- Define more game data structure (game board, piles of cards)
- Implement common operations on these structure (linked list fun)
- Display the current game state on the screen
- Parse user input
- Execute actions based on the user input  

## The cards

Solitaire is played with a standard 52-card deck with four suits: 

> ♥ Heart, ♠ Spade, ♣ Club, ♦ Diamond

and thirteen ranks (in ascending order)

> A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K

Hence the card structure can be defined in C as: 
```c
enum {
	SUIT_HEART, SUIT_SPADE, SUIT_CLUB, SUIT_DIAMOND // ♥♠♣♦
} ;

enum {
	RANK_A, RANK_2, RANK_3, RANK_4, RANK_5, RANK_6, RANK_7, RANK_8, RANK_9, RANK_10, RANK_J, RANK_Q, RANK_K
};

typedef struct card {
	int suit;
	int rank;
};
```

### Solitaire rules as functions

Solitaire defines a couple of card interactions, which we'll define as functions:
- is red? 
- is black?
- are alternate colors? (as card colors in columns must alternate between red and black)
- is in sequence? (A -> 2 -> 3 ... -> K)
- can be placed on foundation? (A♥ -> 2♥ -> 3♥ -> K♥)
- can be placed on bottom? (is alternate and is in sequence) ( J♦ -> 10♠ -> 9♥ -> 8♣ -> 7♥)

These can be implemented as a set of simple C functions:
```c
int is_black(card c) {
	return c.suit == SUIT_CLUB || c.suit == SUIT_SPADE;
}

int is_red(card c) {
	return c.suit == SUIT_HEART || c.suit == SUIT_DIAMOND;
}

int is_alternate_color(card first, card second) {
	return is_black(first) != is_black(second);
}

int is_in_sequence(card lower, card higher) {
	return higher.rank == lower.rank + 1;
}

int can_be_placed_bottom(card parent, card child) {
	return is_alternate_color(parent, child) && is_in_sequence(child, parent);
}

int is_same_suit(card first, card second) {
	return first.suit == second.suit;
}

int can_be_placed_on_foundation(card parent, card child) {
	return is_same_suit(parent, child) && is_in_sequence(parent, child);
}
```

This also can be tested during the development with a simple "test":

```c
    card c5S = make_card(SUIT_SPADE, RANK_5);
	card c6H = make_card(SUIT_HEART, RANK_6);
	printf("5s is black %d vs 1 \n", is_black(c5S));
	printf("5s is red %d vs 0 \n", is_red(c5S));
    printf("5s 6h is alternate %d vs 1 \n", is_alternate_color(c5S, c6H));
    ...
```

> Note: There *are* many unit testing frameworks in C if you want to test things more correctly than dumping some code in the main() function during development

### Game deck (and the data structures)

Let's define our first pile of cards - the deck of initial 52 cards.

```c
#define CARD_COUNT 52

typedef struct deck {
	int num_cards;
	card** cards;
} deck;

deck* make_deck() {
	deck* deck = mallocz(sizeof(deck));
	deck->cards = mallocz(sizeof(card*) * CARD_COUNT);
	deck->num_cards = 0;
	for (int rank = 0; rank < RANK_COUNT; rank++) {
		for (int suit = 0; suit < SUIT_COUNT; suit++) {
			deck->cards[deck->num_cards++] = make_card_ptr(suit,rank);
		}
	}
	return deck;
}
```

It seems there are a couple more piles around Solitaire - for example, waste (revealed cards), the stacks of cards on the foundation, and the piles on the bottom. Seems like it would be nice to have the concept of the pile encapsulated as a structure with associated functions.

```c
typedef struct pile {
	int num_cards;
	card** cards;
} pile;

pile* make_pile();
void append(pile* pile, card* card);
card* pop(pile* pile);
card* dequeue(pile* pile);
card* peek_card_at(pile* pile, int index);
```

### Array vs linked list

We have either the option of using a linked list to represent the collection of cards in a pile, or just assume there will never be a larger pile than 52 and go with an array as the backing store and a counter. With this, at the expense of more memory overhead per pile. As there is a known number of piles: unturned and turned card deck, 4 foundations, 7 columns, the total is 2+4+7=13 piles. On a 32-bit system, that's at most `13 * (sizeof card*) * CARD_COUNT = 13 * 4 * 52 = 2704` bytes overhead. Meh.

On the other hand, linked lists are a kind of a traditional C structure, so it may be nicer with them. Let's see.

## Prototyping without graphics


### Ncurses

There's a fine text-user interface library ncurses (new curses) out there. Using its Unicode version `ncursesw` we get support for Unicode card symbols, such as ♥♠♣♦. That enables us to represent the cards as a fairly human-readable 10♠ or J♥.

We can introduce helper functions such as `rank_to_charptr` and `suit_to_charptr` that we'll later use to print a card:

```c
const char *suit_to_charptr(int suit) {
  switch (suit) {
  case SUIT_HEART:
    return "\u2665";
  case SUIT_SPADE:
    return "\u2660";
  case SUIT_CLUB:
    return "\u2663";
  case SUIT_DIAMOND:
    return "\u2666";
  ...
  }
}
```

Printing a card on the screen is done with the `printw` ncurses function, which behaves like `printf`. We can also move the cursor around with the `move(int row, int column)` function.

```c
void printw_card(card *c) {
  printw("%s%s", rank_to_charptr(c->rank), suit_to_charptr(c->suit));
}
```

### Basic layout

So far we got to the point of having the text user interface laid out:

Here I also had to decide how the cards in the piles would be ordered. I think it makes sense that the first card would mostly be the displayed one - for stock, waste and fodation piles.

I needed to add a `peek(pile *pile)` function to peek at the pile, as these piles would only display the top card.

The column piles would be ordered 'top to bottom', so initially only the last card would be revealed, but we can draw the column from first card to the last.

The rendering code is fairly uninteresting, using string arrays for headers, picking an arbitrary size (100) for the game deck terminal width, then iterating through the piles and moving the cursor around the screen.

```c
char *first_row_headers[] = {"Stock",        "Waste",        "",
                             "Foundation 1", "Foundation 2", "Foundation 3",
                             "Foundation 4"};
...
// first row headers
int column_size = 14;
for (int i = 0; i < 7; i++) {
move(0, column_size * i);
  printw("%s", first_row_headers[i]);
}
// first row content 
move(1, 0);
printw_card(peek(stock(state)));
move(2, 0);
printw_pile_size(stock(state));
...
 // foundations
for (int f = 0; f < FOUNDATION_COUNT; f++) {
  int foundation_1_column = 3;
  move(1, (foundation_1_column + f) * column_size);
  printw_card(peek(foundation(state, f)));
  move(2, (foundation_1_column + f) * column_size);
  printw_pile_size(foundation(state, f));
}

```

At this point of development it makes sense to also show the face-down cards, represented as (Q♦). I had to add the revealed flag (face up), as it's possible to have a sequence of multiple face up cards in the columns.

So we end up with a representation such as:

```
Column 4 
(4 cards)
(J♠) 
(A♣)  
(Q♦)   
6♥      
```

### Adding color to curses

If we add a bit of color, the player will have have an easier time distinguishing 4♣ and 4♥ (four of spades and four of hearts). Ncurses supports colors in the terminal. I've used a [tutorial by Jim Hall](https://www.linuxjournal.com/content/programming-color-ncurses) to get up to speed with the basics.

There are only eight basic colors supported by the console - black, red, green, yellow, blue, magenta, cyan, white. Then we have to define a color pair with `init_pair(index, foreground, background)`. You can also pass `-1` as a color this function to use the default value.

Let's just change the foreground color of the red cards:

```c
#define BLACK_PAIR 1
#define RED_PAIR 2
...
init_pair(BLACK_PAIR, -1, -1);
init_pair(RED_PAIR, COLOR_RED, -1);
...
attron(COLOR_PAIR(RED_PAIR));
printw("4\u2660); //4♠
attroff(COLOR_PAIR(RED_PAIR));
```

To actually use that color pair during printing, use `attron(COLOR_PAIR(int pair))` to turn on the color attribute. This should be later turned off by a corresponding `attroff()` call.

![screenshot](assets/solitaire-curses-colors.png)

### Controls

We have the option of using text-based controls, that would (in case of moving the cards) have a form of `source destination`, so for example `c3 c4` means take 1 card from column 3 and put it at column 4. We also need to draw a card from the stock, so that could be a command `s`. To move the drawn card (from the waste), we'll use `w`. As we sometimes need to move more than one card, it could be solved with a command like `3c1 c5` - take three cards from column 1 and put them at column 5.

So we have a couple of possible combinations:

```
s
c3 f1
c7 c2
3c4 c5
w c4
w f3
```

There are some things, that should not be possible. Moving multiple cards from a column to a foundation makes no sense, as they won't be ordered in ascending order of the same suit. Moving multiple cards from the waste into a column can be disallowed as well. Drawing multiple cards from the stock might be possible, but let's ignore it and add it later. Let's also prohibit moving cards from foundations elsewhere.

#### Parsing the input

We have multiple options on how to parse the user input in C. I initially thought of parsing it by hand going character by character and keeping track of state or using the `scanf` function with multiple input templates, such as `%c%d %c%d` for the likes of `c3 f1`. The `scanf` family of functions returns the number of specific conversions, so we can check the return value for success and cascade the checks.

With the first option one should prepare the templates from the most specific to the least specific, we end up with four specific patterns:

```
%dc%d c%d -> 3c4 c5
%dc %c%d -> c3 f1 / c7 c2
w %c%d -> w c4 / w f3
s -> s
```

As the parsing function `parsed_input parse_input(char *command)` should return multiple values, let's wrap it in a structure:

```c
typedef struct parsed_input {
  char source;
  char destination;
  int source_index;
  int destination_index;
  int source_amount;
  int success;
} parsed_input;
```

And the parsing function is trying the patterns one by one, filling in the sources/destinations, as they are implied by some patterns.

```c
parsed_input parse_input(char *command){
  parsed_input parsed;
  parsed.success = 1;
  parsed.source_amount = 1;
  // parser patterns 
  char *pattern_multi_move = "%dc%d c%d";
  char *pattern_single_move = "c%d %c%d";
  char *pattern_waste_move = "w %c%d";
  char *pattern_stock = "s";
  if(sscanf(command, pattern_multi_move, &parsed.source_amount, &parsed.source_index, &parsed.destination_index) == 3){
    parsed.source = 'c';
    parsed.destination = 'c';
  }
  else if(sscanf(command, pattern_single_move, &parsed.source_index, &parsed.destination, &parsed.destination_index) == 3){
    parsed.source = 'c';
  }
  else if(sscanf(command, pattern_waste_move, &parsed.destination, &parsed.destination_index) == 2){
    parsed.source = 'w';
  }
  else if(strcmp(command, pattern_stock) == 0){
    parsed.source = 's';
  }
  else{
    parsed.success = 0;
  }
  return parsed;
}

```

Later as a more graphical interface is developed we also can have a concept of a cursor that we can move across the piles with the arrow keys.

### Adding more gameplay logic - moving the cards

TODO move or link the rules / functions here for better coherence

Once we parse user's command, we know where they want to move the cards from and to. This is the time to apply the rules based on the source and destination column. We can apply a simple 'source column' rule - we can pick the **source card** from the waste or a column only if it's not empty, and we pick up the last card.

The **destination** has different rules whether it's a foundation or a column, but the sequence of events is similar. We pick up the last card from the destination pile, use the game logic comparison function and if the card can be moved, we remove it from its source and push it to the end of the destination pile:

```c
void move_card(card *card, pile *source_pile, pile *destination_pile) {
  pop(source_pile);
  reveal(peek_last(source_pile));
  push(destination_pile, card);
}

...

card *source_card = peek_last(source_pile);

...
card *top_foundation_card = peek(destination_pile);
if (can_be_placed_on_foundation(*top_foundation_card, *source_card)) {
  move_card(source_card, source_pile, destination_pile);
  return MOVE_OK;
} 
```

One also needs to incorporate special rules for placing aces on empty foundations, or kings on empty columns:

```c
if (parsed.destination == 'f') {
  if (destination_pile->num_cards == 0 && source_card->rank == RANK_A) 
    move_card(source_card, source_pile, destination_pile);
    ...
}
...
if (parsed.destination == 'c') {
  if (destination_pile->num_cards == 0 && source_card->rank == RANK_K) 
    move_card(source_card, source_pile, destination_pile);
    ...
}
```

### Moving more than one card at a time

We would also like to allow the player to move more than one card at a time, from column to column.

![screenshot](assets/solitaire-curses-move-multiple.png)

To do this, we have to change the logic of moving - from checking whether the *bottommost* card of the source column fits the destination column to checking whether the *N-th* card fits.

Also, if it can be moved, we can't just pop the bottommost card from the source pile, but remove the N-th card possible from the middle of the pile, which means implementing one more linked list manipulation function `delete(pile*, card*)`.

```c
// remove a card from a pile, relinking the list
void delete (pile *pile, card *card) {
  if (is_empty(pile)) {
    return;
  }
  // no previous node for the first item
  card_node *prev = NULL;
  card_node *current;
  for (current = pile->head; current != NULL;
       prev = current, current = current->next) {
    if (current->value == card) {
      // skip the current item in the list
      pile->head = current->next;
      // decrement the card counter 
      pile->num_cards--;
      free(current);
      return;
    }
  }
}
```

TODO debugging - gdb, core dump, backtrace from core dump

### Debugging with gdb(tui)

### Debugging from dumps

The game was crashing when I attempted to move the entire column (two or more cards) to another column. 

If you're prepared for this, you can have the debugger ready and step through the code yourself. Another way to debug a crash like is to take a core dump (of the debug build, compiled with `-g`, so we'll have symbols available), and load it with

`gdb ./solitaire core.1000.5629.1593719583`

Then use the `bt` (backtrace) command to get a stack trace from the time of the crash. Examining variables and parameters works the same way as during live debugging. 

I have found out that there was a [bug](https://github.com/jborza/solitaire-cli/commit/a5f14a442418830464d953e33324822a90c7464b) in the `delete()` function if a first item was being removed from the list. Shame on me, I should have bothered with the unit tests.

TODO using valgrind for memory leaks

TODO using srand() for reproducible parties

TODO discuss save/load

TODO scoring