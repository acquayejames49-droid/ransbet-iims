"""Train the two AI models described in the report and save their outputs.

1. Demand forecasting  -> Prophet (one model per product)
   - back-tests on the last 30 days to measure MAPE / MAE / RMSE
   - then forecasts the next 30 days and stores it in the `forecasts` table
2. Anomaly detection   -> Isolation Forest (one model over all products)
   - flags unusual daily sales and stores them in `anomaly_flags`

Run with:  python train_models.py
Re-run it whenever new sales data has been added (this is the "retraining").
"""
import os
import pickle
import logging
import contextlib

import numpy as np
import pandas as pd
from sqlalchemy import func

from app import create_app, db
from app.models import Sale, Product, Forecast, ForecastMetric, AnomalyFlag

# Quieten Prophet's very chatty logging.
logging.getLogger("prophet").setLevel(logging.ERROR)
logging.getLogger("cmdstanpy").setLevel(logging.ERROR)

app = create_app()
FORECAST_DAYS = 30
BACKTEST_DAYS = 30
MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")


def daily_series(pid, start, end):
    """Return a daily sales series for one product, 0-filled for missing days."""
    rows = (db.session.query(Sale.sale_date, func.sum(Sale.quantity))
            .filter(Sale.product_id == pid).group_by(Sale.sale_date).all())
    s = pd.Series({pd.Timestamp(d): float(q) for d, q in rows})
    idx = pd.date_range(start, end, freq="D")
    return s.reindex(idx, fill_value=0.0)


def score_metrics(y_true, y_pred):
    y_true, y_pred = np.array(y_true, float), np.array(y_pred, float)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mask = y_true > 0
    mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100) if mask.any() else None
    return mape, mae, rmse


def fit_prophet(df):
    """Fit a Prophet model quietly and return it."""
    from prophet import Prophet
    m = Prophet(weekly_seasonality=True, yearly_seasonality=True,
                daily_seasonality=False, interval_width=0.9)
    try:
        m.add_country_holidays(country_name="GH")  # Ghana holidays
    except Exception:
        pass
    with open(os.devnull, "w") as devnull, contextlib.redirect_stdout(devnull):
        m.fit(df)
    return m


def run_forecasting():
    print("\n== Demand forecasting (Prophet) ==")
    Forecast.query.delete()
    ForecastMetric.query.delete()
    db.session.commit()

    span = db.session.query(func.min(Sale.sale_date), func.max(Sale.sale_date)).first()
    start, end = span
    if not start:
        print("  no sales data — run generate_sales.py first.")
        return

    products = Product.query.filter_by(is_active=True).all()
    for p in products:
        s = daily_series(p.id, start, end)
        if (s > 0).sum() < 60:
            print(f"  {p.name}: not enough data, skipped")
            continue
        df = pd.DataFrame({"ds": s.index, "y": s.values})

        # --- back-test for accuracy ---
        cutoff = df["ds"].max() - pd.Timedelta(days=BACKTEST_DAYS)
        train, test = df[df.ds <= cutoff], df[df.ds > cutoff]
        mape = mae = rmse = None
        if len(test) >= 7:
            m_bt = fit_prophet(train)
            fc_bt = m_bt.predict(test[["ds"]])
            mape, mae, rmse = score_metrics(test.y.values, fc_bt.yhat.clip(lower=0).values)
            db.session.add(ForecastMetric(product_id=p.id, mape=mape, mae=mae, rmse=rmse))

        # --- final model on all data, forecast forward ---
        m = fit_prophet(df)
        future = m.make_future_dataframe(periods=FORECAST_DAYS)
        fc = m.predict(future).tail(FORECAST_DAYS)
        for _, r in fc.iterrows():
            db.session.add(Forecast(
                product_id=p.id, forecast_date=r.ds.date(),
                predicted_qty=max(0.0, round(float(r.yhat), 2)),
                lower=max(0.0, round(float(r.yhat_lower), 2)),
                upper=round(float(r.yhat_upper), 2)))
        db.session.commit()
        mape_txt = f"MAPE {mape:.1f}%" if mape is not None else "MAPE n/a"
        print(f"  {p.name}: forecast 30d, {mape_txt}")


def run_anomaly_detection():
    print("\n== Anomaly detection (Isolation Forest) ==")
    from sklearn.ensemble import IsolationForest

    AnomalyFlag.query.delete()
    db.session.commit()

    span = db.session.query(func.min(Sale.sale_date), func.max(Sale.sale_date)).first()
    start, end = span
    products = Product.query.filter_by(is_active=True).all()

    frames = []
    for p in products:
        s = daily_series(p.id, start, end)
        d = pd.DataFrame({"date": s.index, "qty": s.values})
        d["product_id"] = p.id
        d["roll_mean"] = d["qty"].rolling(7, min_periods=1).mean()
        d["roll_std"] = d["qty"].rolling(7, min_periods=1).std().fillna(0)
        d["deviation"] = d["qty"] - d["roll_mean"]
        d["dow"] = d["date"].dt.dayofweek
        frames.append(d)
    data = pd.concat(frames, ignore_index=True)

    features = ["qty", "roll_mean", "roll_std", "deviation", "dow"]
    model = IsolationForest(contamination=0.05, random_state=42)
    data["pred"] = model.fit_predict(data[features])
    data["score"] = model.decision_function(data[features])

    flagged = data[data["pred"] == -1]
    # Keep the most recent ~120 days of anomalies so the list stays relevant.
    recent_cut = pd.Timestamp(end) - pd.Timedelta(days=120)
    flagged = flagged[flagged["date"] >= recent_cut]

    for _, r in flagged.iterrows():
        db.session.add(AnomalyFlag(
            product_id=int(r.product_id), flag_date=r.date.date(),
            quantity=int(r.qty), expected=round(float(r.roll_mean), 2),
            score=round(float(r.score), 4),
            reason="spike" if r.qty > r.roll_mean else "drop"))
    db.session.commit()

    os.makedirs(MODELS_DIR, exist_ok=True)
    with open(os.path.join(MODELS_DIR, "anomaly_model.pkl"), "wb") as f:
        pickle.dump(model, f)
    print(f"  flagged {len(flagged)} anomalies (last 120 days); model saved to models/")


with app.app_context():
    db.create_all()
    run_forecasting()
    run_anomaly_detection()
    print("\nTraining complete.")
