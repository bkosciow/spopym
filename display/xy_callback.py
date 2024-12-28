
def transform_half(lcd, i, j):
    offset_width = lcd.height // 2
    if 0 <= i < offset_width:
        i = i + offset_width
    else:
        i = i - offset_width

    return (i, j)
