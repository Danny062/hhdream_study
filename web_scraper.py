import asyncio
from pathlib import Path

import nodriver as uc

from config import Config


class WebScraper:
    """Manages browser interactions for scraping data."""

    def __init__(self, cfg: Config, headless: bool = False):
        self.cfg = cfg
        self.headless = headless
        self.browser = None
        self.page = None

    async def __aenter__(self):
        """Initializes the browser and logs in."""
        self.browser = await uc.start(headless=self.headless)
        self.page = await self.browser.get(self.cfg.login_url)
        await self._login()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Closes the browser."""
        if self.browser:
            print("Closing browser...")
            self.browser.stop()

    async def _login(self):
        """Performs the login sequence, handling a potential two-step flow."""
        print("Attempting to log in...")
        await self.page.sleep(3)

        # --- Email Step ---
        await asyncio.sleep(3)
        email_input = await self.page.select('input[name="email"], input[id*="email"], input[type="email"]')
        if not email_input:
            raise Exception("Email input field not found.")
        await email_input.send_keys(self.cfg.login_email)
        print("Email entered.")

        # --- Password Step ---
        pw_input = await self.page.select('input[name="password"], input[id*="password"], input[type="password"]')
        if not pw_input:
            raise Exception("Password input field not found.")
        await pw_input.send_keys(self.cfg.login_password)
        print("Password entered.")

        # --- Final Login/Submit Step ---
        login_button = await self.page.select('button[type="submit"], input[type="submit"], button[id*="login"]')
        if not login_button:
            raise Exception("Login button not found.")
        await login_button.click()
        print("Clicked final login button.")

        await self.page.sleep(10)  # Wait for login to process

    def _build_record_url(self, rid: int) -> str:
        """Builds the URL for a specific Quickbase record."""
        return (
            f"https://{self.cfg.realm}/nav/app/{self.cfg.app_id}/table/"
            f"{self.cfg.material_table_id}/action/dr?rid={rid}"
        )

    async def get_qa_html(self, component_id: int) -> str:
        """Navigates to a component page and returns its HTML content."""
        target_url = self._build_record_url(component_id)
        print(f"Navigating to component page: {target_url}")
        await self.page.get(target_url)
        await self.page.sleep(5)
        await asyncio.sleep(3)
        html = await self.page.get_content()
        return html

    async def download_image(self, image_url: str, save_path: Path):
        """Downloads an image from a given URL."""
        print(f"Downloading image from {image_url} to {save_path}")
        try:
            # Using a new tab for download to avoid navigation issues
            await self.page.set_download_path(Path(save_path).parent)
            await self.page.get(image_url)
            await self.page.sleep(5)

            retry = 0
            while not save_path.exists() and retry < 5:
                await self.page.download_file(url=image_url, filename=Path(save_path.name))
                await asyncio.sleep(3)
                retry += 1

            # This part assumes nodriver's default download behavior.
            # You may need to find and rename the file if it's not saved with the correct name.
            print(f"Image downloaded successfully to default directory.")

        except Exception as e:
            print(f"Failed to download {image_url}: {e}")
