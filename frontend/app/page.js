"use client";

import { useEffect, useState } from "react";
import ForecastChart from "../components/ForecastChart";
import StaffingTable from "../components/StaffingTable";

const HORIZON_DAYS = 14;

export default function Home() {
  const [forecast, setForecast] = useState(null);
  const [staffing, setStaffing] = useState(null);

  useEffect(() => {
    fetch(`/api/forecast?horizon_days=${HORIZON_DAYS}`)
      .then((r) => r.json())
      .then(setForecast)
      .catch(() => setForecast({ points: [] }));

    fetch(`/api/staffing-plan?horizon_days=${HORIZON_DAYS}`)
      .then((r) => r.json())
      .then(setStaffing)
      .catch(() => setStaffing({ schedule: [], total_cost: 0 }));
  }, []);

  const points = forecast?.points || [];
  const schedule = staffing?.schedule || [];

  const totalVolume = points.reduce((s, p) => s + p.forecast, 0);
  const peakDay = points.reduce((max, p) => (p.forecast > (max?.forecast || 0) ? p : max), null);
  const totalWorkers = schedule.reduce((s, r) => s + r.workers_assigned, 0);

  return (
    <div className="page">
      <header className="topbar">
        <h1>Demand &amp; Capacity Ops Platform</h1>
        <span className="badge">SARIMAX forecast -&gt; Pyomo/HiGHS MILP</span>
      </header>

      <div className="kpi-row">
        <div className="kpi-card">
          <div className="label">14-Day Forecasted Volume</div>
          <div className="value">{totalVolume ? Math.round(totalVolume).toLocaleString() : "--"}</div>
          <div className="sub">parcels</div>
        </div>
        <div className="kpi-card">
          <div className="label">Peak Day</div>
          <div className="value">{peakDay ? peakDay.date : "--"}</div>
          <div className="sub">{peakDay ? `${Math.round(peakDay.forecast).toLocaleString()} parcels` : ""}</div>
        </div>
        <div className="kpi-card">
          <div className="label">Optimized Labor Cost</div>
          <div className="value">{staffing ? `$${Math.round(staffing.total_cost).toLocaleString()}` : "--"}</div>
          <div className="sub">14-day horizon</div>
        </div>
        <div className="kpi-card">
          <div className="label">Shifts Scheduled</div>
          <div className="value">{schedule.length || "--"}</div>
          <div className="sub">{totalWorkers} worker-shifts total</div>
        </div>
      </div>

      <div className="panels">
        <div className="panel">
          <h2>14-Day Parcel Volume Forecast (SARIMAX, 80% interval)</h2>
          <ForecastChart points={points} />
        </div>
        <div className="panel">
          <h2>MILP-Optimized Staffing Plan</h2>
          <StaffingTable schedule={schedule} />
        </div>
      </div>

      <footer className="foot">
        Synthetic demo data. Forecast served by FastAPI (/api/forecast); staffing plan solved
        on demand with Pyomo + HiGHS (/api/staffing-plan).
      </footer>
    </div>
  );
}
