import { useEffect, useState } from "react";
import { getUsage } from "../api";

export default function UsageDashboard() {
  const [usage, setUsage] = useState(0);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const res = await getUsage();
        setUsage(res.reports_generated);
      } catch (err) {
        console.error(err);
      }
    };
    fetchUsage();
  }, []);

  return (
    <div>
      <h2>Usage Dashboard</h2>
      <p>Reports generated: {usage}</p>
    </div>
  );
}
