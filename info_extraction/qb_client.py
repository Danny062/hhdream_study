import re

from quickbase_client import QuickbaseApiClient

from config import Config, load_config
from model import Material


class QBClient:
    """A client for interacting with the Quickbase API."""
    SRC_RE = re.compile(r'src\s*=\s*["\']([^"\']+)["\']', flags=re.IGNORECASE)

    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.client = QuickbaseApiClient(
            realm_hostname=cfg.realm,
            user_token=cfg.token,
            )

    def _query_table(self, table_id: str, material_number: str):
        """Helper to query a table by material number."""
        where_str = f"{{{self.cfg.related_material_field}.CT.'{material_number}'}}"
        try:
            response = self.client.query(table_id=table_id, where_str=where_str)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Error querying table {table_id} for material {material_number}: {e}")
            return None

    def get_component_data(self, material_number: str) -> dict:
        """Fetches component data for a given material number."""
        response_data = self._query_table(self.cfg.material_table_id, material_number)
        if not response_data or not response_data.get("data"):
            print(f"No component data found for material number: {material_number}")
            return {}

        record = response_data["data"][0]
        component_data = {}
        for field in response_data["fields"]:
            field_id = str(field["id"])
            if field_id in record:
                component_data[field["label"]] = record[field_id]["value"]
        return component_data

    def get_attachments(self, material_number: str) -> list[dict]:
        """Fetches attachment data for a given material number."""
        response_data = self._query_table(self.cfg.attachment_table_id, material_number)
        if not response_data or not response_data.get("data"):
            print(f"No attachments found for material number: {material_number}")
            return []

        attachments = []
        for record in response_data["data"]:
            attachment_info = {}
            for field in response_data["fields"]:
                field_id = str(field["id"])
                if field_id in record:
                    attachment_info[field["label"]] = record[field_id]["value"]
            attachments.append(attachment_info)
        return attachments

    def get_material_details(self, material_number: str) -> Material:
        """Constructs a Material object from component and attachment data."""
        component_data = self.get_component_data(material_number)
        attachments = self.get_attachments(material_number)

        image_urls = []
        for att in attachments:
            image_html = att.get(self.cfg.image_field)
            if image_html and "<img" in image_html.lower():
                match = self.SRC_RE.search(image_html)
                if match:
                    image_urls.append(match.group(1))

        return Material(
            material_number=material_number,
            component_id=component_data.get(self.cfg.component_id_field),
            cost=component_data.get(self.cfg.material_cost_field),
            supplier_name=component_data.get(self.cfg.supplier_name_field),
            image_url=image_urls,
            qa_requirements=None,
            )

if __name__ == "__main__":
    config = load_config()
    qb_client = QBClient(config)
    test_material_number = "6860340"
    material_details = qb_client.get_material_details(test_material_number)
    print(material_details)