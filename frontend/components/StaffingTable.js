"use client";

export default function StaffingTable({ schedule }) {
  if (!schedule || schedule.length === 0) return <div>Loading staffing plan...</div>;

  const rows = [...schedule].sort((a, b) => a.date.localeCompare(b.date) || a.start_hour - b.start_hour);

  return (
    <div style={{ maxHeight: 280, overflowY: "auto" }}>
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Shift</th>
            <th>Start</th>
            <th>Workers</th>
            <th>Cost</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i}>
              <td>{r.date}</td>
              <td>{r.pattern_id}</td>
              <td>{String(r.start_hour).padStart(2, "0")}:00</td>
              <td>{r.workers_assigned}</td>
              <td>${r.shift_cost.toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
