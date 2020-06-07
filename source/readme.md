# What's this about

Solitaire was the first computer game I have played, ages ago, on an ancient Windows 3.1 laptop. I have never actually implemented it. 

# The target platform

Let's target Gameboy Advance (GBA). It has a resolution of 240x160, four directional buttons on the d-pad, and A, B buttons and runs the ??? CPU at ??? MHz. We can develop in C using the excellent [devkitPro toolchain](https://devkitpro.org/). 

## Graphics

The Game Boy Advance has a couple of graphic modes. I plan to use  [Mode 3](https://www.coranac.com/tonc/text/bitmaps.htm), which is a bitmap mode, with a resolution of 240x160 and a 16-bit palette of 16 colors.

# Prototyping the dimensions

We'd like a screen layout such as:

Score Time 
P C   F F F F

1 2 3 4 5 6 7

Where the P/C stands for pile and the card next to it; F is the foundation placeholder. The numbers 1,2,3,4,5,6,7 represent the columns with their respective initial height.

So we need 7 columns of cards organized 2 rows. we also need some padding for the board and cards

## Let's prototype in HTML / CSS

I considered multiple options on how to prototype - whethe to do it in Creating a simple mock board in HTML :

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
    padding-left: 2px;
}
```

The we can define a card class, and by twiddling the numbers I've arrived at the following dimensions: 28x36 for the card, 5 px for the margin, so the card itself is 23x36px.

```css
.card {
    width: 28px;
    height: 36px;
    margin-left: 5px;
    float: left;
    background-color: white;
}
```

Now to simulate the height part of the layout let's define the column-N class, where the N is the height of the column in cards (column-5 starts with 4 hidden cards and 1 revealed card).

Using multiples of 8px scales nicely

```css

.column-2 {
    padding-top: 8px;
}

.column-3 {
    padding-top: 16px;
}
...
```

Keeping score

The score row should probably include the score and a timer.

Mocking it up as another div (above the board)

```html
<div id="score-row">Score:123   Time: 01:23</div>
```

and styling with `position:absolute` so not to move the other elements:

```css
#score-row{
    position: absolute;
    margin-left: 4px;
    font-size: xx-small;
    color:white;
}
```

This is how it looks so far:

![screenshot](assets/solitaire-css-mockup.png)

# Implementing Solitaire

!TODO

# Graphics

There is no graphics library. The video RAM is mapped at the address `0x06000000`

We can draw things into the video memory ourselves (set a pixel to a palette color):

```c
#define MEM_VRAM 0x06000000
#define vid_mem ((u16 *)MEM_VRAM)

inline void draw_point(int x, int y, int clr)
{
    vid_mem[y * SCREEN_WIDTH + x] = clr;
};
```

## Sprites

!TODO sprites

## Palette

!TODO update to solitaire

To obtain this palette, Python script helped convert 32-bit hexcodes into 16-bit:

```python
palette = ["#000000", "#ffffff", "#880000", "#aaffee",
      "#cc44cc", "#00cc55", "#0000aa", "#eeee77",
      "#dd8855", "#664400", "#ff7777", "#333333",
      "#777777", "#aaff66", "#0088ff", "#bbbbbb"]

i = 0
for r,g,b in [(int(color[1:3],16), int(color[3:5],16), int (color[5:7],16)) for color in palette]:
    gba_color = (((r >> 3) & 31) | (((g >> 3) & 31) << 5) | (((b >> 3) & 31) << 10))
    print(f'palette[{i}] = {hex(gba_color)};')
    i = i+1
```


## Input

To read the keys one should call `scanKeys();` to obtain the keypad state and then call the `keysDown()` function to get the keys that have been pressed, as documented in devkitPro [`gba_input.h`](https://github.com/devkitPro/libgba/blob/master/include/gba_input.h). 

We'll need the following keys:

```c
typedef enum KEYPAD_BITS {
	KEY_A		=	(1<<0),	/*!< keypad A button */
	KEY_B		=	(1<<1),	/*!< keypad B button */
	KEY_SELECT	=	(1<<2),	/*!< keypad SELECT button */
	KEY_START	=	(1<<3),	/*!< keypad START button */
	KEY_RIGHT	=	(1<<4),	/*!< dpad RIGHT */
	KEY_LEFT	=	(1<<5),	/*!< dpad LEFT */
	KEY_UP		=	(1<<6),	/*!< dpad UP */
	KEY_DOWN	=	(1<<7),	/*!< dpad DOWN */
	KEY_R		=	(1<<8),	/*!< Right shoulder button */
	KEY_L		=	(1<<9),	/*!< Left shoulder button */

	KEYIRQ_ENABLE	=	(1<<14),	/*!< Enable keypad interrupt */
	KEYIRQ_OR		=	(0<<15),	/*!< interrupt logical OR mode */
	KEYIRQ_AND		=	(1<<15),	/*!< interrupt logical AND mode */
	DPAD 		=	(KEY_UP | KEY_DOWN | KEY_LEFT | KEY_RIGHT) /*!< mask all dpad buttons */
} KEYPAD_BITS;
```
