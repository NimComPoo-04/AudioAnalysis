import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse

app = FastAPI()
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def redirect_typer():
    return RedirectResponse("index.html")

app.mount("/", StaticFiles(directory="."), name="static")

serv_config = uvicorn.Config(app, host="0.0.0.0", port=8000, ssl_keyfile='key.pem', ssl_certfile='cert.pem')
server = uvicorn.Server(serv_config)
server.run()
