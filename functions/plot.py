from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import numpy as np


# Function to plot scatter plot with best-fit line
def plots(ax, x, y, title, xlabel, ylabel, color):
    ax.scatter(x, y, color=color)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    # Fit regression model
    model = LinearRegression()
    x_reshaped = np.array(x).reshape(-1, 1)
    model.fit(x_reshaped, y)
    y_pred = model.predict(x_reshaped)

    # Regression line
    ax.plot(x, y_pred, color='black')

    intercept = model.intercept_
    slope = model.coef_[0]
    r2 = r2_score(y, y_pred)

    ax.text(0.05, 0.95, f'Intercept: {intercept:.2f}\nSlope: {slope:.2f}\nR²: {r2:.2f}', 
            transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.5))

    return ax