import pandera as pa
from pandera.typing import Series

# カラム名を管理するために使用


class TranscriptSchema(pa.SchemaModel):
    speaker: Series[str] = pa.Field(nullable=False)
    start: Series[float] = pa.Field(nullable=False)
    end: Series[float] = pa.Field(nullable=False)
    text: Series[str] = pa.Field(nullable=False)


class AnnotateSchema(pa.SchemaModel):
    speaker: Series[str] = pa.Field(nullable=False)
    start: Series[float] = pa.Field(nullable=False, alias="start_time")
    end: Series[float] = pa.Field(nullable=False, alias="end_time")
