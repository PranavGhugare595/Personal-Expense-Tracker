import { useState, useEffect, useCallback } from 'react';
import { BrainCircuit, Info, AlertTriangle, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../utils/api';
import './AdvisorPage.css';

export default function AdvisorPage() {
  const [insights, setInsights] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchInsights = useCallback(async () => {
    try {
      const res = await api.get('/api/v1/advisor/insights');
      setInsights(res.data);
    } catch (err) {
      console.error('Failed to load insights:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  const getIconForType = (type) => {
    switch (type) {
      case 'success': return <CheckCircle2 className="icon-success" />;
      case 'warning': return <AlertTriangle className="icon-warning" />;
      case 'danger': return <AlertCircle className="icon-danger" />;
      case 'info':
      default: return <Info className="icon-info" />;
    }
  };

  return (
    <div className="advisor-page">
      <div className="advisor-header">
        <div className="advisor-title-row">
          <div className="advisor-icon-wrapper">
            <BrainCircuit size={28} />
          </div>
          <div>
            <h1>AI Financial Advisor</h1>
            <p className="header-subtitle">Intelligent insights based on your spending patterns and budgets.</p>
          </div>
        </div>
      </div>

      <div className="insights-container">
        {loading ? (
          <div className="no-data">Generating your personalized insights...</div>
        ) : insights.length === 0 ? (
          <div className="no-data">No insights available right now.</div>
        ) : (
          <div className="insights-list">
            {insights.map((insight, idx) => (
              <div key={idx} className={`insight-card type-${insight.type}`}>
                <div className="insight-icon">
                  {getIconForType(insight.type)}
                </div>
                <div className="insight-message">
                  {insight.message}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
