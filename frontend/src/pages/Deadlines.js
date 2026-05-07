import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { deadlinesService } from '../services/deadlines';
import '../App.css';

function Deadlines({ onLogout }) {
  const navigate = useNavigate();
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    case_id: '',
    due_date: '',
    description: '',
    status: 'pending',
  });

  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    case_id: '',
  });

  useEffect(() => {
    fetchDeadlines();
  }, [filters]);

  const fetchDeadlines = async () => {
    try {
      setLoading(true);
      const data = await deadlinesService.getAllDeadlines(0, 20, filters);
      setDeadlines(data.data || []);
    } catch (err) {
      setError('Failed to fetch deadlines');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await deadlinesService.updateDeadline(editingId, formData);
      } else {
        await deadlinesService.createDeadline(formData);
      }
      setFormData({ case_id: '', due_date: '', description: '', status: 'pending' });
      setShowForm(false);
      setEditingId(null);
      fetchDeadlines();
    } catch (err) {
      setError('Failed to save deadline');
      console.error(err);
    }
  };

  const handleEdit = (deadline) => {
    setFormData({
      case_id: deadline.case_id,
      due_date: deadline.due_date,
      description: deadline.description,
      status: deadline.status,
    });
    setEditingId(deadline.id);
    setShowForm(true);
  };

  const handleComplete = async (id) => {
    try {
      await deadlinesService.completeDeadline(id);
      fetchDeadlines();
    } catch (err) {
      setError('Failed to complete deadline');
      console.error(err);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this deadline?')) {
      try {
        await deadlinesService.deleteDeadline(id);
        fetchDeadlines();
      } catch (err) {
        setError('Failed to delete deadline');
        console.error(err);
      }
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  const handleCancel = () => {
    setShowForm(false);
    setEditingId(null);
    setFormData({ case_id: '', due_date: '', description: '', status: 'pending' });
  };

  const getDaysRemaining = (dueDate) => {
    const today = new Date();
    const due = new Date(dueDate);
    const diff = Math.ceil((due - today) / (1000 * 60 * 60 * 24));
    return diff;
  };

  return (
    <div className="page">
      <nav className="nav-bar">
        <h1>Deadlines</h1>
        <ul className="nav-links">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/cases">Cases</Link></li>
          <li><Link to="/deadlines">Deadlines</Link></li>
          <li><Link to="/ai-assistant">AI Assistant</Link></li>
          <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
        </ul>
      </nav>

      <div className="container">
        <h2>Deadline Management</h2>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Filters */}
        <div className="card">
          <h3>Filters</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <input
              type="number"
              placeholder="Filter by case ID"
              value={filters.case_id}
              onChange={(e) => setFilters({ ...filters, case_id: e.target.value })}
            />
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="completed">Completed</option>
              <option value="missed">Missed</option>
            </select>
          </div>
        </div>

        {/* Create Button */}
        <div style={{ marginBottom: '1rem', marginTop: '1rem' }}>
          {!showForm && (
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              + New Deadline
            </button>
          )}
        </div>

        {/* Create/Edit Form */}
        {showForm && (
          <div className="card">
            <h3>{editingId ? 'Edit Deadline' : 'Create New Deadline'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Case ID *</label>
                <input
                  type="number"
                  value={formData.case_id}
                  onChange={(e) => setFormData({ ...formData, case_id: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Due Date *</label>
                <input
                  type="date"
                  value={formData.due_date}
                  onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows="4"
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="pending">Pending</option>
                  <option value="completed">Completed</option>
                  <option value="missed">Missed</option>
                </select>
              </div>

              <div style={{ display: 'flex', gap: '1rem' }}>
                <button type="submit" className="btn btn-primary">
                  {editingId ? 'Update' : 'Create'}
                </button>
                <button type="button" className="btn btn-secondary" onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Deadlines List */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>Loading deadlines...</div>
        ) : deadlines.length === 0 ? (
          <div className="card">
            <p>No deadlines found. Create one to get started.</p>
          </div>
        ) : (
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>Case ID</th>
                  <th>Due Date</th>
                  <th>Days Remaining</th>
                  <th>Status</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {deadlines.map((deadline) => {
                  const daysRemaining = getDaysRemaining(deadline.due_date);
                  return (
                    <tr key={deadline.id}>
                      <td>{deadline.case_id}</td>
                      <td>{new Date(deadline.due_date).toLocaleDateString()}</td>
                      <td style={{ color: daysRemaining < 0 ? '#e74c3c' : '#27ae60' }}>
                        {daysRemaining < 0 ? `${Math.abs(daysRemaining)} days overdue` : `${daysRemaining} days`}
                      </td>
                      <td>{deadline.status}</td>
                      <td>{deadline.description}</td>
                      <td style={{ display: 'flex', gap: '0.5rem' }}>
                        {deadline.status === 'pending' && (
                          <button
                            className="btn btn-secondary"
                            onClick={() => handleComplete(deadline.id)}
                            style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                          >
                            Complete
                          </button>
                        )}
                        <button
                          className="btn btn-secondary"
                          onClick={() => handleEdit(deadline)}
                          style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                        >
                          Edit
                        </button>
                        <button
                          className="btn btn-danger"
                          onClick={() => handleDelete(deadline.id)}
                          style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Deadlines;
