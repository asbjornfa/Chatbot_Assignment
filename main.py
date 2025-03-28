from fastapi import FastAPI

import mainAi

app = FastAPI()


app.include_router(mainAi.router, prefix="/AI")