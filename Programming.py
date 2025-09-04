import turtle

def draw_edge(length, depth):
    if depth == 0:
        turtle.forward(length)
    else:
        length /= 3.0
        draw_edge(length, depth-1)    # First third
        turtle.right(60)              # turn inward
        draw_edge(length, depth-1)    # middle segment up side of triangle
        turtle.left(120)              # turn inward to complete triangle
        draw_edge(length, depth-1)    # middle segment down side of triangle
        turtle.right(60)              # back to original direction
        draw_edge(length, depth-1)    # last third

def draw_polygon(sides, length, depth):
    for _ in range(sides):
        draw_edge(length, depth)
        turtle.right(360 / sides)

if __name__ == "__main__":
    sides = int(input("Enter number of sides: "))
    length = int(input("Enter side length: "))
    depth = int(input("Enter recursion depth: "))

    turtle.speed(0)
    turtle.hideturtle()
    draw_polygon(sides, length, depth)
    turtle.done()