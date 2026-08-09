import { useState, useEffect, useCallback } from 'react';
import { PieChart, Pie, Cell, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calendar, TrendingUp, TrendingDown, DollarSign } from 'lucide-react';
import api from '../utils/api';
import { formatCurrency, getCurrencySymbol } from '../utils/currencies';
import './AnalyticsPage.css';

const COLORS = ['#be185d', '#4338ca', '#065f46', '#92400e', '#6d28d9', '#9d174d', '#1e40af', '#7c3aed', '#047857', '#0e7490', '#3730a3', '#4b5563'];

export default function AnalyticsPage() {
  const [data, setData] = useState({
    summary: { total_expenses: 0, avg_daily: 0, highest_category: 'None' },
    pie_data: [],
    trend_data: []
  });
  const [currency, setCurrency] = useState('INR');
  const [filter, setFilter] = useState('this_month');
  const [customRange, setCustomRange] = useState({ start: '', end: '' });
  const [loading, setLoading] = useState(true);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    try {
      // First get profile for currency
      const profileRes = await api.get('/api/v1/profile');
      setCurrency(profileRes.data.currency || 'INR');

      // Then get analytics
      let url = `/api/v1/analytics?filter=${filter}`;
      if (filter === 'custom' && customRange.start && customRange.end) {
        url += `&start_date=${customRange.start}&end_date=${customRange.end}`;
      }
      
      const res = await api.get(url);
      setData(res.data);
    } catch (err) {
      console.error('Failed to load analytics:', err);
    } finally {
      setLoading(false);
    }
  }, [filter, customRange]);

  useEffect(() => {
    fetchAnalytics();
  }, [fetchAnalytics]);

  const sym = getCurrencySymbol(currency);

  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="custom-tooltip">
          <p className="label">{`${label || payload[0].name}`}</p>
          <p className="intro">{`${sym}${payload[0].value.toLocaleString('en-IN', { minimumFractionDigits: 2 })}`}</p>
        </div>
      );
    }
    return null;
  };

  return (
    <div className="analytics-page">
      <div className="page-header">
        <h1>Financial Analytics</h1>
        <div className="filter-controls">
          <select 
            value={filter} 
            onChange={(e) => setFilter(e.target.value)}
            className="filter-select"
          >
            <option value="today">Today</option>
            <option value="last_7_days">Last 7 Days</option>
            <option value="this_month">This Month</option>
            <option value="this_year">This Year</option>
            <option value="custom">Custom Range</option>
          </select>
          
          {filter === 'custom' && (
            <div className="custom-date-inputs">
              <input 
                type="date" 
                value={customRange.start}
                onChange={(e) => setCustomRange({...customRange, start: e.target.value})}
              />
              <span>to</span>
              <input 
                type="date" 
                value={customRange.end}
                onChange={(e) => setCustomRange({...customRange, end: e.target.value})}
              />
              <button className="apply-btn" onClick={fetchAnalytics}>Apply</button>
            </div>
          )}
        </div>
      </div>

      {loading ? (
        <div className="no-data">Loading analytics...</div>
      ) : (
        <>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-card-icon"><DollarSign size={20} /></div>
              <div className="stat-content">
                <div className="stat-card-label">Total Expenses</div>
                <div className="stat-card-value negative">
                  {formatCurrency(data.summary.total_expenses, currency)}
                </div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-card-icon"><Calendar size={20} /></div>
              <div className="stat-content">
                <div className="stat-card-label">Average Daily Expense</div>
                <div className="stat-card-value">
                  {formatCurrency(data.summary.avg_daily, currency)}
                </div>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-card-icon"><TrendingUp size={20} /></div>
              <div className="stat-content">
                <div className="stat-card-label">Highest Spending Category</div>
                <div className="stat-card-value" style={{fontSize: '1.2rem', marginTop: '0.2rem'}}>
                  {data.summary.highest_category}
                </div>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3>Expense Distribution</h3>
              {data.pie_data.length > 0 ? (
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={data.pie_data}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={90}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {data.pie_data.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip content={<CustomTooltip />} />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="no-data">No expense data for this period.</div>
              )}
            </div>

            <div className="chart-card">
              <h3>Daily Expense Trend</h3>
              {data.trend_data.length > 0 ? (
                <div className="chart-container">
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={data.trend_data} margin={{ top: 5, right: 20, bottom: 5, left: 0 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                      <XAxis dataKey="date" tick={{fontSize: 12}} tickMargin={10} axisLine={false} tickLine={false} />
                      <YAxis tickFormatter={(val) => `₹${val}`} tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                      <Tooltip content={<CustomTooltip />} />
                      <Line type="monotone" dataKey="amount" stroke="#7c3aed" strokeWidth={3} dot={{r: 4, strokeWidth: 2}} activeDot={{r: 6}} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              ) : (
                <div className="no-data">No trend data for this period.</div>
              )}
            </div>
            
            <div className="chart-card full-width">
               <h3>Category Comparison</h3>
               {data.pie_data.length > 0 ? (
                 <div className="chart-container">
                   <ResponsiveContainer width="100%" height={300}>
                     <BarChart data={data.pie_data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                       <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                       <XAxis dataKey="name" tick={{fontSize: 12}} tickMargin={10} axisLine={false} tickLine={false} />
                       <YAxis tickFormatter={(val) => `₹${val}`} tick={{fontSize: 12}} axisLine={false} tickLine={false} />
                       <Tooltip content={<CustomTooltip />} />
                       <Bar dataKey="value" fill="#a78bfa" radius={[4, 4, 0, 0]} barSize={40} />
                     </BarChart>
                   </ResponsiveContainer>
                 </div>
               ) : (
                 <div className="no-data">No comparison data available.</div>
               )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
