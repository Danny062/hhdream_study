from typing import List, Optional, TypedDict


class Material(TypedDict):
    material_number: str
    component_id: Optional[str]
    cost: Optional[str]
    supplier_name: Optional[str]
    supplier_material_no: Optional[str]
    image_url: Optional[List[str]]
    qa_requirements: Optional[dict]
