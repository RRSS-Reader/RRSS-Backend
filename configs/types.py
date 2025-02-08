from pydantic import BaseModel, ConfigDict


class ConfigDataModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class DBConfigModel(ConfigDataModel):
    name: str
