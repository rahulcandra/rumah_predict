import os
import joblib
import numpy as np
import pandas as pd
from flask import current_app


# ── Konstanta kolom (sesuai dataset Salary_Data_Based_country_and_race.csv) ───
# Catatan: nama kolom di bawah adalah SETELAH pipeline cleaning di notebook
# (spasi → underscore), sesuai work_df.columns yang masuk ke training.
NUMERIC_FEATURES = ["Age", "Years_of_Experience"]
CATEGORICAL_FEATURES = ["Gender", "Education_Level", "Job_Title", "Country", "Race"]
FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES


# ── Singleton loader ──────────────────────────────────────────────────────────
_pipeline = None
_metadata = None


def _get_model_dir() -> str:
    return os.path.join(current_app.root_path, "static", "models")


def load_model():
    global _pipeline, _metadata

    model_dir     = _get_model_dir()
    pipeline_path = os.path.join(model_dir, "salary_prediction_model.pkl")
    metadata_path = os.path.join(model_dir, "model_metadata.pkl")

    if not os.path.exists(pipeline_path):
        raise FileNotFoundError(
            f"Model tidak ditemukan: {pipeline_path}\n"
            "Pastikan file .pkl sudah ada di app/static/models/"
        )
    if not os.path.exists(metadata_path):
        raise FileNotFoundError(f"Metadata tidak ditemukan: {metadata_path}")

    _pipeline = joblib.load(pipeline_path)
    _metadata = joblib.load(metadata_path)
    current_app.logger.info("✅ Salary prediction model loaded successfully.")


def get_metadata() -> dict:
    if _metadata is None:
        load_model()
    return _metadata


def get_pipeline():
    if _pipeline is None:
        load_model()
    return _pipeline


# ── Validasi input ────────────────────────────────────────────────────────────
class PredictionInputError(ValueError):
    pass


def validate_input(form_data: dict) -> dict:
    errors = []
    cleaned = {}

    # ── Kolom kategorikal ─────────────────────────────────────────────────────
    for col in CATEGORICAL_FEATURES:
        val = form_data.get(col, "").strip()
        if not val:
            errors.append(f"'{col}' tidak boleh kosong.")
        else:
            cleaned[col] = val

    # ── Age ───────────────────────────────────────────────────────────────────
    age_raw = form_data.get("Age", "").strip()
    if not age_raw:
        errors.append("'Age' tidak boleh kosong.")
    else:
        try:
            age = float(age_raw)
            if age < 18 or age > 70:
                errors.append("'Age' harus antara 18 dan 70.")
            else:
                cleaned["Age"] = age
        except ValueError:
            errors.append("'Age' harus berupa angka.")

    # ── Years of Experience ───────────────────────────────────────────────────
    years_raw = form_data.get("Years_of_Experience", "").strip()
    if not years_raw:
        errors.append("'Years_of_Experience' tidak boleh kosong.")
    else:
        try:
            years = float(years_raw)
            if years < 0 or years > 36:
                errors.append("'Years_of_Experience' harus antara 0 dan 36.")
            else:
                cleaned["Years_of_Experience"] = years
        except ValueError:
            errors.append("'Years_of_Experience' harus berupa angka.")

    if errors:
        raise PredictionInputError(" | ".join(errors))

    return cleaned


# ── Core prediction ───────────────────────────────────────────────────────────
def predict_salary(form_data: dict) -> dict:
    result = {
        "success":       False,
        "prediction":    None,
        "formatted":     "",
        "problem_type":  "",
        "input_summary": {},
        "error":         None,
    }

    try:
        cleaned  = validate_input(form_data)
        meta     = get_metadata()
        pipeline = get_pipeline()

        feature_cols = meta.get("feature_columns", FEATURE_COLUMNS)
        input_df = pd.DataFrame([{col: cleaned.get(col) for col in feature_cols}])

        raw_pred     = pipeline.predict(input_df)[0]
        problem_type = meta.get("problem_type", "regression")

        if problem_type == "regression":
            prediction_val = float(raw_pred)
            formatted      = f"${prediction_val:,.2f}"
        else:
            prediction_val = str(raw_pred)
            formatted      = prediction_val

        result.update({
            "success":       True,
            "prediction":    prediction_val,
            "formatted":     formatted,
            "problem_type":  problem_type,
            "input_summary": cleaned,
        })

    except PredictionInputError as e:
        result["error"] = str(e)
    except FileNotFoundError as e:
        current_app.logger.error(f"Model file error: {e}")
        result["error"] = "Model belum tersedia. Hubungi administrator."
    except Exception as e:
        current_app.logger.exception(f"Prediction error: {e}")
        result["error"] = f"Terjadi kesalahan saat prediksi: {str(e)}"

    return result


