from transformers import AutoProcessor, AutoModelForTableExtraction

MODEL_DIR = "/opt/models/table-transformer"

class TableTransformerWorker:
  def __init__(self):
    self.processor = AutoProcessor.from_pretrained(
      MODEL_DIR,
      local_files_only=True
    )
    self.model = AutoModelForTableExtraction.from_pretrained(
      MODEL_DIR,
      local_files_only=True
    )
    print("Table Transformer loaded from", MODEL_DIR)
