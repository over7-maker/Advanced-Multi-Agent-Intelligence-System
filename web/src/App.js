import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import {
  Layout,
  Menu,
  Card,
  Row,
  Col,
  Statistic,
  Table,
  Tag,
  Button,
  Input,
  Select,
  Space,
  Typography,
  Alert,
  Spin,
  message,
  Tabs,
  Timeline,
  Progress,
  Badge
} from 'antd';
import {
  DashboardOutlined,
  RobotOutlined,
  FileTextOutlined,
  BarChartOutlined,
  SettingOutlined,
  PlayCircleOutlined,
  PauseCircleOutlined,
  ReloadOutlined,
  PlusOutlined,
  SearchOutlined,
  EyeOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  ClockCircleOutlined
} from '@ant-design/icons';
import axios from 'axios';
import './index.css';

const { Header, Sider, Content } = Layout;
const { Title, Text } = Typography;
const { Option } = Select;
const { TabPane } = Tabs;

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
const API_TOKEN = process.env.REACT_APP_API_TOKEN || 'valid_token';

// API Client
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Authorization': `Bearer ${API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Dashboard Component
const Dashboard = () => {
  const [systemStatus, setSystemStatus] = useState(null);
  const [agents, setAgents] = useState([]);
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
    const interval = setInterval(loadDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadDashboardData = async () => {
    try {
      const [statusRes, agentsRes] = await Promise.all([
        apiClient.get('/status'),
        apiClient.get('/agents')
      ]);

      setSystemStatus(statusRes.data);
      setAgents(agentsRes.data.agents || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading dashboard data:', error);
      message.error('Failed to load dashboard data');
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return '#52c41a';
      case 'inactive': return '#ff4d4f';
      case 'pending': return '#faad14';
      default: return '#d9d9d9';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'active': return <CheckCircleOutlined />;
      case 'inactive': return <ExclamationCircleOutlined />;
      case 'pending': return <ClockCircleOutlined />;
      default: return <ClockCircleOutlined />;
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div>
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={12} md={6}>
          <Card className="amas-metric-card">
            <div className="amas-metric-value">
              {systemStatus?.active_agents || 0}
            </div>
            <div className="amas-metric-label">Active Agents</div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="amas-metric-card">
            <div className="amas-metric-value">
              {tasks.filter(t => t.status === 'completed').length}
            </div>
            <div className="amas-metric-label">Completed Tasks</div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="amas-metric-card">
            <div className="amas-metric-value">
              {tasks.filter(t => t.status === 'pending').length}
            </div>
            <div className="amas-metric-label">Pending Tasks</div>
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card className="amas-metric-card">
            <div className="amas-metric-value">
              {systemStatus?.orchestrator_status === 'active' ? '100%' : '0%'}
            </div>
            <div className="amas-metric-label">System Health</div>
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="System Status" className="amas-card">
            <Space direction="vertical" style={{ width: '100%' }}>
              <div>
                <Text strong>Orchestrator Status: </Text>
                <Tag color={getStatusColor(systemStatus?.orchestrator_status)}>
                  {getStatusIcon(systemStatus?.orchestrator_status)}
                  {systemStatus?.orchestrator_status || 'Unknown'}
                </Tag>
              </div>
              <div>
                <Text strong>Active Agents: </Text>
                <Badge count={systemStatus?.active_agents || 0} />
              </div>
              <div>
                <Text strong>Last Updated: </Text>
                <Text>{new Date().toLocaleString()}</Text>
              </div>
            </Space>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Agent Status" className="amas-card">
            <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
              {agents.map(agent => (
                <div key={agent.agent_id} style={{ marginBottom: '8px' }}>
                  <Space>
                    <span className={`amas-status-indicator amas-status-${agent.status}`} />
                    <Text strong>{agent.name}</Text>
                    <Tag color={getStatusColor(agent.status)}>
                      {agent.status}
                    </Tag>
                  </Space>
                </div>
              ))}
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// Agents Component
const Agents = () => {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAgents();
    const interval = setInterval(loadAgents, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadAgents = async () => {
    try {
      const response = await apiClient.get('/agents');
      setAgents(response.data.agents || []);
      setLoading(false);
    } catch (error) {
      console.error('Error loading agents:', error);
      message.error('Failed to load agents');
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active': return 'green';
      case 'inactive': return 'red';
      case 'pending': return 'orange';
      default: return 'default';
    }
  };

  const columns = [
    {
      title: 'Agent ID',
      dataIndex: 'agent_id',
      key: 'agent_id',
      render: (text) => <Text code>{text}</Text>
    },
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {status}
        </Tag>
      )
    },
    {
      title: 'Capabilities',
      dataIndex: 'capabilities',
      key: 'capabilities',
      render: (capabilities) => (
        <div>
          {capabilities.slice(0, 3).map(cap => (
            <Tag key={cap} size="small">{cap}</Tag>
          ))}
          {capabilities.length > 3 && (
            <Tag size="small">+{capabilities.length - 3} more</Tag>
          )}
        </div>
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />}>
            View
          </Button>
          <Button size="small" icon={<ReloadOutlined />}>
            Restart
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '16px' }}>
        <Button type="primary" icon={<PlusOutlined />}>
          Add Agent
        </Button>
        <Button icon={<ReloadOutlined />} style={{ marginLeft: '8px' }}>
          Refresh
        </Button>
      </div>
      
      <Card className="amas-card">
        <Table
          columns={columns}
          dataSource={agents}
          loading={loading}
          rowKey="agent_id"
          pagination={{ pageSize: 10 }}
        />
      </Card>
    </div>
  );
};

// Tasks Component
const Tasks = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    loadTasks();
  }, []);

  const loadTasks = async () => {
    try {
      // In a real implementation, you'd have a GET /tasks endpoint
      setTasks([]);
      setLoading(false);
    } catch (error) {
      console.error('Error loading tasks:', error);
      message.error('Failed to load tasks');
      setLoading(false);
    }
  };

  const submitTask = async (taskData) => {
    setSubmitting(true);
    try {
      const response = await apiClient.post('/tasks', taskData);
      message.success('Task submitted successfully');
      loadTasks();
      return response.data.task_id;
    } catch (error) {
      console.error('Error submitting task:', error);
      message.error('Failed to submit task');
      return null;
    } finally {
      setSubmitting(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'green';
      case 'failed': return 'red';
      case 'pending': return 'orange';
      case 'running': return 'blue';
      default: return 'default';
    }
  };

  const taskColumns = [
    {
      title: 'Task ID',
      dataIndex: 'task_id',
      key: 'task_id',
      render: (text) => <Text code>{text}</Text>
    },
    {
      title: 'Type',
      dataIndex: 'type',
      key: 'type',
      render: (type) => <Tag color="blue">{type}</Tag>
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description'
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => (
        <Tag color={getStatusColor(status)}>
          {status}
        </Tag>
      )
    },
    {
      title: 'Priority',
      dataIndex: 'priority',
      key: 'priority',
      render: (priority) => (
        <Badge count={priority} style={{ backgroundColor: '#52c41a' }} />
      )
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button size="small" icon={<EyeOutlined />}>
            View
          </Button>
          <Button size="small" icon={<ReloadOutlined />}>
            Retry
          </Button>
        </Space>
      )
    }
  ];

  return (
    <div>
      <Card title="Task Management" className="amas-card" style={{ marginBottom: '16px' }}>
        <Tabs defaultActiveKey="submit">
          <TabPane tab="Submit Task" key="submit">
            <TaskSubmissionForm onSubmit={submitTask} loading={submitting} />
          </TabPane>
          <TabPane tab="Task History" key="history">
            <Table
              columns={taskColumns}
              dataSource={tasks}
              loading={loading}
              rowKey="task_id"
              pagination={{ pageSize: 10 }}
            />
          </TabPane>
        </Tabs>
      </Card>
    </div>
  );
};

