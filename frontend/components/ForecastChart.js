"use client";

// Dependency-free SVG line chart. A real production build would likely
// reach for Recharts/visx/Observable Plot, but plotting three series
// (forecast + an 80% confidence band) by hand keeps this demo's `npm
// install` to three packages (next/react/react-dom) and makes the exact
// rendering logic inspectable in one place.
export default function ForecastChart({ points }) {
  if (!points || points.length === 0) return <div>Loading forecast...</div>;

  const width = 760;
  const height = 280;
  const padding = { top: 16, right: 16, bottom: 28, left: 56 };

  const values = points.flatMap((p) => [p.forecast, p.lower_80, p.upper_80]);
  const minY = Math.min(...values) * 0.95;
  const maxY = Math.max(...values) * 1.05;

  const xStep = (width - padding.left - padding.right) / (points.length - 1 || 1);
  const yScale = (v) =>
    height - padding.bottom - ((v - minY) / (maxY - minY)) * (height - padding.top - padding.bottom);
  const xScale = (i) => padding.left + i * xStep;

  const linePath = (key) =>
    points.map((p, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(p[key])}`).join(" ");

  const bandPath =
    points.map((p, i) => `${i === 0 ? "M" : "L"} ${xScale(i)} ${yScale(p.upper_80)}`).join(" ") +
    " " +
    [...points]
      .reverse()
      .map((p, i) => `L ${xScale(points.length - 1 - i)} ${yScale(p.lower_80)}`)
      .join(" ") +
    " Z";

  const yTicks = 4;
  const tickValues = Array.from({ length: yTicks + 1 }, (_, i) => minY + ((maxY - minY) * i) / yTicks);

  return (
    <svg width="100%" viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Parcel volume forecast chart">
      {tickValues.map((t, i) => (
        <g key={i}>
          <line x1={padding.left} x2={width - padding.right} y1={yScale(t)} y2={yScale(t)} stroke="#1f2937" strokeWidth="1" />
          <text x={padding.left - 8} y={yScale(t) + 4} textAnchor="end" fontSize="10" fill="#9ca3af">
            {Math.round(t).toLocaleString()}
          </text>
        </g>
      ))}

      <path d={bandPath} fill="#3b82f6" opacity="0.15" stroke="none" />
      <path d={linePath("forecast")} fill="none" stroke="#3b82f6" strokeWidth="2.5" />

      {points.map((p, i) =>
        i % Math.ceil(points.length / 7) === 0 ? (
          <text key={i} x={xScale(i)} y={height - 8} textAnchor="middle" fontSize="10" fill="#9ca3af">
            {p.date.slice(5)}
          </text>
        ) : null
      )}
    </svg>
  );
}
