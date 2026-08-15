from contextlib import asynccontextmanager
from fastapi import FastAPI,Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from .config import BASE_DIR,TELEGRAM_USERNAME
from .document import load_document
from .routes.web import router as web_router
from .routes.telegram import router as telegram_router
from .telegram_service import configure_webhook
@asynccontextmanager
async def lifespan(app):
    load_document()
    try:await configure_webhook();print('Webhook do Telegram verificado.')
    except Exception as e:print(f'Falha ao configurar Telegram: {type(e).__name__}')
    yield
app=FastAPI(title='Chatbot de Gestão',version='3.0.0',docs_url=None,redoc_url=None,lifespan=lifespan)
app.mount('/static',StaticFiles(directory=BASE_DIR/'static'),name='static')
templates=Jinja2Templates(directory=BASE_DIR/'templates')
app.include_router(web_router);app.include_router(telegram_router)
@app.get('/',response_class=HTMLResponse)
async def home(request:Request):return templates.TemplateResponse(request=request,name='index.html',context={'telegram_username':TELEGRAM_USERNAME})
