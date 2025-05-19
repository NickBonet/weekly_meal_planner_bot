"""
Basic Discord bot for requesting meal plans and
meal plan reminders from Mealie.
"""

import asyncio
import datetime
import logging
import os

import aiocron
import aiohttp
import discord
import pytz
from dotenv import load_dotenv

from core.generate_meal_plan import get_todays_meal, get_tomorrows_meal

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

load_dotenv()


def parse_meal_data(meal_data, meal_date=None):
    """
    Parse the meal data from Mealie API and format it for Discord.
    Handles multiple meals for a single day.
    """
    if not meal_data:
        return "No meal data found!"

    # If meal_date is not provided, use the current date
    if meal_date is None:
        meal_date = datetime.datetime.now().strftime("%Y-%m-%d")

    # Start with the header message
    message = (
        f"<@&{os.environ.get('WEBHOOK_ROLE_ID')}>\n"
        f"**Reminder: Meal{'s' if len(meal_data) > 1 else ''} for {meal_date}**\n"
        f"(remember to get out any frozen ingredients!)\n\n"
    )

    # Process each meal and add to the message
    for i, meal in enumerate(meal_data, 1):
        meal_name = ""
        meal_slug = ""

        if meal.get("title"):
            meal_name = meal["title"]
        elif meal.get("recipe") is not None:
            meal_name = meal["recipe"]["name"]
            meal_slug = meal["recipe"].get("slug", "")

        # Add meal number if multiple meals
        prefix = f"**Meal {i}:** " if len(meal_data) > 1 else ""
        message += f"{prefix}{meal_name}\n"

        if meal_slug:
            message += f"URL: {os.environ.get('MEALIE_API')}/g/home/r/{meal_slug}\n"

        # Add spacing between meals
        if i < len(meal_data):
            message += "\n"

    return message


async def initialize_webhook():
    async with aiohttp.ClientSession() as session:
        webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"), session=session
        )

        await webhook.send(
            "Meal planner bot started!",
            username="Meal Planner",
        )


@aiocron.crontab("00 09,11 * * *", tz=pytz.timezone(os.environ["TZ"]))
async def send_today_meal_plan_to_discord():
    async with aiohttp.ClientSession() as session:
        todays_meal = get_todays_meal()
        date_today = datetime.datetime.now().strftime("%Y-%m-%d")
        webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"), session=session
        )

        message = parse_meal_data(todays_meal, date_today)

        await webhook.send(message, username="Meal Planner")
    logging.info("Meal data for today sent to Discord!")


@aiocron.crontab("30 20 * * *", tz=pytz.timezone(os.environ["TZ"]))
async def send_tomorrows_meal_plan_to_discord():
    async with aiohttp.ClientSession() as session:
        tomorrow_meal = get_tomorrows_meal()
        date_tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime(
            "%Y-%m-%d"
        )
        webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"), session=session
        )

        message = parse_meal_data(tomorrow_meal, date_tomorrow)

        await webhook.send(message, username="Meal Planner")
    logging.info("Meal data for tomorrow sent to Discord!")


if __name__ == "__main__":
    logging.info("Starting meal planner webhook bot!")

    loop = asyncio.get_event_loop()
    loop.create_task(initialize_webhook())

    # Run the event loop forever
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down meal planner bot.")
