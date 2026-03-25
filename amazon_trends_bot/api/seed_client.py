from __future__ import annotations

from amazon_trends_bot.config import Settings
from amazon_trends_bot.domain.models import ProductCandidate


class SeedProductSource:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_trending_products(self, limit: int) -> list[ProductCandidate]:
        samples = [
            ProductCandidate(
                asin="SEEDPORT01",
                title="Portable Blender for Smoothies and Travel",
                brand="BlendGo",
                category="Home & Kitchen",
                estimated_sales=3200,
                price=34.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDPORT01",
            ),
            ProductCandidate(
                asin="SEEDDESK02",
                title="Desk Organizer with Drawer for Home Office",
                brand="NeatNest",
                category="Office Products",
                estimated_sales=2800,
                price=22.49,
                url=f"{self.settings.amazon_base_url}/dp/SEEDDESK02",
            ),
            ProductCandidate(
                asin="SEEDLED03",
                title="LED Strip Lights for Bedroom Decor",
                brand="Glowly",
                category="Home & Kitchen",
                estimated_sales=4100,
                price=18.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDLED03",
            ),
            ProductCandidate(
                asin="SEEDFAN04",
                title="Mini Desk Fan USB Rechargeable",
                brand="CoolWave",
                category="Home & Kitchen",
                estimated_sales=2600,
                price=19.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDFAN04",
            ),
            ProductCandidate(
                asin="SEEDPOST05",
                title="Posture Corrector Back Support Brace",
                brand="AlignFit",
                category="Sports & Outdoors",
                estimated_sales=3700,
                price=27.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDPOST05",
            ),
            ProductCandidate(
                asin="SEEDMUG06",
                title="Self Heating Coffee Mug Warmer",
                brand="WarmSip",
                category="Home & Kitchen",
                estimated_sales=1900,
                price=29.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDMUG06",
            ),
            ProductCandidate(
                asin="SEEDWALK07",
                title="Walking Pad Treadmill for Home Office",
                brand="StrideLab",
                category="Sports & Outdoors",
                estimated_sales=2400,
                price=249.0,
                url=f"{self.settings.amazon_base_url}/dp/SEEDWALK07",
            ),
            ProductCandidate(
                asin="SEEDSKIN08",
                title="Ice Roller for Face and Skin Care",
                brand="FreshMuse",
                category="Beauty & Personal Care",
                estimated_sales=3500,
                price=15.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDSKIN08",
            ),
            ProductCandidate(
                asin="SEEDMEAL09",
                title="Glass Meal Prep Containers with Lids",
                brand="PrepRoot",
                category="Home & Kitchen",
                estimated_sales=2100,
                price=31.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDMEAL09",
            ),
            ProductCandidate(
                asin="SEEDSUN10",
                title="Sunscreen Stick for Outdoor Sports",
                brand="SunTrail",
                category="Beauty & Personal Care",
                estimated_sales=3000,
                price=12.99,
                url=f"{self.settings.amazon_base_url}/dp/SEEDSUN10",
            ),
        ]
        return samples[:limit]

