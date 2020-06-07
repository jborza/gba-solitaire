klondike notes:

# The target platform

Gameboy Advance (GBA). It has a resolution of 240x160, four directional buttons on the d-pad, and A, B buttons.

# Prototyping the dimensions

We'd like a layout such as

Score Time 
P C   F F F F

1 2 3 4 5 6 7

Where the P/C/F things stand for pile and card placeholders, and the numbers 1,2,3,4,5,6,7 represent the columns with their respective initial height.

need 6 columns of cards, 2 rows.
padding for the board and cards

width formula:
240 = board_padding / 2 + (card_width + card_pading * 2) * 6

height formula:
160 = board_padding / 2 + (card_height + card_padding * 2) * 6

# Let's prototype in CSS

Creating a simple mock board in HTML:

```html
   <div id="board">
        <div class="row">
            <div id="pile" class="card">P</div>
            <div class="card">?</div>
            <div class="card" id="blank">?</div>
            <div class="card" id="f1">A1</div>
            <div class="card" id="f2">A2</div>
            <div class="card" id="f3">A3</div>
            <div class="card" id="f4">A4</div>
        </div>
        <div class="row second-row">
            <div class="card column-1" id="p1">1</div>
            <div class="card column-2" id="p2">2</div>
            <div class="card column-3" id="p3">3</div>
            <div class="card column-4" id="p4">4</div>
            <div class="card column-5" id="p5">5</div>
            <div class="card column-6" id="p6">6</div>
            <div class="card column-7" id="p7">7</div>
        </div>
    </div>
```

We can define the basic styles in CSS and tweak the numbers as we go.

Having Screen and Board entities lets us set up the board - using GBA 240x160px dimensions for screen and padding to make space for the score row:

```css
#screen{
    width:240px;
    height: 160px;
    background-color: green;
}

#board {
    padding-top: 20px;
    padding-left: 4px;
}

```

let board_padding = 24 
240 - 48 = (card_width + card_pading * 2) * 6
let card_padding = 4
192 = (card_width + card_pading * 2) * 6
32 = (card_width + card_pading * 2)
24 = (card_width + card_pading * 2)

let card_width = 24
let card_height = 32





240 = 64 + 

score row:
number of turns, points, timer?

card in windows solitaire:
120x160 px
aspect ratio: 12:16 = 6:8 = 3:4

we also need to draw a cursor moved by the d-pad