import React, { useState, useEffect } from "react";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

function UsageDashboard() {
  const [usage, setUsage] = useState({ questions_asked: 0, reports_generated: 0 });

  const fetchUsage = async () => {
    try {
      const res = await fetch(`${API_URL}/usage/`);
      const data = await res.json();
      setUsage({
        questions_asked: data.questions_asked || 0,
        reports_generated: data.reports_generated || 0,
      });
    } catch (err) {
      console.log("Error fetching usage:", err);
    }
  };

  useEffect(() => {
    fetchUsage();
    const interval = setInterval(fetchUsage, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="usage-dashboard">
      <h3>Usage & Billing</h3>
      <div className="usage-counters">
        <p>Questions Asked: <strong>{usage.questions_asked}</strong> (1 credit/question)</p>
        <p>Reports Generated: <strong>{usage.reports_generated}</strong> (1 credit/report)</p>
      </div>
    </div>
  );
}

export default UsageDashboard;
