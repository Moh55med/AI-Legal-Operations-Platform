import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { casesService } from '../services/cases';
import '../App.css';

function Cases({ onLogout }) {
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    client_id: '',
    status: 'open',
    description: '',
  });

  // Filter state
  const [filters, setFilters] = useState({
    status: '',
    title: '',
    client_name: '',
  });

  useEffect(() => {
    fetchCases();
  }, [filters]);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const data = await casesService.getAllCases(0, 20, filters);
      setCases(data.data || []);
    } catch (err) {
      setError('Failed to fetch cases');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingId) {
        await casesService.updateCase(editingId, formData);
      } else {
        await casesService.createCase(formData);
      }
      setFormData({ title: '', client_id: '', status: 'open', description: '' });
      setShowForm(false);
      setEditingId(null);
      fetchCases();
    } catch (err) {
      setError('Failed to save case');
      console.error(err);
    }
  };

  const handleEdit = (caseItem) => {
    setFormData({
      title: caseItem.title,
      client_id: caseItem.client_id,
      status: caseItem.status,
      description: caseItem.description,
    });
    setEditingId(caseItem.id);
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this case?')) {
      try {
        await casesService.deleteCase(id);
        fetchCases();
      } catch (err) {
        setError('Failed to delete case');
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
    setFormData({ title: '', client_id: '', status: 'open', description: '' });
  };

  return (
    <div className="page">
      <nav className="nav-bar">
        <h1>Cases</h1>
        <ul className="nav-links">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/cases">Cases</Link></li>
          <li><Link to="/deadlines">Deadlines</Link></li>
          <li><Link to="/ai-assistant">AI Assistant</Link></li>
          <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
        </ul>
      </nav>

      <div className="container">
        <h2>Case Management</h2>

        {error && <div className="alert alert-error">{error}</div>}

        {/* Filters */}
        <div className="card">
          <h3>Filters</h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
            <input
              type="text"
              placeholder="Search by title"
              value={filters.title}
              onChange={(e) => setFilters({ ...filters, title: e.target.value })}
            />
            <input
              type="text"
              placeholder="Search by client"
              value={filters.client_name}
              onChange={(e) => setFilters({ ...filters, client_name: e.target.value })}
            />
            <select
              value={filters.status}
              onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            >
              <option value="">All Statuses</option>
              <option value="open">Open</option>
              <option value="closed">Closed</option>
              <option value="on_hold">On Hold</option>
            </select>
          </div>
        </div>

        {/* Create Button */}
        <div style={{ marginBottom: '1rem', marginTop: '1rem' }}>
          {!showForm && (
            <button className="btn btn-primary" onClick={() => setShowForm(true)}>
              + New Case
            </button>
          )}
        </div>

        {/* Create/Edit Form */}
        {showForm && (
          <div className="card">
            <h3>{editingId ? 'Edit Case' : 'Create New Case'}</h3>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>Title *</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  required
                />
              </div>

              <div className="form-group">
                <label>Client ID</label>
                <input
                  type="number"
                  value={formData.client_id}
                  onChange={(e) => setFormData({ ...formData, client_id: e.target.value })}
                />
              </div>

              <div className="form-group">
                <label>Status</label>
                <select
                  value={formData.status}
                  onChange={(e) => setFormData({ ...formData, status: e.target.value })}
                >
                  <option value="open">Open</option>
                  <option value="closed">Closed</option>
                  <option value="on_hold">On Hold</option>
                </select>
              </div>

              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                  rows="4"
                />
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

        {/* Cases List */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '2rem' }}>Loading cases...</div>
        ) : cases.length === 0 ? (
          <div className="card">
            <p>No cases found. Create one to get started.</p>
          </div>
        ) : (
          <div className="card">
            <table className="table">
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Reference</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {cases.map((caseItem) => (
                  <tr key={caseItem.id}>
                    <td>{caseItem.title}</td>
                    <td>{caseItem.case_reference_number}</td>
                    <td>{caseItem.status}</td>
                    <td>{new Date(caseItem.created_at).toLocaleDateString()}</td>
                    <td style={{ display: 'flex', gap: '0.5rem' }}>
                      <Link
                        to={`/cases/${caseItem.id}`}
                        className="btn btn-primary"
                        style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                      >
                        View
                      </Link>
                      <button
                        className="btn btn-secondary"
                        onClick={() => handleEdit(caseItem)}
                        style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                      >
                        Edit
                      </button>
                      <button
                        className="btn btn-danger"
                        onClick={() => handleDelete(caseItem.id)}
                        style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default Cases;
