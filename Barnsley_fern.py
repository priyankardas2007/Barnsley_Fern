import matplotlib.pyplot as plt
import random

# Starting point
x, y = 0.0, 0.0

# Prepare plot
plt.ion()  # Turn on interactive mode
fig, ax = plt.subplots(figsize=(6, 10))
ax.set_title("Barnsley Fern")
ax.axis('off')

x_data = []
y_data = []

# Number of iterations
iterations = 100000

for i in range(iterations):
    r = random.random()

    if r < 0.01:
        x_new = 0.0
        y_new = 0.16 * y
    elif r < 0.86:
        x_new = 0.85 * x + 0.04 * y
        y_new = -0.04 * x + 0.85 * y + 1.6
    elif r < 0.93:
        x_new = 0.2 * x - 0.26 * y
        y_new = 0.23 * x + 0.22 * y + 1.6
    else:
        x_new = -0.15 * x + 0.28 * y
        y_new = 0.26 * x + 0.24 * y + 0.44

    x, y = x_new, y_new

    x_data.append(x)
    y_data.append(y)

    # Update plot periodically
    if i % 1000 == 0 and i > 0:  # Reduced update frequency for better performance
        ax.clear()
        ax.set_title("Barnsley Fern")
        ax.axis('off')
        ax.scatter(x_data, y_data, s=0.2, c='green', marker='.')
        plt.pause(0.001)

# Turn off interactive mode and display final plot
plt.ioff()
ax.clear()
ax.set_title("Barnsley Fern - Final")
ax.axis('off')
ax.scatter(x_data, y_data, s=0.2, c='green', marker='.')
plt.show()
