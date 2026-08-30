from pydantic import BaseModel, Field


class DemandForecastRequest(BaseModel):
    store_id: int = Field(..., gt=0)
    product_id: int = Field(..., gt=0)