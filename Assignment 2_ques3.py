# Geometric Pattern Using Python's turtle graphics

import math
import turtle as T

def koch_segment(t, length, depth):
    # Code for given length and recursion depth.
    if depth == 0:
        t.forward(length)
    else:
        length /= 3.0
        koch_segment(t, length, depth - 1)
        t.left(60)
        koch_segment(t, length, depth - 1)
        t.right(120)
        koch_segment(t, length, depth - 1)
        t.left(60)
        koch_segment(t, length, depth - 1)

def draw_koch_polygon(n_sides, side_len, depth):
    T.setup(width=900, height=900)
    T.title(f"Koch-indented {n_sides}-gon | side={side_len}px | depth={depth}")
    t = T.Turtle()
    t.hideturtle()
    t.speed(0)      # Increase Speed
    t.penup()

    # Make sure to center it on screen
    R = side_len / (2 * math.sin(math.pi / n_sides))       
    t.setpos(-side_len/2.0, -R * 0.55)  # a bit below center 
    t.setheading(0)
    t.pendown()

    # Draw every side 
    for _ in range(n_sides):
        koch_segment(t, side_len, depth)
        t.left(360.0 / n_sides)

    T.done()

if __name__ == "__main__":
    try:
        x= int(input("Enter the number of sides: "))
        y= float(input("Enter the side length (pixels): "))
        z = int(input("Enter the recursion depth: "))
        if x < 3:
            raise ValueError("Number of sides must be at least 3.")
        if y <= 0 or z < 0:
            raise ValueError("Side length must be > 0 and depth >= 0.")
    except ValueError as e:
        print("Input error:", e)
    else:
        draw_koch_polygon(x, y, z)

