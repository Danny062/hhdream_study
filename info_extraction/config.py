import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass
class Config:
    """Holds all configuration for the application."""
    realm: str
    login_url: str
    login_email: str
    login_password: str
    app_id: str
    material_table_id: str
    attachment_table_id: str
    token: str
    headless: bool = True
    material_number_field: str = "NPR Material Number"
    component_id_field: str = "Component ID#"
    material_cost_field: str = "Material Cost"
    supplier_name_field: str = "Supplier Name(EN)"
    supplier_material_id_field: str = "Supplier Material ID#"
    image_field: str = "Image"
    related_material_field: str = "Related Material"  # Placeholder for the query field


def load_config() -> Config:
    """Loads configuration from environment variables."""
    load_dotenv()
    return Config(
        realm=os.getenv("REALM"),
        login_url=os.getenv("LOGIN_URL"),
        login_email=os.getenv("LOGIN_EMAIL"),
        login_password=os.getenv("LOGIN_PASSWORD"),
        app_id=os.getenv("APP_ID"),
        material_table_id=os.getenv("MATERIAL_TABLE_ID"),
        attachment_table_id=os.getenv("ATTACHMENT_TABLE_ID"),
        token=os.getenv("TOKEN"),
        related_material_field=os.getenv("RELATED_MATERIAL_FIELD", "Related Material"),
        headless=True if (os.getenv("HEADLESS")) == "1" else False,
    )


config = load_config()
