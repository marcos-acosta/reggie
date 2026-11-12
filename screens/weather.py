from screens import screen
from services import weather
from ui import Column, Row, Text


@screen(refresh=1800)
def weather_report() -> Column:
    weather_report = weather.fetch_weather()
    return Column(
        Text(f"{weather_report.currentTempF}°", font="helvR12"),
        Row(
            Text(f"{weather_report.minTempF}°", font="tom-thumb", color="#8080ff"),
            Text(f"{weather_report.maxTempF}°", font="tom-thumb", color="#ff2020"),
            gap=2,
        ),
        gap=1,
        align="center",
        justify="center",
    )
