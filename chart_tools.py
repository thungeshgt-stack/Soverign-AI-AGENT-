"""
Plotly chart generation for sensor trends.
"""
import plotly.graph_objects as go
from config.settings import SENSOR_THRESHOLDS


def generate_chart(df, field: str, x_field: str = None):
    """Return a Plotly Figure for a sensor field trend, with threshold line if configured."""
    if field not in df.columns:
        return None
    x = df[x_field] if x_field and x_field in df.columns else df.index

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x, y=df[field], mode="lines+markers", name=field.title(),
        line=dict(color="#38BDF8", width=2), marker=dict(size=4),
    ))

    threshold_cfg = SENSOR_THRESHOLDS.get(field)
    if threshold_cfg:
        fig.add_hline(
            y=threshold_cfg["max"], line_dash="dash", line_color="#F87171",
            annotation_text=f"Threshold ({threshold_cfg['max']} {threshold_cfg['unit']})",
            annotation_position="top left",
        )

    fig.update_layout(
        title=f"{field.title()} Trend",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(20,25,35,0.4)",
        font=dict(color="#E5E7EB", family="Arial"),
        margin=dict(l=40, r=20, t=50, b=40),
        height=320,
    )
    return fig