// Task Submission Form
const TaskSubmissionForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    type: 'osint',
    description: '',
    parameters: {},
    priority: 1
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  const taskTypes = [
    { value: 'osint', label: 'OSINT Collection' },
    { value: 'investigation', label: 'Investigation' },
    { value: 'forensics', label: 'Forensics' },
    { value: 'data_analysis', label: 'Data Analysis' },
    { value: 'reverse_engineering', label: 'Reverse Engineering' },
    { value: 'metadata', label: 'Metadata Analysis' },
    { value: 'reporting', label: 'Reporting' },
    { value: 'technology_monitor', label: 'Technology Monitor' }
  ];

  return (
    <form onSubmit={handleSubmit}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <div>
          <Text strong>Task Type:</Text>
          <Select
            value={formData.type}
            onChange={(value) => setFormData({ ...formData, type: value })}
            style={{ width: '100%', marginTop: '8px' }}
          >
            {taskTypes.map(type => (
              <Option key={type.value} value={type.value}>
                {type.label}
              </Option>
            ))}
          </Select>
        </div>
        
        <div>
          <Text strong>Description:</Text>
          <Input.TextArea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Describe the task to be performed..."
            rows={3}
            style={{ marginTop: '8px' }}
          />
        </div>
        
        <div>
          <Text strong>Priority:</Text>
          <Select
            value={formData.priority}
            onChange={(value) => setFormData({ ...formData, priority: value })}
            style={{ width: '100%', marginTop: '8px' }}
          >
            <Option value={1}>High</Option>
            <Option value={2}>Medium</Option>
            <Option value={3}>Low</Option>
          </Select>
        </div>
        
        <Button
          type="primary"
          htmlType="submit"
          loading={loading}
          icon={<PlayCircleOutlined />}
          style={{ width: '100%' }}
        >
          Submit Task
        </Button>
      </Space>
    </form>
  );
};

