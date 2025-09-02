from fastapi import FastAPI, HTTPException, Request

from vidaplus.controllers import admissions, appointments, auth, beds, healthcare_professionals, patients, stock, units
from vidaplus.main.exceptions import ApplicationError

app = FastAPI(title='SSGHSS VidaPlus')
app.include_router(admissions.router)
app.include_router(appointments.router)
app.include_router(auth.router)
app.include_router(beds.router)
app.include_router(healthcare_professionals.router)
app.include_router(patients.router)
app.include_router(stock.router)
app.include_router(units.router)


@app.exception_handler(ApplicationError)
def application_error_handler(request: Request, exc: ApplicationError) -> None:
    raise HTTPException(status_code=exc.code, detail=str(exc))
