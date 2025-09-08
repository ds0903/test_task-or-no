from fastapi import FastAPI
from app.api.versia1.user_credits import router as credits_router
from app.api.versia1.plans import router as plans_router
from app.api.versia1.performance import router as perf_router


app = FastAPI(title="Credit Service")
app.include_router(credits_router, prefix="/api/versia1")
app.include_router(plans_router,   prefix="/api/versia1")
app.include_router(perf_router,    prefix="/api/versia1")


@app.get("/ping")
def ping():
    return {"ok": True}

