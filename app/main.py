from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import files


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=files.router, tags=["File"], prefix='/api/file')

@app.get("/api/healtcheck")
def root():
    return {"message": "FastAPI OK"}
