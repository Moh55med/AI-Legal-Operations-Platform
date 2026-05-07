import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { casesService } from '../services/cases';
import { deadlinesService } from '../services/deadlines';
import '../App.css';

function Dashboard({ onLogout }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    activeCases: 0,
    upcomingDeadlines: 0,
    overdueDeadlines: 0,
  });
  const [recentCases, setRecentCases] = useState([]);
  const [recentDeadlines, setRecentDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [casesData, pendingDeadlinesData, overdueDeadlinesData] = await Promise.all([
        casesService.getAllCases(0, 5, { status: 'open' }),
        deadlinesService.getPendingDeadlines(0, 5),
        deadlinesService.getOverdueDeadlines(0, 5),
      ]);

      setRecentCases(casesData.data || []);
      setRecentDeadlines(pendingDeadlinesData.data || []);

      setStats({
        activeCases: casesData.total || 0,
        upcomingDeadlines: pendingDeadlinesData.total || 0,
        overdueDeadlines: overdueDeadlinesData.total || 0,
      });
    } catch (err) {
      setError('Failed to fetch dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  return (
    <div className="page">
      <nav className="nav-bar">
        <h1>Dashboard</h1>
        <ul className="nav-links">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/cases">Cases</Link></li>
          <li><Link to="/deadlines">Deadlines</Link></li>
          <li><Link to="/ai-assistant">AI Assistant</Link></li>
          <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
        </ul>
      </nav>

      <div className="container">
        <h2>Welcome to AI Legal Operations Platform</h2>

        {error && <div className="alert alert-error">{error}</div>}

        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>Loading...</div>
        ) : (
          <>
            <div className="grid">
              <div className="card stat-card">
                <h3>Active Cases</h3>
                <div className="value">{stats.activeCases}</div>
                <Link to="/cases" style={{ marginTop: '1rem', display: 'block' }}>
                  View Cases →
                </Link>
              </div>

              <div className="card stat-card">
                <h3>Upcoming Deadlines</h3>
                <div className="value">{stats.upcomingDeadlines}</div>
                <Link to="/deadlines" style={{ marginTop: '1rem', display: 'block' }}>
                  View Deadlines →
                </Link>
              </div>

              <div className="card stat-card">
                <h3>Overdue</h3>
                <div className="value" style={{ color: '#e74c3c' }}>{stats.overdueDeadlines}</div>
                <Link to="/deadlines" style={{ marginTop: '1rem', display: 'block', color: '#e74c3c' }}>
                  View Overdue →
                </Link>
              </div>
            </div>

            {recentCases.length > 0 && (
              <div className="card">
                <h3>Recent Cases</h3>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Title</th>
                      <th>Reference</th>
                      <th>Status</th>
                      <th>Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentCases.map((caseItem) => (
                      <tr key={caseItem.id}>
                        <td>{caseItem.title}</td>
                        <td>{caseItem.case_reference_number}</td>
                        <td>{caseItem.status}</td>
                        <td>
                          <Link to={`/cases/${caseItem.id}`} className="btn btn-primary">
                            View
                          </Link>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            {recentDeadlines.length > 0 && (
              <div className="card">
                <h3>Upcoming Deadlines</h3>
                <table className="table">
                  <thead>
                    <tr>
                      <th>Due Date</th>
                      <th>Description</th>
                      <th>Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {recentDeadlines.map((deadline) => (
                      <tr key={deadline.id}>
                        <td>{new Date(deadline.due_date).toLocaleDateString()}</td>
                        <td>{deadline.description}</td>
                        <td>{deadline.status}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

            <div className="card" style={{ marginTop: '2rem' }}>
              <h3>Quick Actions</h3>
              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
                <Link to="/cases" className="btn btn-primary">Manage Cases</Link>
                <Link to="/deadlines" className="btn btn-secondary">Manage Deadlines</Link>
                <Link to="/ai-assistant" className="btn btn-secondary">Ask AI Assistant</Link>
              </div>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
