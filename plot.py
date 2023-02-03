"""3D plot"""
import numpy as np
import plotly.graph_objs as go


n_points = 5
days = np.linspace(1, 10, n_points)
jobs = np.linspace(0, 10, n_points)
X, Y = np.meshgrid(days, jobs)
Z = 1 / X**2 + 0.5 * Y**2

fig = go.Figure(data=[go.Surface(x=X, y=Y, z=Z)])
fig.update_layout(scene=dict(xaxis_title="Days", yaxis_title="Jobs", zaxis_title="Benefit"))
fig.show()