// Analytics Component
const Analytics = () => {
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalytics();
  }, []);

  const loadAnalytics = async () => {
    try {
      // Mock analytics data
      setAnalyticsData({
        taskCompletion: [
          { name: 'OSINT', value: 45 },
          { name: 'Forensics', value: 30 },
          { name: 'Investigation', value: 25 }
        ],
        agentPerformance: [
          { name: 'OSINT Agent', efficiency: 95 },
          { name: 'Forensics Agent', efficiency: 88 },
          { name: 'Investigation Agent', efficiency: 92 }
        ]
      });
      setLoading(false);
    } catch (error) {
      console.error('Error loading analytics:', error);
      message.error('Failed to load analytics');
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: '16px' }}>Loading analytics...</div>
      </div>
    );
  }

  return (
    <div>
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card title="Task Completion Distribution" className="amas-chart-container">
            <div style={{ height: '300px' }}>
              {/* In a real implementation, you'd use a chart library like Recharts */}
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Text>Chart visualization would go here</Text>
              </div>
            </div>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="Agent Performance" className="amas-chart-container">
            <div style={{ height: '300px' }}>
              <div style={{ textAlign: 'center', padding: '50px' }}>
                <Text>Performance metrics would go here</Text>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

// Settings Component
const Settings = () => {
  const [settings, setSettings] = useState({
    systemName: 'AMAS',
    maxConcurrentTasks: 10,
    autoRestart: true,
    logLevel: 'info'
  });

  const handleSave = () => {
    message.success('Settings saved successfully');
  };

  return (
    <div>
      <Card title="System Settings" className="amas-card">
        <Space direction="vertical" style={{ width: '100%' }}>
          <div>
            <Text strong>System Name:</Text>
            <Input
              value={settings.systemName}
              onChange={(e) => setSettings({ ...settings, systemName: e.target.value })}
              style={{ marginTop: '8px' }}
            />
          </div>
          
          <div>
            <Text strong>Max Concurrent Tasks:</Text>
            <Input
              type="number"
              value={settings.maxConcurrentTasks}
              onChange={(e) => setSettings({ ...settings, maxConcurrentTasks: parseInt(e.target.value) })}
              style={{ marginTop: '8px' }}
            />
          </div>
          
          <div>
            <Text strong>Auto Restart:</Text>
            <Select
              value={settings.autoRestart}
              onChange={(value) => setSettings({ ...settings, autoRestart: value })}
              style={{ width: '100%', marginTop: '8px' }}
            >
              <Option value={true}>Enabled</Option>
              <Option value={false}>Disabled</Option>
            </Select>
          </div>
          
          <div>
            <Text strong>Log Level:</Text>
            <Select
              value={settings.logLevel}
              onChange={(value) => setSettings({ ...settings, logLevel: value })}
              style={{ width: '100%', marginTop: '8px' }}
            >
              <Option value="debug">Debug</Option>
              <Option value="info">Info</Option>
              <Option value="warn">Warning</Option>
              <Option value="error">Error</Option>
            </Select>
          </div>
          
          <Button type="primary" onClick={handleSave} style={{ width: '100%' }}>
            Save Settings
          </Button>
        </Space>
      </Card>
    </div>
  );
};

// Main App Component
const App = () => {
  const [collapsed, setCollapsed] = useState(false);
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard'
    },
    {
      key: '/agents',
      icon: <RobotOutlined />,
      label: 'Agents'
    },
    {
      key: '/tasks',
      icon: <FileTextOutlined />,
      label: 'Tasks'
    },
    {
      key: '/analytics',
      icon: <BarChartOutlined />,
      label: 'Analytics'
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings'
    }
  ];

  const renderContent = () => {
    switch (location.pathname) {
      case '/':
        return <Dashboard />;
      case '/agents':
        return <Agents />;
      case '/tasks':
        return <Tasks />;
      case '/analytics':
        return <Analytics />;
      case '/settings':
        return <Settings />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <Router>
      <Layout className="amas-container" style={{ minHeight: '100vh' }}>
        <Sider
          collapsible
          collapsed={collapsed}
          onCollapse={setCollapsed}
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)'
          }}
        >
          <div style={{ 
            padding: '16px', 
            textAlign: 'center',
            borderBottom: '1px solid rgba(255, 255, 255, 0.2)'
          }}>
            <Title level={4} style={{ color: 'white', margin: 0 }}>
              {collapsed ? 'AMAS' : 'AMAS System'}
            </Title>
          </div>
          <Menu
            theme="dark"
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems.map(item => ({
              key: item.key,
              icon: item.icon,
              label: <Link to={item.key}>{item.label}</Link>
            }))}
            style={{ background: 'transparent' }}
          />
        </Sider>
        
        <Layout>
          <Header className="amas-header" style={{ padding: '0 24px' }}>
            <Title level={3} style={{ color: 'white', margin: 0 }}>
              Advanced Multi-Agent Intelligence System
            </Title>
          </Header>
          
          <Content style={{ padding: '24px', background: 'transparent' }}>
            {renderContent()}
          </Content>
        </Layout>
      </Layout>
    </Router>
  );
};

export default App;