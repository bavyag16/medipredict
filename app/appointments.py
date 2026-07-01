import json, os
from datetime import datetime
from fpdf import FPDF
from fpdf.enums import XPos, YPos

FILE = "app/appointments.json"

def _clean(text):
    return str(text).encode("latin-1", "ignore").decode("latin-1").strip()

def save_appointment(patient, doctor, specialty, hospital, date, time,
                     disease="", confidence=0, symptoms=None):
    appointments = []
    if os.path.exists(FILE):
        with open(FILE) as f:
            appointments = json.load(f)
    appt = {
        "id": len(appointments) + 1,
        "patient": patient, "doctor": doctor, "specialty": specialty,
        "hospital": hospital, "date": date, "time": time,
        "disease": disease, "confidence": confidence, "symptoms": symptoms or [],
        "booked_at": datetime.now().isoformat(timespec="seconds"),
    }
    appointments.append(appt)
    with open(FILE, "w") as f:
        json.dump(appointments, f, indent=2)
    return appt

def get_appointment(appt_id):
    for a in get_all_appointments():
        if a["id"] == appt_id:
            return a
    return None

def get_all_appointments():
    if not os.path.exists(FILE):
        return []
    with open(FILE) as f:
        return json.load(f)

def build_letter(appt):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(13, 148, 136)
    pdf.rect(0, 0, 210, 34, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 9)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 10, "MediPredict", align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_xy(0, 21)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, "Appointment Confirmation", align="C")

    pdf.set_text_color(13, 148, 136)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_xy(20, 48)
    pdf.cell(0, 10, f"Appointment ID:  #{appt['id']}", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    rows = [
        ("Patient Name", appt["patient"]),
        ("Doctor", appt["doctor"]),
        ("Specialty", appt["specialty"]),
        ("Hospital", appt.get("hospital", "")),
        ("Date", appt["date"]),
        ("Time", appt["time"]),
        ("Booked On", appt["booked_at"]),
    ]
    for label, value in rows:
        pdf.set_x(20)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(71, 85, 105)
        pdf.cell(45, 9, label + ":")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(0, 9, _clean(value), new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(4)
    pdf.set_draw_color(203, 213, 225)
    pdf.line(20, pdf.get_y(), 190, pdf.get_y())
    pdf.ln(8)

    pdf.set_x(20)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(170, 6,
        "Please arrive 10 minutes early and bring a valid photo ID. "
        "This is a student decision-support demo, not a real medical appointment.")
    return bytes(pdf.output())