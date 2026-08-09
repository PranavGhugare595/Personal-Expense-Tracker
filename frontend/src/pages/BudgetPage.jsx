import { useState, useEffect, useCallback } from 'react';
import { Wallet, AlertTriangle, CheckCircle2 } from 'lucide-react';
import api from '../utils/api';
import { formatCurrency, getCurrencySymbol } from '../utils/currencies';
import './BudgetPage.css';

const CATEGORIES = [
  'Food & Dining', 'Transport', 'Utilities', 
  'Entertainment', 'Shopping', 'Healthcare', 
  'Education', 'Rent & Housing', 'Groceries', 
  'Travel', 'Subscriptions', 'Other'
];

export default function BudgetPage() {
  const [budgets, setBudgets] = useState([]);
  const [currency, setCurrency] = useState('INR');
  const [loading, setLoading] = useState(true);
  const [editingCategory, setEditingCategory] = useState(null);
  const [editAmount, setEditAmount] = useState('');

  const fetchBudgets = useCallback(async () => {
    try {
      const [profileRes, budgetRes] = await Promise.all([
        api.get('/api/v1/profile'),
        api.get('/api/v1/budget')
      ]);
      setCurrency(profileRes.data.currency || 'INR');
      setBudgets(budgetRes.data);
    } catch (err) {
      console.error('Failed to load budgets:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchBudgets();
  }, [fetchBudgets]);

  const handleSaveBudget = async (category) => {
    try {
      await api.post('/api/v1/budget', {
        category,
        amount: Number(editAmount)
      });
      setEditingCategory(null);
      fetchBudgets();
    } catch (err) {
      console.error('Failed to save budget:', err);
      alert('Failed to save budget');
    }
  };

  const getBudgetForCategory = (cat) => {
    return budgets.find(b => b.category === cat) || { 
      category: cat, budget_amount: 0, spent_amount: 0, remaining_amount: 0, usage_percentage: 0 
    };
  };

  const sym = getCurrencySymbol(currency);
  
  // Overall stats
  const totalBudget = budgets.reduce((acc, curr) => acc + curr.budget_amount, 0);
  const totalSpent = budgets.reduce((acc, curr) => acc + curr.spent_amount, 0);
  const overallUsage = totalBudget > 0 ? (totalSpent / totalBudget) * 100 : 0;

  return (
    <div className="budget-page">
      <div className="page-header">
        <h1>Budget Planner</h1>
        <p className="header-subtitle">Set monthly limits for each category to keep your spending in check.</p>
      </div>

      <div className="overall-budget-card">
        <div className="budget-header-content">
          <div className="icon-wrapper">
            <Wallet size={24} />
          </div>
          <div className="budget-summary">
            <h3>Overall Budget Usage</h3>
            <div className="budget-numbers">
              <span className="spent">{formatCurrency(totalSpent, currency)}</span>
              <span className="divider">/</span>
              <span className="total">{formatCurrency(totalBudget, currency)}</span>
            </div>
          </div>
        </div>
        <div className="progress-container">
          <div 
            className={`progress-fill ${overallUsage >= 100 ? 'danger' : overallUsage >= 80 ? 'warning' : 'safe'}`}
            style={{ width: `${Math.min(overallUsage, 100)}%` }}
          />
        </div>
        <div className="progress-labels">
          <span>{overallUsage.toFixed(1)}% Used</span>
          <span>{formatCurrency(totalBudget - totalSpent, currency)} Remaining</span>
        </div>
      </div>

      <div className="budgets-grid">
        {CATEGORIES.map(category => {
          const data = getBudgetForCategory(category);
          const isEditing = editingCategory === category;
          const isDanger = data.usage_percentage >= 100;
          const isWarning = data.usage_percentage >= 80 && !isDanger;

          return (
            <div className={`budget-item-card ${isDanger ? 'alert-danger' : isWarning ? 'alert-warning' : ''}`} key={category}>
              <div className="budget-item-header">
                <span className="category-name">{category}</span>
                {isEditing ? (
                  <div className="edit-controls">
                    <span className="currency-symbol">{sym}</span>
                    <input 
                      type="number" 
                      value={editAmount}
                      onChange={(e) => setEditAmount(e.target.value)}
                      className="budget-input"
                      autoFocus
                    />
                    <button className="btn-save" onClick={() => handleSaveBudget(category)}>Save</button>
                    <button className="btn-cancel" onClick={() => setEditingCategory(null)}>Cancel</button>
                  </div>
                ) : (
                  <div className="budget-display">
                    <span className="budget-limit">Budget: {formatCurrency(data.budget_amount, currency)}</span>
                    <button 
                      className="btn-edit" 
                      onClick={() => {
                        setEditAmount(data.budget_amount);
                        setEditingCategory(category);
                      }}
                    >
                      Set Limit
                    </button>
                  </div>
                )}
              </div>

              <div className="budget-progress-area">
                <div className="budget-amounts">
                  <span className="spent-amount">Spent: {formatCurrency(data.spent_amount, currency)}</span>
                  <span className={`remaining-amount ${data.remaining_amount < 0 ? 'negative' : ''}`}>
                    {data.remaining_amount < 0 ? 'Over budget by ' : 'Remaining: '}
                    {formatCurrency(Math.abs(data.remaining_amount), currency)}
                  </span>
                </div>
                
                <div className="progress-track">
                  <div 
                    className={`progress-bar ${isDanger ? 'bg-danger' : isWarning ? 'bg-warning' : 'bg-safe'}`}
                    style={{ width: `${Math.min(data.usage_percentage, 100)}%` }}
                  />
                </div>
                
                {isDanger && (
                  <div className="status-alert danger">
                    <AlertTriangle size={14} /> You have exceeded your budget!
                  </div>
                )}
                {isWarning && (
                  <div className="status-alert warning">
                    <AlertTriangle size={14} /> You are nearing your budget limit.
                  </div>
                )}
                {!isDanger && !isWarning && data.budget_amount > 0 && (
                  <div className="status-alert safe">
                    <CheckCircle2 size={14} /> On track
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
