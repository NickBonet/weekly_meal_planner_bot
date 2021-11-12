"""Basic Discord bot for requesting meal plans and meal plan reminders from Mealie."""
import os
import asyncio
import aiohttp
import aiocron
from discord import Webhook, AsyncWebhookAdapter
from core.generate_meal_plan import get_random_recipes, get_todays_meal


@aiocron.crontab('0 09 * * 5')
async def send_new_meal_plan_to_discord():
    async with aiohttp.ClientSession() as session:
        webhook = Webhook.from_url(os.environ.get('WEBHOOK_URL'), adapter=AsyncWebhookAdapter(session))
        await webhook.send("<@&" + os.environ.get('WEBHOOK_ROLE_ID') + ">\n**Recipes for next week:**\n" +
                           '\n'.join([str(elem.name + " (URL: " + elem.recipe_url + ")")
                                      for elem in get_random_recipes()]),
                           username='Meal Planner')
    print('Meal plan for the week sent to Discord!')


@aiocron.crontab('0 08 * * *')
async def send_today_meal_plan_to_discord():
    async with aiohttp.ClientSession() as session:
        todays_meal = get_todays_meal()
        webhook = Webhook.from_url(os.environ.get('WEBHOOK_URL'), adapter=AsyncWebhookAdapter(session))
        await webhook.send("<@&" + os.environ.get('WEBHOOK_ROLE_ID') + ">\n**Reminder: Meal for today**\n" +
                           "(remember to get out any frozen ingredients!)\n" +
                           todays_meal['name'] + "\n" +
                           "URL: " + os.environ.get('MEALIE_API') + "/recipe/" + todays_meal['slug'],
                           username='Meal Planner')
    print('Meal data for today sent to Discord!')

print('Starting meal planner webhook bot!')
asyncio.get_event_loop().run_forever()
