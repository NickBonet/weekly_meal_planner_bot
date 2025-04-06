"""
Basic Discord bot for requesting meal plans and
meal plan reminders from Mealie.
"""

import asyncio
import logging
import os
import pytz

import aiocron
import aiohttp
import discord
from dotenv import load_dotenv

from core.generate_meal_plan import get_todays_meal

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
)

load_dotenv()


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
        webhook = discord.Webhook.from_url(
            os.environ.get("WEBHOOK_URL"), session=session
        )

        if not todays_meal:
            logging.warning("No meal data for today!")
            message = (
                "<@&"
                + os.environ.get("WEBHOOK_ROLE_ID")
                + ">\n**No meal data found for today!**\n"
            )

            await webhook.send(message, username="Meal Planner")
            return

        name = ""
        slug = ""

        if todays_meal[0]["title"]:
            name = todays_meal[0]["title"]
        elif todays_meal[0]["recipe"] is not None:
            name = todays_meal[0]["recipe"]["name"]
            slug = todays_meal[0]["recipe"]["slug"]

        message = (
            "<@&"
            + os.environ.get("WEBHOOK_ROLE_ID")
            + ">\n**Reminder: Meal for today**\n"
            + "(remember to get out any frozen ingredients!)\n"
            + name
            + "\n"
        )
        if slug:
            message = (
                message + "URL: " + os.environ.get("MEALIE_API") + "/g/home/r/" + slug
            )

        await webhook.send(message, username="Meal Planner")
    logging.info("Meal data for today sent to Discord!")


if __name__ == "__main__":
    logging.info("Starting meal planner webhook bot!")

    loop = asyncio.get_event_loop()
    loop.create_task(initialize_webhook())

    # Run the event loop forever
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logging.info("Shutting down meal planner bot.")
