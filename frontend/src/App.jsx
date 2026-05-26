import React, { useState, useEffect } from 'react';
import { Layout, Menu, Input, Card, Button, Form, Typography, Space, Row, Col, Alert, Table, Modal, Progress, Tag, Statistic, Empty, message, Slider } from 'antd';
import { 
  LineChartOutlined, 
  FormOutlined, 
  PieChartOutlined, 
  SecurityScanOutlined, 
  UserOutlined, 
  LockOutlined, 
  PlusOutlined, 
  DeleteOutlined, 
  CheckCircleOutlined,
  AlertOutlined,
  RocketOutlined 
} from '@ant-design/icons';

const { Header, Content, Sider } = Layout;
const { Title, Text, Paragraph } = Typography;

const API_BASE_URL = `${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1`;

function App() {
  const [collapsed, setCollapsed] = useState(false);
  const [currentTab, setCurrentTab] = useState('dashboard');
  const [token, setToken] = useState(localStorage.getItem('jwt_token') || null);
  const [user, setUser] = useState(null);
  
  // App States
  const [expenses, setExpenses] = useState([]);
  const [activeBudget, setActiveBudget] = useState(null);
  const [forecasts, setForecasts] = useState([]);
  const [insights, setInsights] = useState(null);

  // Custom Income & Safety Target States
  const [userIncome, setUserIncome] = useState(parseFloat(localStorage.getItem('user_income')) || 4000.0);
  const [safetyAllocation, setSafetyAllocation] = useState(parseFloat(localStorage.getItem('safety_allocation')) || 20.0);
  
  // Table Loading states
  const [loading, setLoading] = useState(false);
  const [mlLoading, setMlLoading] = useState(false);
  
  // Auth Form forms
  const [isRegistering, setIsRegistering] = useState(false);
  const [expenseForm] = Form.useForm();
  const [loginForm] = Form.useForm();
  const [registerForm] = Form.useForm();

  // Floating suggested ML categories state
  const [suggestedCategory, setSuggestedCategory] = useState(null);
  const [suggestionConfidence, setSuggestionConfidence] = useState(null);

  // Auto load initial states on user login
  useEffect(() => {
    if (token) {
      fetchUserProfile();
      fetchExpenses();
      fetchBudget();
    }
  }, [token]);

  // Re-fetch/recalculate insights when config or token changes
  useEffect(() => {
    if (token) {
      if (token === 'offline_sandbox_token') {
        recalculateOfflineInsights(expenses, userIncome, safetyAllocation);
      } else {
        fetchMLInsights(userIncome, safetyAllocation);
      }
    }
  }, [userIncome, safetyAllocation, token, expenses]);

  // Auth Functions
  const handleLogin = async (values) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await response.json();
      if (response.ok) {
        localStorage.setItem('jwt_token', data.access_token);
        setToken(data.access_token);
        message.success("Authenticated successfully!");
      } else {
        message.error(data.detail || "Authentication credentials rejected.");
      }
    } catch (err) {
      // Offline fallback login for easy local demonstration without backend
      console.warn("Backend not detected, activating local sandbox environment.");
      localStorage.setItem('jwt_token', 'offline_sandbox_token');
      setToken('offline_sandbox_token');
      setUser({ name: "Jane Doe (Offline Sandbox)", email: values.email, currency: "USD" });
      loadOfflineSandboxData();
      message.warning("FastAPI offline: Activated Local Browser Sandbox Sandbox.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (values) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...values, currency: 'USD' }),
      });
      const data = await response.json();
      if (response.ok) {
        message.success("Account registered! Please sign in.");
        setIsRegistering(false);
        loginForm.setFieldsValue({ email: values.email });
      } else {
        message.error(data.detail || "Registration failed.");
      }
    } catch (err) {
      message.error("Could not reach backend servers to compile registration.");
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setToken(null);
    setUser(null);
    setExpenses([]);
    setActiveBudget(null);
    setForecasts([]);
    setInsights(null);
    message.info("Logged out safely.");
  };

  // Fetch functions with Auth Headers
  const fetchUserProfile = async () => {
    if (token === 'offline_sandbox_token') return;
    try {
      const res = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setUser(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchExpenses = async () => {
    if (token === 'offline_sandbox_token') return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/expenses`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setExpenses(data);
      }
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchBudget = async () => {
    if (token === 'offline_sandbox_token') return;
    try {
      const res = await fetch(`${API_BASE_URL}/budgets/active`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setActiveBudget(data);
      }
    } catch (e) {
      console.error(e);
    }
  };

  const fetchMLInsights = async (customIncome = userIncome, customSafety = safetyAllocation) => {
    if (token === 'offline_sandbox_token') return;
    try {
      // 1. Fetch Forecasts
      const fRes = await fetch(`${API_BASE_URL}/ml/forecast`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (fRes.ok) {
        const fData = await fRes.json();
        setForecasts(fData.forecasts);
      }
      
      // 2. Fetch Budget Recommendations
      const iRes = await fetch(`${API_BASE_URL}/ml/insights?income=${customIncome}&safety_allocation=${customSafety}`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (iRes.ok) {
        const iData = await iRes.json();
        setInsights(iData);
      }
    } catch (e) {
      console.error(e);
    }
  };

  // Run Category Classifier suggestion
  const handleDescriptionChange = async (e) => {
    const text = e.target.value;
    if (text.length < 5) return;
    
    setMlLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/ml/suggest-category`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ description: text }),
      });
      if (response.ok) {
        const data = await response.json();
        setSuggestedCategory(data.suggested_category);
        setSuggestionConfidence(data.confidence);
      }
    } catch (err) {
      // Local Mock NLP classification rules if FastAPI is down
      const lower = text.toLowerCase();
      let cat = "Others";
      let conf = 0.65;
      if (lower.includes("starbucks") || lower.includes("coffee") || lower.includes("mcdonalds") || lower.includes("food") || lower.includes("dinner")) {
        cat = "Food & Dining";
        conf = 0.96;
      } else if (lower.includes("uber") || lower.includes("taxi") || lower.includes("ride") || lower.includes("gas") || lower.includes("cab")) {
        cat = "Transport";
        conf = 0.94;
      } else if (lower.includes("netflix") || lower.includes("games") || lower.includes("movie") || lower.includes("spotify")) {
        cat = "Entertainment";
        conf = 0.89;
      } else if (lower.includes("wifi") || lower.includes("bill") || lower.includes("electricity") || lower.includes("power")) {
        cat = "Utilities";
        conf = 0.92;
      } else if (lower.includes("rent") || lower.includes("apartment")) {
        cat = "Housing";
        conf = 0.98;
      }
      setSuggestedCategory(cat);
      setSuggestionConfidence(conf);
    } finally {
      setMlLoading(false);
    }
  };

  // Add manual suggested category to the input
  const applySuggestedCategory = () => {
    if (suggestedCategory) {
      expenseForm.setFieldsValue({ category: suggestedCategory });
      message.success(`Applied classification: ${suggestedCategory}`);
    }
  };

  // Handle logging new expenses
  const handleAddExpense = async (values) => {
    setLoading(true);
    const newExpense = {
      ...values,
      amount: parseFloat(values.amount),
      ml_metadata: {
        is_suggested: suggestedCategory === values.category,
        confidence_score: suggestedCategory === values.category ? suggestionConfidence : null,
        original_description: values.description
      }
    };

    if (token === 'offline_sandbox_token') {
      const mockRecord = {
        ...newExpense,
        _id: String(Math.random()),
        date: new Date().toISOString(),
        userId: 'sandbox_user'
      };
      const updated = [mockRecord, ...expenses];
      setExpenses(updated);
      recalculateOfflineInsights(updated);
      expenseForm.resetFields();
      setSuggestedCategory(null);
      message.success("Logged transaction locally.");
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/expenses`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(newExpense),
      });
      if (response.ok) {
        message.success("Transaction logged in database.");
        expenseForm.resetFields();
        setSuggestedCategory(null);
        fetchExpenses();
        fetchMLInsights();
      } else {
        const err = await response.json();
        message.error(err.detail || "Failed to log expense.");
      }
    } catch (err) {
      message.error("Could not write record to server.");
    } finally {
      setLoading(false);
    }
  };

  // Handle deleting individual logs
  const handleDeleteExpense = async (id) => {
    if (token === 'offline_sandbox_token') {
      const updated = expenses.filter(e => e._id !== id);
      setExpenses(updated);
      recalculateOfflineInsights(updated);
      message.success("Removed locally.");
      return;
    }

    try {
      const res = await fetch(`${API_BASE_URL}/expenses/${id}`, {
        method: 'DELETE',
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (res.ok) {
        message.success("Deleted transaction.");
        fetchExpenses();
        fetchMLInsights();
      }
    } catch (e) {
      message.error("Failed to sync deletion to cloud database.");
    }
  };

  // Sandboxed local data loaders for easy standalone demonstration
  const loadOfflineSandboxData = () => {
    const sandboxExpenses = [
      { _id: '1', amount: 45.50, description: "Whole Foods family shopping", category: "Food & Dining", date: "2026-05-25T14:00:00Z", payment_method: "Credit Card" },
      { _id: '2', amount: 15.00, description: "Starbucks latte & cookies", category: "Food & Dining", date: "2026-05-24T09:30:00Z", payment_method: "Cash" },
      { _id: '3', amount: 25.00, description: "Uber cab home from office", category: "Transport", date: "2026-05-22T19:00:00Z", payment_method: "Credit Card" },
      { _id: '4', amount: 110.00, description: "Wifi Router broadband plan", category: "Utilities", date: "2026-05-18T08:00:00Z", payment_method: "Bank Transfer" },
      { _id: '5', amount: 75.00, description: "Cinema VIP tickets popcorn", category: "Entertainment", date: "2026-05-15T21:15:00Z", payment_method: "Debit Card" }
    ];
    setExpenses(sandboxExpenses);
    setActiveBudget({
      month: "2026-05",
      total_limit: 2000.0,
      category_limits: { "Food & Dining": 500.0, "Transport": 200.0, "Utilities": 300.0 }
    });
    recalculateOfflineInsights(sandboxExpenses);
  };

  const recalculateOfflineInsights = (currentList, customIncome = userIncome, customSafety = safetyAllocation) => {
    const total = currentList.reduce((acc, curr) => acc + curr.amount, 0);
    setForecasts([
      { month: "2026-06", predicted_amount: Math.round(total * 1.1 + 100), confidence_interval: [total * 0.9, total * 1.3] },
      { month: "2026-07", predicted_amount: Math.round(total * 1.2 + 150), confidence_interval: [total * 0.95, total * 1.45] }
    ]);
    
    const savingsRatio = customSafety / 100.0;
    const remainingRatio = 1.0 - savingsRatio;
    const needsRatio = remainingRatio * (5.0 / 8.0);
    const wantsRatio = remainingRatio * (3.0 / 8.0);
    
    const needs_cap = customIncome * needs_ratio;
    const wants_cap = customIncome * wants_ratio;
    const savings_cap = customIncome * savingsRatio;

    setInsights({
      income: customIncome,
      recommended_savings: Math.max(savings_cap, customIncome - total),
      recommended_limits: {
        "Food & Dining": Math.round(wants_cap * 0.40),
        "Transport": Math.round(wants_cap * 0.20),
        "Utilities": Math.round(needs_cap * 0.30),
        "Entertainment": Math.round(wants_cap * 0.20),
        "Housing": Math.round(needs_cap * 0.50),
        "Shopping": Math.round(wants_cap * 0.20)
      }
    });
  };

  // Calculations for Dash
  const totalExpensesSum = expenses.reduce((acc, curr) => acc + curr.amount, 0);
  const budgetRatio = activeBudget ? (totalExpensesSum / activeBudget.total_limit) * 100 : 0;

  // Render Login Panel if unauthenticated
  if (!token) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center', background: 'var(--dark-bg)' }}>
        <div className="glass-panel" style={{ padding: 40, width: 420, border: '1px solid var(--glass-border)' }}>
          <Space direction="vertical" align="center" style={{ width: '100%', marginBottom: 30 }}>
            <div style={{ background: 'var(--primary-gradient)', padding: 12, borderRadius: 15, display: 'inline-block', boxShadow: 'var(--neon-glow)' }}>
              <RocketOutlined style={{ fontSize: 32, color: '#fff' }} />
            </div>
            <Title level={2} className="glow-title" style={{ margin: 0 }}>AI Expense Tracker</Title>
            <Text type="secondary" style={{ color: 'var(--text-secondary)' }}>
              {isRegistering ? 'Setup a new ML analytical account' : 'Sign in to access your budget forecast'}
            </Text>
          </Space>

          {isRegistering ? (
            <Form form={registerForm} layout="vertical" onFinish={handleRegister}>
              <Form.Item name="name" label={<span style={{ color: 'var(--text-primary)' }}>Full Name</span>} rules={[{ required: true, message: 'Please input your name!' }]}>
                <Input prefix={<UserOutlined style={{ color: 'var(--text-secondary)' }} />} placeholder="Jane Doe" className="glass-input" />
              </Form.Item>
              <Form.Item name="email" label={<span style={{ color: 'var(--text-primary)' }}>Email Address</span>} rules={[{ required: true, type: 'email', message: 'Enter a valid email!' }]}>
                <Input prefix={<UserOutlined style={{ color: 'var(--text-secondary)' }} />} placeholder="jane.doe@example.com" className="glass-input" />
              </Form.Item>
              <Form.Item name="password" label={<span style={{ color: 'var(--text-primary)' }}>Secret Password</span>} rules={[{ required: true, min: 6, message: 'Password must be at least 6 characters!' }]}>
                <Input.Password prefix={<LockOutlined style={{ color: 'var(--text-secondary)' }} />} placeholder="••••••••" className="glass-input" />
              </Form.Item>
              <Button type="primary" htmlType="submit" className="btn-premium-neon" block loading={loading}>
                Register Account
              </Button>
              <div style={{ textAlign: 'center', marginTop: 15 }}>
                <Text style={{ color: 'var(--text-secondary)' }}>Already have an account? </Text>
                <a onClick={() => setIsRegistering(false)} style={{ color: '#a855f7' }}>Login Here</a>
              </div>
            </Form>
          ) : (
            <Form form={loginForm} layout="vertical" onFinish={handleLogin}>
              <Form.Item name="email" label={<span style={{ color: 'var(--text-primary)' }}>Email Address</span>} rules={[{ required: true, type: 'email', message: 'Enter a valid email!' }]}>
                <Input prefix={<UserOutlined style={{ color: 'var(--text-secondary)' }} />} placeholder="jane.doe@example.com" className="glass-input" />
              </Form.Item>
              <Form.Item name="password" label={<span style={{ color: 'var(--text-primary)' }}>Secret Password</span>} rules={[{ required: true, message: 'Please enter your password!' }]}>
                <Input.Password prefix={<LockOutlined style={{ color: 'var(--text-secondary)' }} />} placeholder="••••••••" className="glass-input" />
              </Form.Item>
              <Button type="primary" htmlType="submit" className="btn-premium-neon" block loading={loading}>
                Secure Authenticate
              </Button>
              <div style={{ textAlign: 'center', marginTop: 15 }}>
                <Text style={{ color: 'var(--text-secondary)' }}>Need a financial companion? </Text>
                <a onClick={() => setIsRegistering(true)} style={{ color: '#a855f7' }}>Sign Up Free</a>
              </div>
            </Form>
          )}
        </div>
      </div>
    );
  }

  // Define table schema inside Expense View
  const expenseColumns = [
    { title: 'Description', dataIndex: 'description', key: 'description', render: (t) => <Text style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{t}</Text> },
    { title: 'Category', dataIndex: 'category', key: 'category', render: (cat) => <Tag color="purple">{cat}</Tag> },
    { 
      title: 'Amount', 
      dataIndex: 'amount', 
      key: 'amount', 
      render: (val) => <span style={{ color: '#ef4444', fontWeight: 'bold' }}>-₹{parseFloat(val).toFixed(2)}</span> 
    },
    { 
      title: 'Date', 
      dataIndex: 'date', 
      key: 'date', 
      render: (d) => <span style={{ color: 'var(--text-secondary)' }}>{new Date(d).toLocaleDateString()}</span> 
    },
    { 
      title: 'Actions', 
      key: 'actions', 
      render: (_, record) => (
        <Button 
          type="text" 
          danger 
          icon={<DeleteOutlined />} 
          onClick={() => handleDeleteExpense(record._id)} 
        />
      ) 
    }
  ];

  return (
    <Layout style={{ minHeight: '100vh', background: 'transparent' }}>
      <Sider collapsible collapsed={collapsed} onCollapse={(v) => setCollapsed(v)} style={{ background: 'rgba(255, 255, 255, 0.85)', borderRight: '1px solid var(--glass-border)' }}>
        <div style={{ height: 60, margin: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
          <div style={{ background: 'var(--primary-gradient)', padding: 6, borderRadius: 10 }}>
            <RocketOutlined style={{ fontSize: 18, color: '#fff' }} />
          </div>
          {!collapsed && <span style={{ color: 'var(--text-primary)', fontWeight: 'bold', fontSize: 16, background: 'var(--primary-gradient)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>AI Expense Tracker</span>}
        </div>
        <Menu 
          theme="light" 
          mode="inline" 
          selectedKeys={[currentTab]} 
          style={{ background: 'transparent' }}
          onClick={({ key }) => setCurrentTab(key)}
        >
          <Menu.Item key="dashboard" icon={<LineChartOutlined />}>Dashboard</Menu.Item>
          <Menu.Item key="log" icon={<FormOutlined />}>Log Expense</Menu.Item>
          <Menu.Item key="budgets" icon={<PieChartOutlined />}>Active Limits</Menu.Item>
          <Menu.Item key="insights" icon={<SecurityScanOutlined />}>AI Predictor Room</Menu.Item>
        </Menu>
        <div style={{ position: 'absolute', bottom: 20, width: '100%', padding: '0 20px', textAlign: 'center' }}>
          <Button type="primary" size="small" danger onClick={handleLogout} block={!collapsed}>
            {collapsed ? 'X' : 'Secure Exit'}
          </Button>
        </div>
      </Sider>

      <Layout style={{ background: 'transparent' }}>
        <Header style={{ background: 'transparent', padding: '0 30px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: 70 }}>
          <Title level={4} style={{ color: 'var(--text-primary)', margin: 0 }}>Active Portal: <span className="glow-title" style={{ textTransform: 'capitalize' }}>{currentTab}</span></Title>
          <Space>
            <Tag color="cyan"><UserOutlined /> {user?.name || "Premium User"}</Tag>
            {token === 'offline_sandbox_token' && <Tag color="orange">Offline Sandbox Mode</Tag>}
          </Space>
        </Header>

        <Content style={{ padding: '0 30px 40px 30px' }}>
          
          {/* TAB 1: DASHBOARD PANEL */}
          {currentTab === 'dashboard' && (
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Row gutter={[20, 20]}>
                <Col xs={24} md={6}>
                  <Card className="glass-panel" bordered={false}>
                    <Statistic 
                      title={<span style={{ color: 'var(--text-secondary)' }}>Gross Expenditure</span>}
                      value={totalExpensesSum} 
                      precision={2} 
                      prefix="-₹" 
                      valueStyle={{ color: '#ef4444', fontWeight: 'bold' }} 
                    />
                  </Card>
                </Col>
                <Col xs={24} md={6}>
                  <Card className="glass-panel" bordered={false}>
                    <Statistic 
                      title={<span style={{ color: 'var(--text-secondary)' }}>Monthly Income</span>}
                      value={userIncome} 
                      precision={2} 
                      prefix="₹" 
                      valueStyle={{ color: '#6366f1', fontWeight: 'bold' }} 
                    />
                  </Card>
                </Col>
                <Col xs={24} md={6}>
                  <Card className="glass-panel" bordered={false}>
                    <Statistic 
                      title={<span style={{ color: 'var(--text-secondary)' }}>Safety Savings Target</span>}
                      value={(userIncome * safetyAllocation) / 100} 
                      precision={2} 
                      prefix="₹" 
                      valueStyle={{ color: '#10b981', fontWeight: 'bold' }} 
                    />
                  </Card>
                </Col>
                <Col xs={24} md={6}>
                  <Card className="glass-panel" bordered={false}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Budget Allocation Limit</span>
                      <span style={{ color: 'var(--text-primary)', fontWeight: 600 }}>{budgetRatio.toFixed(1)}% Used</span>
                    </div>
                    <Progress 
                      percent={Math.min(100, Math.round(budgetRatio))} 
                      status={budgetRatio > 90 ? "exception" : "normal"}
                      strokeColor={{ '0%': '#10b881', '100%': '#ef4444' }} 
                      trailColor="rgba(255,255,255,0.05)"
                    />
                  </Card>
                </Col>
              </Row>

              <Row gutter={[20, 20]}>
                <Col xs={24}>
                  <Card className="glass-panel" bordered={false}>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: 15 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: 10 }}>
                        <div>
                          <Title level={4} style={{ color: 'var(--text-primary)', margin: 0 }}>
                            🎯 Financial Planning & Safety Allocation Configurator
                          </Title>
                          <Text style={{ color: 'var(--text-secondary)' }}>
                            Personalize your monthly targets. The system automatically adjusts category thresholds and optimizer savings to match your safety margins.
                          </Text>
                        </div>
                      </div>
                      
                      <Row gutter={[30, 20]} align="middle">
                        <Col xs={24} md={10}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                            <Text strong style={{ color: 'var(--text-primary)' }}>Monthly Income (₹)</Text>
                            <Input 
                              type="number" 
                              value={userIncome} 
                              onChange={(e) => {
                                const val = parseFloat(e.target.value) || 0;
                                setUserIncome(val);
                                localStorage.setItem('user_income', val);
                              }}
                              className="glass-input" 
                              style={{ width: '100%' }}
                              placeholder="e.g. 50000"
                              prefix="₹"
                            />
                          </div>
                        </Col>
                        <Col xs={24} md={14}>
                          <div style={{ display: 'flex', flexDirection: 'column', gap: 5 }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                              <Text strong style={{ color: 'var(--text-primary)' }}>Safety Savings Allocation (%)</Text>
                              <Text strong style={{ color: '#10b981' }}>{safetyAllocation}% Selected</Text>
                            </div>
                            <Slider 
                              min={5} 
                              max={50} 
                              value={safetyAllocation} 
                              onChange={(val) => {
                                setSafetyAllocation(val);
                                localStorage.setItem('safety_allocation', val);
                              }}
                              tooltip={{ formatter: (v) => `${v}%` }}
                              marks={{
                                10: { style: { color: 'var(--text-secondary)' }, label: '10%' },
                                20: { style: { color: '#10b981', fontWeight: 'bold' }, label: '20% (Standard)' },
                                30: { style: { color: 'var(--text-secondary)' }, label: '30%' },
                                40: { style: { color: 'var(--text-secondary)' }, label: '40%' },
                                50: { style: { color: 'var(--text-secondary)' }, label: '50%' }
                              }}
                            />
                          </div>
                        </Col>
                      </Row>
                      
                      <Alert 
                        type="success"
                        showIcon
                        message={
                          <span style={{ fontWeight: 600 }}>
                            Current Safety Target: ₹{((userIncome * safetyAllocation) / 100).toFixed(2)} / Month
                          </span>
                        }
                        description={
                          <span>
                            This allocates <strong>{safetyAllocation}%</strong> of your income to secure reserves. 
                            The remaining <strong>{100 - safetyAllocation}%</strong> is dynamically budgeted into 
                            Needs (₹{((userIncome * (100 - safetyAllocation) * 5/8) / 100).toFixed(2)}) and Wants (₹{((userIncome * (100 - safetyAllocation) * 3/8) / 100).toFixed(2)}) using a 5:3 optimized priority model.
                          </span>
                        }
                        style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.15)', marginTop: 10 }}
                      />
                    </div>
                  </Card>
                </Col>
              </Row>

              <Row gutter={[20, 20]}>
                <Col xs={24} md={16}>
                  <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>Recent Expense Stream</span>} bordered={false}>
                    {expenses.length === 0 ? (
                      <Empty description={<span style={{ color: 'var(--text-secondary)' }}>No transactions registered. Add transactions in Log Expense.</span>} />
                    ) : (
                      <Table 
                        dataSource={expenses.slice(0, 5)} 
                        columns={expenseColumns} 
                        pagination={false} 
                        rowKey="_id"
                        style={{ background: 'transparent' }}
                        className="custom-dark-table"
                      />
                    )}
                  </Card>
                </Col>
                <Col xs={24} md={8}>
                  <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>Core Category Distribution</span>} bordered={false}>
                    {expenses.length === 0 ? (
                      <Empty description="No aggregates" />
                    ) : (
                      <Space direction="vertical" style={{ width: '100%' }}>
                        {Object.entries(
                          expenses.reduce((acc, curr) => {
                            acc[curr.category] = (acc[curr.category] || 0) + curr.amount;
                            return acc;
                          }, {})
                        ).map(([cat, total]) => (
                          <div key={cat} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Text style={{ color: 'var(--text-secondary)' }}>{cat}</Text>
                            <Tag color="cyan">₹{parseFloat(total).toFixed(2)}</Tag>
                          </div>
                        ))}
                      </Space>
                    )}
                  </Card>
                </Col>
              </Row>
            </Space>
          )}

          {/* TAB 2: LOG EXPENSE PANEL */}
          {currentTab === 'log' && (
            <Row gutter={[20, 20]}>
              <Col xs={24} md={12}>
                <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>Submit New Expense (Auto-Categorized)</span>} bordered={false}>
                  <Form form={expenseForm} layout="vertical" onFinish={handleAddExpense}>
                    <Form.Item name="description" label={<span style={{ color: 'var(--text-primary)' }}>Transaction Memo</span>} rules={[{ required: true }]}>
                      <Input 
                        placeholder="e.g., Dinner at Starbucks with friends" 
                        onChange={handleDescriptionChange}
                        className="glass-input"
                      />
                    </Form.Item>
                    <Form.Item name="amount" label={<span style={{ color: 'var(--text-primary)' }}>Amount Paid (₹)</span>} rules={[{ required: true }]}>
                      <Input type="number" step="0.01" placeholder="14.50" className="glass-input" />
                    </Form.Item>
                    <Form.Item name="category" label={<span style={{ color: 'var(--text-primary)' }}>Resolved Category</span>} rules={[{ required: true }]}>
                      <Input placeholder="Click auto-suggest or type custom category" className="glass-input" />
                    </Form.Item>
                    <Form.Item name="payment_method" label={<span style={{ color: 'var(--text-primary)' }}>Payment Route</span>}>
                      <Input placeholder="Credit Card, Cash, etc." className="glass-input" />
                    </Form.Item>
                    
                    <Button type="primary" htmlType="submit" className="btn-premium-neon" block loading={loading}>
                      Log Secure Transaction
                    </Button>
                  </Form>
                </Card>
              </Col>
              
              <Col xs={24} md={12}>
                <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>AI Auto-Classification Assist</span>} bordered={false}>
                  {mlLoading ? (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                      <RocketOutlined spin style={{ fontSize: 36, color: '#a855f7', marginBottom: 15 }} />
                      <Paragraph style={{ color: 'var(--text-secondary)' }}>Auto-processing NLP features using custom weights...</Paragraph>
                    </div>
                  ) : suggestedCategory ? (
                    <Space direction="vertical" style={{ width: '100%' }} size="middle">
                      <Alert 
                        message={<span style={{ fontWeight: 600 }}>Classification Confidence Established!</span>}
                        description={`Our Multinomial Naive Bayes pipeline classified your description string into the following category.`}
                        type="info"
                        showIcon
                      />
                      <div style={{ padding: '20px 0', textAlign: 'center', background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid var(--glass-border)' }}>
                        <Title level={3} style={{ color: '#a855f7', margin: 0 }}>{suggestedCategory}</Title>
                        <Text type="secondary">Prediction Confidence: {(suggestionConfidence * 100).toFixed(1)}%</Text>
                      </div>
                      <Button type="dashed" className="btn-premium-neon" style={{ background: 'transparent' }} onClick={applySuggestedCategory} block>
                        Apply AI Suggested Category Label
                      </Button>
                    </Space>
                  ) : (
                    <div style={{ textAlign: 'center', padding: '40px 0' }}>
                      <RocketOutlined style={{ fontSize: 36, color: 'var(--text-secondary)', marginBottom: 15 }} />
                      <Paragraph style={{ color: 'var(--text-secondary)' }}>
                        Begin typing inside the Transaction Memo (e.g. "latte", "uber rides") to trigger live ML categorization.
                      </Paragraph>
                    </div>
                  )}
                </Card>
              </Col>
            </Row>
          )}

          {/* TAB 3: BUDGET PANELS */}
          {currentTab === 'budgets' && (
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>Active Target Budget Bounds</span>} bordered={false}>
                <Row gutter={[20, 20]}>
                  <Col xs={24} md={8}>
                    <Statistic title={<span style={{ color: 'var(--text-secondary)' }}>Combined Monthly Limit</span>} value={activeBudget?.total_limit || 2000.0} prefix="₹" valueStyle={{ color: 'var(--text-primary)' }} />
                  </Col>
                  <Col xs={24} md={16}>
                    <Paragraph style={{ color: 'var(--text-secondary)' }}>
                      Adjust your spending guardrails to maintain high compliance scores. The AI Predictor Room will recommend boundaries based on your transaction ratios.
                    </Paragraph>
                  </Col>
                </Row>
              </Card>

              <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}>Category Limits Monitoring</span>} bordered={false}>
                {activeBudget?.category_limits ? (
                  <Row gutter={[20, 20]}>
                    {Object.entries(activeBudget.category_limits).map(([cat, limit]) => {
                      const spent = expenses.filter(e => e.category === cat).reduce((acc, curr) => acc + curr.amount, 0);
                      const percent = Math.round((spent / limit) * 100);
                      return (
                        <Col xs={24} md={8} key={cat}>
                          <div style={{ background: 'rgba(255,255,255,0.01)', padding: 20, borderRadius: 15, border: '1px solid var(--glass-border)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 10 }}>
                              <Text strong style={{ color: 'var(--text-primary)' }}>{cat}</Text>
                              <Text style={{ color: percent > 90 ? '#ef4444' : 'var(--text-secondary)' }}>₹{spent.toFixed(0)} / ₹{limit.toFixed(0)}</Text>
                            </div>
                            <Progress 
                              percent={Math.min(100, percent)} 
                              status={percent > 100 ? "exception" : "normal"}
                              strokeColor={percent > 90 ? '#ef4444' : '#6366f1'} 
                              trailColor="rgba(255,255,255,0.03)"
                            />
                          </div>
                        </Col>
                      );
                    })}
                  </Row>
                ) : (
                  <Empty />
                )}
              </Card>
            </Space>
          )}

          {/* TAB 4: AI Predictor Lounge */}
          {currentTab === 'insights' && (
            <Space direction="vertical" size="large" style={{ width: '100%' }}>
              <Row gutter={[20, 20]}>
                <Col xs={24} md={12}>
                  <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}><RocketOutlined /> Expense Projections (3-Month ML Forecast)</span>} bordered={false}>
                    {forecasts.length === 0 ? (
                      <Empty description="No forecasts" />
                    ) : (
                      <Space direction="vertical" style={{ width: '100%' }} size="large">
                        <Alert 
                          message="Time-Series Linear Forecasting Generated"
                          description="This forecasting models are built using linear extrapolations of your daily cumulative spending streams."
                          type="success"
                          showIcon
                        />
                        {forecasts.map((f, idx) => (
                          <div key={idx} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '15px 20px', background: 'rgba(255,255,255,0.02)', borderRadius: 12, border: '1px solid var(--glass-border)' }}>
                            <div>
                              <Text strong style={{ color: 'var(--text-primary)' }}>Month: {f.month}</Text>
                              <br />
                              <Text type="secondary">Confidence Bounds: ₹{f.confidence_interval[0].toFixed(0)} - ₹{f.confidence_interval[1].toFixed(0)}</Text>
                            </div>
                            <Statistic value={f.predicted_amount} precision={2} prefix="₹" valueStyle={{ color: '#a855f7', fontWeight: 'bold' }} />
                          </div>
                        ))}
                      </Space>
                    )}
                  </Card>
                </Col>

                <Col xs={24} md={12}>
                  <Card className="glass-panel" title={<span style={{ color: 'var(--text-primary)' }}><SecurityScanOutlined /> Spending Optimization Insights</span>} bordered={false}>
                    {insights ? (
                      <Space direction="vertical" style={{ width: '100%' }} size="middle">
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10, background: 'rgba(16,185,129,0.05)', padding: 15, borderRadius: 12, border: '1px solid rgba(16,185,129,0.1)' }}>
                          <CheckCircleOutlined style={{ color: '#10b981', fontSize: 20 }} />
                          <div>
                            <Text strong style={{ color: '#10b981' }}>Optimized Savings Allocation</Text>
                            <br />
                            <Text style={{ color: 'var(--text-secondary)' }}>Suggested minimum target savings: <strong style={{ color: 'var(--text-primary)' }}>₹{insights.recommended_savings.toFixed(2)}</strong></Text>
                          </div>
                        </div>

                        <Text strong style={{ color: 'var(--text-primary)', marginTop: 10, display: 'block' }}>Category allocations compared with standard ratios:</Text>
                        
                        {Object.entries(insights.recommended_limits).map(([cat, recommendedLimit]) => {
                          const currentSpent = expenses.filter(e => e.category === cat).reduce((acc, curr) => acc + curr.amount, 0);
                          const isCompliant = currentSpent <= recommendedLimit;
                          return (
                            <div key={cat} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '1px solid var(--glass-border)', paddingBottom: 8 }}>
                              <div>
                                <Text style={{ color: 'var(--text-primary)' }}>{cat}</Text>
                                <br />
                                <Text type="secondary" style={{ fontSize: 12 }}>Spent: ₹{currentSpent.toFixed(0)} / Target Max: ₹{recommendedLimit.toFixed(0)}</Text>
                              </div>
                              <Tag color={isCompliant ? "emerald" : "rose"}>
                                {isCompliant ? "Compliant Ratio" : "Alert: Over Target"}
                              </Tag>
                            </div>
                          );
                        })}
                      </Space>
                    ) : (
                      <Empty description="Aggregate data points are required to train baseline spending recommendation models." />
                    )}
                  </Card>
                </Col>
              </Row>
            </Space>
          )}

        </Content>
      </Layout>
    </Layout>
  );
}

export default App;
