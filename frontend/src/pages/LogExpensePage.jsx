import { useState, useEffect } from 'react';
import { Bot, CheckCircle } from 'lucide-react';
import api from '../utils/api';
import { expenseCategories, paymentRoutes, suggestCategory } from '../utils/currencies';
import './LogExpensePage.css';

export default function LogExpensePage() {
  const [formData, setFormData] = useState({
    description: '',
    amount: '',
    category: 'Other',
    payment_route: 'Cash'
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [aiSuggestion, setAiSuggestion] = useState(null);

  useEffect(() => {
    if (formData.description.length > 2) {
      const suggestion = suggestCategory(formData.description);
      if (suggestion && suggestion !== formData.category) {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setAiSuggestion(suggestion);
      } else {
        setAiSuggestion(null);
      }
    } else {
      setAiSuggestion(null);
    }
  }, [formData.description, formData.category]);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
    if (error) setError('');
    if (success) setSuccess(false);
  };

  const handleApplySuggestion = () => {
    setFormData({ ...formData, category: aiSuggestion });
    setAiSuggestion(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    const amountValue = parseFloat(formData.amount);
    if (!formData.description.trim() || Number.isNaN(amountValue) || amountValue <= 0) {
      setError('Please enter a valid description and positive amount.');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/v1/expenses/', {
        description: formData.description.trim(),
        amount: amountValue,
        category: formData.category,
        payment_route: formData.payment_route
      });
      setSuccess(true);
      setFormData({ description: '', amount: '', category: 'Other', payment_route: 'Cash' });
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError(
        err.response?.data?.detail || err.response?.data?.message ||
        'Failed to log expense. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="log-grid">
      <div className="expense-form-card">
        <h2>Log New Expense</h2>
        {error && <div className="error-message" style={{marginBottom: '1rem'}}>{error}</div>}
        {success && <div className="success-message" style={{color: 'green', marginBottom: '1rem'}}>Expense logged successfully!</div>}
        
        <form className="expense-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Description / Memo</label>
            <input
              type="text"
              name="description"
              className="form-input"
              placeholder="e.g. Starbucks Coffee"
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Amount</label>
            <input
              type="number"
              name="amount"
              className="form-input"
              placeholder="0.00"
              step="0.01"
              min="0.01"
              value={formData.amount}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">Category</label>
            <select
              name="category"
              className="form-select"
              value={formData.category}
              onChange={handleChange}
            >
              {expenseCategories.map(cat => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label className="form-label">Payment Method</label>
            <select
              name="payment_route"
              className="form-select"
              value={formData.payment_route}
              onChange={handleChange}
            >
              {paymentRoutes.map(route => (
                <option key={route} value={route}>{route}</option>
              ))}
            </select>
          </div>

          <button type="submit" className="log-submit-btn" disabled={loading}>
            {loading ? 'Logging...' : 'Log Expense'}
          </button>
        </form>
      </div>

      <div className="ai-assist-card">
        <h2>AI Categorization Assist</h2>
        {aiSuggestion ? (
          <div className="ai-suggestion">
            <div className="ai-suggestion-label">Suggested Category</div>
            <div 
              className={`ai-suggestion-value ${aiSuggestion.toLowerCase().replace(/ & /g, '-').replace(/\s/g, '-')}`}
              onClick={handleApplySuggestion}
            >
              <CheckCircle size={16} />
              {aiSuggestion}
            </div>
            <p className="ai-suggestion-hint">Click to apply this category automatically.</p>
          </div>
        ) : (
          <div className="ai-assist-empty">
            <Bot />
            <p>Type a description and AI will suggest the best matching budget category.</p>
          </div>
        )}
      </div>
    </div>
  );
}
