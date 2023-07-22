from fastapi import FastAPI

from api import router


app = FastAPI(
    title="Book App Server",
    description="Book App",
    version="0.1.0",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    }
)

app.include_router(router, tags=["Images"])
