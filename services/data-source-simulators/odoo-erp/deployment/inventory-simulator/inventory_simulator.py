"""Inventory simulation workflow."""

import logging
import random
from datetime import UTC, datetime
from typing import Any

from odoo_client import OdooJson2Client
from settings import Settings

logger = logging.getLogger(__name__)


def _m2o_id(value: Any) -> int | bool:
    if isinstance(value, (list, tuple)):
        return value[0] if value else False
    return value or False


class InventorySimulator:
    def __init__(self, client: OdooJson2Client, settings: Settings):
        self.client = client
        self.settings = settings

    def load_master_data(self) -> dict[str, list[dict]]:
        return {
            "picking_types": self.client.search_read_all(
                "stock.picking.type",
                [["active", "=", True], ["code", "in", ["incoming", "outgoing", "internal"]]],
                ["id", "name", "code", "default_location_src_id", "default_location_dest_id"],
            ),
            "locations": self.client.search_read_all(
                "stock.location",
                [["active", "=", True], ["usage", "in", ["internal", "supplier", "customer"]]],
                ["id", "usage"],
            ),
            "products": self.client.search_read_all(
                "product.product",
                [["active", "=", True], ["is_storable", "=", True]],
                ["id", "display_name", "uom_id"],
            ),
        }

    @staticmethod
    def _location_pair(picking_type: dict, locations: list[dict]) -> tuple[int, int] | None:
        by_usage: dict[str, list[int]] = {}
        for location in locations:
            by_usage.setdefault(location["usage"], []).append(location["id"])

        source_id = _m2o_id(picking_type.get("default_location_src_id"))
        destination_id = _m2o_id(picking_type.get("default_location_dest_id"))
        source_usage, destination_usage = {
            "incoming": ("supplier", "internal"),
            "outgoing": ("internal", "customer"),
            "internal": ("internal", "internal"),
        }[picking_type["code"]]
        source_id = source_id or random.choice(by_usage.get(source_usage, []) or [False])
        candidates = [item for item in by_usage.get(destination_usage, []) if item != source_id]
        destination_id = destination_id or random.choice(candidates or [False])
        if not source_id or not destination_id or source_id == destination_id:
            return None
        return int(source_id), int(destination_id)

    @staticmethod
    def _move_values(products: list[dict], source_id: int, destination_id: int) -> list[list[Any]]:
        selected = random.sample(products, random.randint(1, min(3, len(products))))
        return [[0, 0, {
            "name": product["display_name"],
            "product_id": product["id"],
            "product_uom": _m2o_id(product["uom_id"]),
            "product_uom_qty": random.randint(1, 10),
            "location_id": source_id,
            "location_dest_id": destination_id,
        }] for product in selected]

    def build_picking_values(self, data: dict[str, list[dict]]) -> dict:
        products = [item for item in data["products"] if _m2o_id(item.get("uom_id"))]
        usable_types = [
            (item, pair)
            for item in data["picking_types"]
            if (pair := self._location_pair(item, data["locations"]))
        ]
        if not usable_types or not products:
            raise RuntimeError("Missing usable picking types, locations, or products")

        picking_type, (source_id, destination_id) = random.choice(usable_types)
        reference = datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        return {
            "picking_type_id": picking_type["id"],
            "location_id": source_id,
            "location_dest_id": destination_id,
            "origin": f"EXT-INV-SIM-{reference}",
            "move_ids": self._move_values(products, source_id, destination_id),
        }

    def push_batch(self) -> None:
        logger.info("Starting inventory API push, batch_size=%s", self.settings.batch_size)
        data = self.load_master_data()
        created = 0
        failed = 0
        for attempt in range(1, self.settings.batch_size * 3 + 1):
            if created >= self.settings.batch_size:
                break
            try:
                picking_ids = self.client.create_picking(self.build_picking_values(data))
                created += 1
                logger.info("Created picking %s (%s/%s)", picking_ids, created, self.settings.batch_size)
            except Exception:
                failed += 1
                logger.exception("Failed to create picking on attempt %s", attempt)
        logger.info("Finished inventory API push: created=%s failed=%s", created, failed)
