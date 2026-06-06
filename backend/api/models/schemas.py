from pydantic import BaseModel

class ProcessRequest(BaseModel):
    input_folder: str
    output_folder: str