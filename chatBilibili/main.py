import uvicorn
from fastapi import FastAPI

import config
from router import embedding_router

app = FastAPI()
app.include_router(router=embedding_router)


if __name__ == "__main__":
    host = config.service_settings.get('host', '127.0.0.1')
    port = int(config.service_settings.get('port', 7880))

    uvicorn.run(app, host=host, port=port)