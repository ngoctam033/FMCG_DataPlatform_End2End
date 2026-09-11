"""Application bootstrap and scheduling."""

import logging

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger

from inventory_simulator import InventorySimulator
from odoo_client import OdooJson2Client
from settings import Settings


def run_service() -> None:
    settings = Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    simulator = InventorySimulator(OdooJson2Client(settings), settings)
    if settings.run_on_start:
        simulator.push_batch()

    scheduler = BlockingScheduler(timezone=settings.timezone)
    scheduler.add_job(
        simulator.push_batch,
        CronTrigger.from_crontab(settings.cron, timezone=settings.timezone),
        id="inventory_api_push",
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()
