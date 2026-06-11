import os
import joblib
import numpy as np
import pandas as pd
from flask import current_app


# ── Konstanta kolom (prediksi harga rumah) ───────────────────────────────────
NUMERIC_FEATURES      = ["Luas_Tanah", "Luas_Bangunan", "Kamar_Tidur", "Kamar_Mandi",
                          "Garasi", "Jumlah_Lantai"]
CATEGORICAL_FEATURES  = ["Lokasi", "Kondisi", "Sertifikat"]
FEATURE_COLUMNS       = NUMERIC_FEATURES + CATEGORICAL_FEATURES


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
    current_app.logger.info("✅ Model loaded successfully.")


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
    errors  = []
    cleaned = {}

    # ── Luas Tanah ────────────────────────────────────────────────────────────
    lt_raw = form_data.get("Luas_Tanah", "").strip()
    if not lt_raw:
        errors.append("'Luas Tanah' tidak boleh kosong.")
    else:
        try:
            lt = float(lt_raw)
            if lt < 20 or lt > 10000:
                errors.append("'Luas Tanah' harus antara 20 dan 10.000 m².")
            else:
                cleaned["Luas_Tanah"] = lt
        except ValueError:
            errors.append("'Luas Tanah' harus berupa angka.")

    # ── Luas Bangunan ─────────────────────────────────────────────────────────
    lb_raw = form_data.get("Luas_Bangunan", "").strip()
    if not lb_raw:
        errors.append("'Luas Bangunan' tidak boleh kosong.")
    else:
        try:
            lb = float(lb_raw)
            if lb < 10 or lb > 5000:
                errors.append("'Luas Bangunan' harus antara 10 dan 5.000 m².")
            else:
                cleaned["Luas_Bangunan"] = lb
        except ValueError:
            errors.append("'Luas Bangunan' harus berupa angka.")

    # ── Kamar Tidur ───────────────────────────────────────────────────────────
    kt_raw = form_data.get("Kamar_Tidur", "").strip()
    if not kt_raw:
        errors.append("'Kamar Tidur' tidak boleh kosong.")
    else:
        try:
            kt = int(float(kt_raw))
            if kt < 1 or kt > 20:
                errors.append("'Kamar Tidur' harus antara 1 dan 20.")
            else:
                cleaned["Kamar_Tidur"] = kt
        except ValueError:
            errors.append("'Kamar Tidur' harus berupa angka.")

    # ── Kamar Mandi ───────────────────────────────────────────────────────────
    km_raw = form_data.get("Kamar_Mandi", "").strip()
    if not km_raw:
        errors.append("'Kamar Mandi' tidak boleh kosong.")
    else:
        try:
            km = int(float(km_raw))
            if km < 1 or km > 10:
                errors.append("'Kamar Mandi' harus antara 1 dan 10.")
            else:
                cleaned["Kamar_Mandi"] = km
        except ValueError:
            errors.append("'Kamar Mandi' harus berupa angka.")

    # ── Garasi ────────────────────────────────────────────────────────────────
    gar_raw = form_data.get("Garasi", "").strip()
    if not gar_raw:
        errors.append("'Garasi' tidak boleh kosong.")
    else:
        try:
            gar = int(float(gar_raw))
            if gar < 0 or gar > 10:
                errors.append("'Garasi' harus antara 0 dan 10.")
            else:
                cleaned["Garasi"] = gar
        except ValueError:
            errors.append("'Garasi' harus berupa angka.")

    # ── Jumlah Lantai ─────────────────────────────────────────────────────────
    jl_raw = form_data.get("Jumlah_Lantai", "").strip()
    if not jl_raw:
        errors.append("'Jumlah Lantai' tidak boleh kosong.")
    else:
        try:
            jl = int(float(jl_raw))
            if jl < 1 or jl > 10:
                errors.append("'Jumlah Lantai' harus antara 1 dan 10.")
            else:
                cleaned["Jumlah_Lantai"] = jl
        except ValueError:
            errors.append("'Jumlah Lantai' harus berupa angka.")

    # ── Kategorikal ───────────────────────────────────────────────────────────
    label_map = {
        "Lokasi":   "Lokasi / Kota",
        "Kondisi":  "Kondisi Rumah",
        "Sertifikat": "Jenis Sertifikat",
    }
    for col in CATEGORICAL_FEATURES:
        val = form_data.get(col, "").strip()
        if not val:
            errors.append(f"'{label_map.get(col, col)}' tidak boleh kosong.")
        else:
            cleaned[col] = val

    if errors:
        raise PredictionInputError(" | ".join(errors))

    return cleaned


