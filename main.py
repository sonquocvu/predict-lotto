from fastapi import FastAPI, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database import models
from database.database import local_session, engine
from predictLotto import PredictVietlottNumbers
from collectData import CollectWonNumbers
from pathlib import Path
import uvicorn


models.Base.metadata.create_all(bind=engine)

app = FastAPI()

BASE_PATH = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_PATH / "templates"))


def get_db():
    db = local_session()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("lotto.html", {"request": request})


@app.get("/predict/{Type}")
async def collectLotto(Type, Db: Session = Depends(get_db)):
    Results = []
    CollectLottoNumbers = CollectWonNumbers(Results, Type, Db)
    CollectLottoNumbers.Start()

    Predict = PredictVietlottNumbers(Results, Type)
    res = Predict.Start()
    res = ' '.join(map(str, res))

    return {"You should buy the numbers:": res}

if __name__ == "__main__":
    uvicorn.run("__main__:app", host="127.0.0.1", port=8000, reload=True)