# ── Helpers untuk template / dropdown ────────────────────────────────────────
def get_field_options() -> dict:
    """
    Opsi dropdown sesuai nilai unik di dataset asli.
    Job Title dikelompokkan agar UI tidak terlalu panjang;
    pipeline sudah handle 'Other' untuk nilai di luar top-25.
    """
    return {
        "Gender": ["Male", "Female", "Other"],

        "Education_Level": [
            "High School",
            "Bachelor's",
            "Bachelor's Degree",
            "Master's",
            "Master's Degree",
            "PhD",
        ],

        # Semua 175 job title unik dari dataset
        "Job_Title": [
            "Account Manager", "Accountant", "Administrative Assistant",
            "Back end Developer", "Business Analyst",
            "Business Development Manager", "Business Intelligence Analyst",
            "CEO", "Chief Data Officer", "Chief Technology Officer",
            "Content Marketing Manager", "Copywriter", "Creative Director",
            "Customer Service Manager", "Customer Service Rep",
            "Customer Service Representative", "Customer Success Manager",
            "Customer Success Rep", "Data Analyst", "Data Entry Clerk",
            "Data Scientist", "Delivery Driver", "Developer",
            "Digital Content Producer", "Digital Marketing Manager",
            "Digital Marketing Specialist", "Director",
            "Director of Business Development", "Director of Data Science",
            "Director of Engineering", "Director of Finance", "Director of HR",
            "Director of Human Capital", "Director of Human Resources",
            "Director of Marketing", "Director of Operations",
            "Director of Product Management", "Director of Sales",
            "Director of Sales and Marketing", "Event Coordinator",
            "Financial Advisor", "Financial Analyst", "Financial Manager",
            "Front End Developer", "Front end Developer", "Full Stack Engineer",
            "Graphic Designer", "HR Generalist", "HR Manager",
            "Help Desk Analyst", "Human Resources Coordinator",
            "Human Resources Director", "Human Resources Manager",
            "IT Manager", "IT Support", "IT Support Specialist",
            "Junior Account Manager", "Junior Accountant",
            "Junior Advertising Coordinator", "Junior Business Analyst",
            "Junior Business Development Associate",
            "Junior Business Operations Analyst", "Junior Copywriter",
            "Junior Customer Support Specialist", "Junior Data Analyst",
            "Junior Data Scientist", "Junior Designer", "Junior Developer",
            "Junior Financial Advisor", "Junior Financial Analyst",
            "Junior HR Coordinator", "Junior HR Generalist",
            "Junior Marketing Analyst", "Junior Marketing Coordinator",
            "Junior Marketing Manager", "Junior Marketing Specialist",
            "Junior Operations Analyst", "Junior Operations Coordinator",
            "Junior Operations Manager", "Junior Product Manager",
            "Junior Project Manager", "Junior Recruiter",
            "Junior Research Scientist", "Junior Sales Associate",
            "Junior Sales Representative", "Junior Social Media Manager",
            "Junior Social Media Specialist", "Junior Software Developer",
            "Junior Software Engineer", "Junior UX Designer",
            "Junior Web Designer", "Junior Web Developer",
            "Marketing Analyst", "Marketing Coordinator",
            "Marketing Director", "Marketing Manager", "Marketing Specialist",
            "Network Engineer", "Office Manager", "Operations Analyst",
            "Operations Director", "Operations Manager", "Principal Engineer",
            "Principal Scientist", "Product Designer", "Product Manager",
            "Product Marketing Manager", "Project Engineer", "Project Manager",
            "Public Relations Manager", "Receptionist", "Recruiter",
            "Research Director", "Research Scientist", "Sales Associate",
            "Sales Director", "Sales Executive", "Sales Manager",
            "Sales Operations Manager", "Sales Representative",
            "Senior Account Executive", "Senior Account Manager",
            "Senior Accountant", "Senior Business Analyst",
            "Senior Business Development Manager", "Senior Consultant",
            "Senior Data Analyst", "Senior Data Engineer",
            "Senior Data Scientist", "Senior Engineer",
            "Senior Financial Advisor", "Senior Financial Analyst",
            "Senior Financial Manager", "Senior Graphic Designer",
            "Senior HR Generalist", "Senior HR Manager", "Senior HR Specialist",
            "Senior Human Resources Coordinator",
            "Senior Human Resources Manager", "Senior Human Resources Specialist",
            "Senior IT Consultant", "Senior IT Project Manager",
            "Senior IT Support Specialist", "Senior Manager",
            "Senior Marketing Analyst", "Senior Marketing Coordinator",
            "Senior Marketing Director", "Senior Marketing Manager",
            "Senior Marketing Specialist", "Senior Operations Analyst",
            "Senior Operations Coordinator", "Senior Operations Manager",
            "Senior Product Designer", "Senior Product Development Manager",
            "Senior Product Manager", "Senior Product Marketing Manager",
            "Senior Project Coordinator", "Senior Project Engineer",
            "Senior Project Manager", "Senior Quality Assurance Analyst",
            "Senior Research Scientist", "Senior Researcher",
            "Senior Sales Manager", "Senior Sales Representative",
            "Senior Scientist", "Senior Software Architect",
            "Senior Software Developer", "Senior Software Engineer",
            "Senior Training Specialist", "Senior UX Designer",
            "Social Media Manager", "Social Media Specialist",
            "Software Developer", "Software Engineer",
            "Software Engineer Manager", "Software Manager",
            "Software Project Manager", "Strategy Consultant",
            "Supply Chain Analyst", "Supply Chain Manager",
            "Technical Recruiter", "Technical Support Specialist",
            "Technical Writer", "Training Specialist",
            "UX Designer", "UX Researcher",
            "VP of Finance", "VP of Operations", "Web Developer",
        ],

        # Hanya 5 negara yang ada di dataset
        "Country": ["Australia", "Canada", "China", "UK", "USA"],

        # Semua ras dari dataset
        "Race": [
            "African American", "Asian", "Australian",
            "Black", "Chinese", "Hispanic",
            "Korean", "Mixed", "Welsh", "White",
        ],
    }


def get_model_info() -> dict:
    try:
        meta = get_metadata()
        return {
            "problem_type":         meta.get("problem_type", "N/A"),
            "feature_columns":      meta.get("feature_columns", []),
            "numeric_features":     meta.get("numeric_features", []),
            "categorical_features": meta.get("categorical_features", []),
            "target_column":        meta.get("target_column", "Salary"),
            "model_loaded":         _pipeline is not None,
        }
    except Exception:
        return {"model_loaded": False}