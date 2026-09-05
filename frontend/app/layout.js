import "./globals.css";

export const metadata = {
  title: "Demand & Capacity Ops Platform",
  description: "Forecast-driven staffing optimization dashboard",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
