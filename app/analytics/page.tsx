// app/analytics/page.tsx
'use client';

import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

// Mock data fetching function
async function fetchAnalyticsData() {
  // In a real application, you would fetch this data from your API
  return {
    caseDistribution: [
      { name: 'Region A', cases: 4000 },
      { name: 'Region B', cases: 3000 },
      { name: 'Region C', cases: 2000 },
      { name: 'Region D', cases: 2780 },
      { name: 'Region E', cases: 1890 },
      { name: 'Region F', cases: 2390 },
      { name: 'Region G', cases: 3490 },
    ],
  };
}

export default function AnalyticsDashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    async function loadData() {
      try {
        const analyticsData = await fetchAnalyticsData();
        setData(analyticsData);
      } catch (error) {
        console.error('Failed to load analytics data:', error);
      } finally {
        setLoading(false);
      }
    }
    
    loadData();
  }, []);
  
  if (loading) return <div>Loading analytics...</div>;
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 p-4">
      <div className="p-4 bg-white rounded-lg shadow">
        <h2 className="text-xl font-bold mb-4">Case Distribution</h2>
        {data && (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.caseDistribution}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="cases" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        )}
      </div>
      
      {/* Add more analytics components here */}
    </div>
  );
}
