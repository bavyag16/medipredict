from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from app.predict import predict, SYMPTOMS
from app.doctors import find_doctors
from app.appointments import (save_appointment, get_appointment,
                              build_letter, get_all_appointments)

app = FastAPI(title="Disease Prediction & Doctor Matching")

class SymptomRequest(BaseModel):
    symptoms: list[str]

class BookingRequest(BaseModel):
    patient: str
    doctor: str
    specialty: str
    hospital: str = ""
    date: str
    time: str
    disease: str = ""
    confidence: float = 0
    symptoms: list[str] = []

@app.get("/symptoms")
def get_symptoms():
    return SYMPTOMS

@app.post("/predict")
def run_prediction(req: SymptomRequest):
    result = predict(req.symptoms)
    if not result["low_confidence"]:
        result["doctors"] = find_doctors(result["disease"])
    return result

@app.post("/book")
def book(req: BookingRequest):
    appt = save_appointment(req.patient, req.doctor, req.specialty, req.hospital,
                            req.date, req.time, req.disease, req.confidence, req.symptoms)
    return {"status": "confirmed", "appointment": appt}

@app.get("/appointments")
def list_appointments():
    return get_all_appointments()

@app.get("/appointment/{appt_id}/letter")
def appointment_letter(appt_id: int):
    appt = get_appointment(appt_id)
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    pdf_bytes = build_letter(appt)
    headers = {"Content-Disposition": f'attachment; filename="appointment_{appt_id}.pdf"'}
    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)

app.mount("/", StaticFiles(directory="static", html=True), name="static")