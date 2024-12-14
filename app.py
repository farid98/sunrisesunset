import streamlit as st
from datetime import date, datetime, timedelta
from suntime import Sun, SunTimeException
import pytz
import plotly.graph_objects as go


# Function to calculate sunrise and sunset data
def calculate_sunrise_sunset():
    # Islamabad's coordinates
    latitude = 33.6844
    longitude = 73.0479

    # Initialize Sun object for Islamabad
    sun = Sun(latitude, longitude)

    # Timezone for Islamabad
    timezone = pytz.timezone("Asia/Karachi")

    # Generate dates for the year 2025
    start_date = date(2025, 1, 1)
    end_date = date(2025, 12, 31)
    delta = timedelta(days=1)

    # Prepare lists to store data
    dates = []
    sunrise_hours = []
    sunset_hours = []
    sunrise_times_am_pm = []
    sunset_times_am_pm = []
    daylight_hours = []

    # Calculate sunrise and sunset times for each day
    current_date = start_date
    while current_date <= end_date:
        try:
            # Convert the date to a datetime object
            current_datetime = datetime.combine(current_date, datetime.min.time())

            # Get sunrise and sunset times in UTC
            sunrise = sun.get_sunrise_time(current_datetime)
            sunset = sun.get_sunset_time(current_datetime)

            # Convert to local time
            sunrise_local = sunrise.astimezone(timezone)
            sunset_local = sunset.astimezone(timezone)

            # Calculate daylight duration
            daylight_duration = (
                sunset_local - sunrise_local
            ).seconds / 3600  # in hours

            # Append data to lists
            dates.append(current_date)
            sunrise_hours.append(sunrise_local.hour + sunrise_local.minute / 60)
            sunset_hours.append(sunset_local.hour + sunset_local.minute / 60)
            sunrise_times_am_pm.append(sunrise_local.strftime("%I:%M %p"))
            sunset_times_am_pm.append(sunset_local.strftime("%I:%M %p"))
            daylight_hours.append(daylight_duration)
        except SunTimeException as e:
            print(f"Error: {e} on {current_date}")
        current_date += delta

    return (
        dates,
        sunrise_hours,
        sunset_hours,
        sunrise_times_am_pm,
        sunset_times_am_pm,
        daylight_hours,
    )


# Main Streamlit app
def main():
    st.title("Sunrise and Sunset Times in Islamabad for 2025")

    # Calculate sunrise and sunset data
    (
        dates,
        sunrise_hours,
        sunset_hours,
        sunrise_times_am_pm,
        sunset_times_am_pm,
        daylight_hours,
    ) = calculate_sunrise_sunset()

    # Function to format y-axis ticks as AM/PM
    def format_hour(hour):
        hour_24 = int(hour)
        minute = int((hour - hour_24) * 60)
        if hour_24 == 24:  # Special case for 24
            hour_24 = 23
            minute = 59
        time_obj = datetime(1, 1, 1, hour_24, minute)
        return time_obj.strftime("%I:%M %p")

    # Generate custom tick labels for the y-axis
    y_ticks = [i for i in range(0, 24, 2)]  # Tick every 2 hours, exclude 24
    y_tick_labels = [format_hour(h) for h in y_ticks]

    # Create an interactive plot using Plotly
    fig = go.Figure()

    # Add sunrise and sunset trace with shared tooltips
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=sunrise_hours,
            mode="lines",
            name="Sunrise",
            line=dict(color="orange"),
            hoverinfo="skip",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=sunset_hours,
            mode="lines",
            name="Sunset",
            line=dict(color="purple"),
            hoverinfo="skip",
        )
    )

    # Add a shared hover layer for sunrise, sunset, and daylight
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[12] * len(dates),  # Dummy y-values to anchor the hover tooltip
            mode="markers",
            marker=dict(opacity=0),
            hovertemplate=(
                "<b>Sunrise:</b> %{customdata[0]}<br>"
                "<b>Sunset:</b> %{customdata[1]}<br>"
                "<b>Daylight hours:</b> %{customdata[2]:.2f} hours<extra></extra>"
            ),
            customdata=list(
                zip(sunrise_times_am_pm, sunset_times_am_pm, daylight_hours)
            ),
            showlegend=False,  # Hide this trace from the legend
        )
    )

    # Update layout with inverted y-axis
    fig.update_layout(
        title="Sunrise and Sunset Times in Islamabad for 2025 (Local Time)",
        xaxis_title="Date",
        yaxis_title="Time of Day",
        hovermode="x unified",
        template="plotly_white",
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        xaxis=dict(tickformat="%b %d", tickangle=45),
        yaxis=dict(
            tickmode="array",
            tickvals=y_ticks,
            ticktext=y_tick_labels,
            range=[24, 0],  # Invert the range to flip the axis
        ),
    )

    # Display the interactive plot in Streamlit
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
