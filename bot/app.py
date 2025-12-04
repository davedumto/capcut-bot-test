from fastapi import FastAPI
from fastapi.responses import JSONResponse
import logging

app = FastAPI(title="CapCut Password Reset Bot")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the reset password route
from routes.reset_password import router as reset_password_router

# Include the router
app.include_router(reset_password_router, prefix="/bot")

@app.get("/health")
async def health_check():
    return {"status": "Bot service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)