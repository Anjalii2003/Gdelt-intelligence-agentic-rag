from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from FlagEmbedding import BGEM3FlagModel

app = FastAPI(title="GDELT BGE-M3 Embedding Service")

model = None


class EmbeddingRequest(BaseModel):
    text: str


@app.on_event("startup")
def load_model():
    global model
    print("Loading BGE-M3 model...")
    model = BGEM3FlagModel("BAAI/bge-m3", use_fp16=False)
    print("BGE-M3 model loaded successfully!")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}


@app.post("/embed")
def create_embedding(request: EmbeddingRequest):
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")

    result = model.encode([request.text], return_dense=True)
    embedding = result["dense_vecs"][0].tolist()

    return {
        "embedding": embedding,
        "dimension": len(embedding),
        "model": "BAAI/bge-m3"
    }
