palette = ["#000000", #black
           "#ffffff", #white
           "#ff0000", #red 2
           "#00ff00", #green 3
           "#0000ff", #blue 4
           "#007F46", #darkgreen 5
           "#32BCFF", #lightblue 6
           "#195EBD", #darkblue 7
           "#dd8855",
           "#664400",
           "#ff7777",
           "#333333",
           "#777777",
           "#aaff66",
           "#0088ff",
           "#bbbbbb"]

i = 0
for r, g, b in [(int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)) for color in palette]:
    gba_color = (((r >> 3) & 31) | (((g >> 3) & 31) << 5)
                 | (((b >> 3) & 31) << 10))
    print(f'palette[{i}] = {hex(gba_color)};')
    i = i+1