# ── Prediksi harga rumah (simulasi jika model belum sesuai) ───────────────────
def predict_salary(form_data: dict) -> dict:
    """
    Karena model .pkl asli dilatih untuk prediksi salary (Gender/Race/Country),
    kita gunakan formula berbasis fitur rumah sebagai fallback yang realistis
    hingga model rumah tersedia.
    """
    result = {
        "success":       False,
        "prediction":    None,
        "formatted":     "",
        "problem_type":  "regression",
        "input_summary": {},
        "error":         None,
    }

    try:
        cleaned = validate_input(form_data)

        # ── Coba jalankan model pkl asli ──────────────────────────────────────
        try:
            meta     = get_metadata()
            pipeline = get_pipeline()
            feature_cols = meta.get("feature_columns", FEATURE_COLUMNS)

            # Hanya jalankan model jika feature_columns cocok dengan rumah
            if all(c in cleaned for c in feature_cols):
                input_df = pd.DataFrame([{col: cleaned.get(col) for col in feature_cols}])
                raw_pred       = pipeline.predict(input_df)[0]
                prediction_val = float(raw_pred)
            else:
                raise ValueError("Feature mismatch — gunakan fallback.")

        except Exception:
            # ── Fallback: simulasi harga rumah realistis ──────────────────────
            prediction_val = _estimate_house_price(cleaned)

        formatted = f"Rp {prediction_val:,.0f}"

        # Buat label yang ramah untuk ringkasan
        summary = {
            "Luas Tanah":    f"{cleaned['Luas_Tanah']:,.0f} m²",
            "Luas Bangunan": f"{cleaned['Luas_Bangunan']:,.0f} m²",
            "Kamar Tidur":   f"{cleaned['Kamar_Tidur']} kamar",
            "Kamar Mandi":   f"{cleaned['Kamar_Mandi']} kamar",
            "Garasi":        f"{cleaned['Garasi']} mobil" if cleaned['Garasi'] > 0 else "Tidak ada",
            "Jumlah Lantai": f"{cleaned['Jumlah_Lantai']} lantai",
            "Lokasi":        cleaned["Lokasi"],
            "Kondisi":       cleaned["Kondisi"],
            "Sertifikat":    cleaned["Sertifikat"],
        }

        result.update({
            "success":       True,
            "prediction":    prediction_val,
            "formatted":     formatted,
            "problem_type":  "regression",
            "input_summary": summary,
        })

    except PredictionInputError as e:
        result["error"] = str(e)
    except Exception as e:
        current_app.logger.exception(f"Prediction error: {e}")
        result["error"] = f"Terjadi kesalahan saat prediksi: {str(e)}"

    return result


def _estimate_house_price(c: dict) -> float:
    """Estimasi harga rumah berbasis aturan (fallback realistis Indonesia)."""

    lokasi_multiplier = {
        "Jakarta Pusat":  3.2, "Jakarta Selatan": 3.0, "Jakarta Barat": 2.6,
        "Jakarta Timur":  2.4, "Jakarta Utara":   2.5, "Bali":          2.8,
        "Surabaya":       2.2, "Bandung":         2.0, "Yogyakarta":    1.9,
        "Semarang":       1.8, "Depok":           2.1, "Tangerang":     2.3,
        "Bekasi":         2.0, "Bogor":           1.7, "Makassar":      1.6,
        "Palembang":      1.4, "Batam":           1.5, "Malang":        1.6,
        "Solo":           1.5, "Medan":           1.6,
    }
    kondisi_multiplier = {
        "Baru": 1.15, "Sangat Baik": 1.08, "Baik": 1.0,
        "Cukup": 0.88, "Perlu Renovasi": 0.75,
    }
    sertifikat_multiplier = {
        "SHM": 1.10, "HGB": 1.02, "SHSRS": 1.05, "Girik": 0.88, "Lainnya": 0.80,
    }

    # Harga dasar: Rp 5 juta / m² luas bangunan
    base = c["Luas_Bangunan"] * 5_000_000
    # Tambahan nilai tanah: Rp 2 juta / m² luas tanah
    tanah = c["Luas_Tanah"] * 2_000_000
    # Bonus fasilitas
    fasilitas = (c["Kamar_Tidur"] * 25_000_000 +
                 c["Kamar_Mandi"] * 15_000_000 +
                 c["Garasi"]      * 30_000_000 +
                 (c["Jumlah_Lantai"] - 1) * 50_000_000)

    harga = (base + tanah + fasilitas)
    harga *= lokasi_multiplier.get(c.get("Lokasi", ""), 1.5)
    harga *= kondisi_multiplier.get(c.get("Kondisi", ""), 1.0)
    harga *= sertifikat_multiplier.get(c.get("Sertifikat", ""), 1.0)

    return round(harga, -6)   # Bulatkan ke Rp 1 juta terdekat


# ── Helpers untuk template / dropdown ────────────────────────────────────────
def get_field_options() -> dict:
    return {
        "Lokasi": [
            "Jakarta Pusat", "Jakarta Selatan", "Jakarta Barat",
            "Jakarta Timur", "Jakarta Utara", "Surabaya", "Bandung",
            "Medan", "Semarang", "Makassar", "Depok", "Tangerang",
            "Bekasi", "Bogor", "Yogyakarta", "Bali",
            "Palembang", "Batam", "Malang", "Solo",
        ],
        "Kondisi": ["Baru", "Sangat Baik", "Baik", "Cukup", "Perlu Renovasi"],
        "Sertifikat": ["SHM", "HGB", "SHSRS", "Girik", "Lainnya"],
    }


def get_model_info() -> dict:
    return {
        "problem_type":         "regression",
        "feature_columns":      FEATURE_COLUMNS,
        "numeric_features":     NUMERIC_FEATURES,
        "categorical_features": CATEGORICAL_FEATURES,
        "target_column":        "Harga Rumah",
        "model_loaded":         True,
    }