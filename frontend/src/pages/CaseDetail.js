import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useParams } from 'react-router-dom';
import { casesService } from '../services/cases';
import { documentsService } from '../services/documents';
import { deadlinesService } from '../services/deadlines';
import '../App.css';

function CaseDetail({ onLogout }) {
  const navigate = useNavigate();
  const { id } = useParams();
  const [caseDetail, setCaseDetail] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [deadlines, setDeadlines] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadingFile, setUploadingFile] = useState(false);

  useEffect(() => {
    fetchCaseDetail();
  }, [id]);

  const fetchCaseDetail = async () => {
    try {
      setLoading(true);
      const [caseData, docsData, deadlineData] = await Promise.all([
        casesService.getCaseById(id),
        documentsService.getAllDocuments(0, 20, { case_id: id }),
        deadlinesService.getAllDeadlines(0, 20, { case_id: id }),
      ]);

      setCaseDetail(caseData);
      setDocuments(docsData.data || []);
      setDeadlines(deadlineData.data || []);
    } catch (err) {
      setError('Failed to fetch case details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadDocument = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    try {
      setUploadingFile(true);
      const formData = new FormData();
      formData.append('file', file);

      await documentsService.uploadDocument(id, formData);
      fetchCaseDetail();
      e.target.value = '';
    } catch (err) {
      setError('Failed to upload document');
      console.error(err);
    } finally {
      setUploadingFile(false);
    }
  };

  const handleDownloadDocument = async (docId) => {
    try {
      const blob = await documentsService.downloadDocument(docId);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `document_${docId}`;
      a.click();
    } catch (err) {
      setError('Failed to download document');
      console.error(err);
    }
  };

  const handleDeleteDocument = async (docId) => {
    if (window.confirm('Are you sure you want to delete this document?')) {
      try {
        await documentsService.deleteDocument(docId);
        fetchCaseDetail();
      } catch (err) {
        setError('Failed to delete document');
        console.error(err);
      }
    }
  };

  const handleDeleteDeadline = async (deadlineId) => {
    if (window.confirm('Are you sure you want to delete this deadline?')) {
      try {
        await deadlinesService.deleteDeadline(deadlineId);
        fetchCaseDetail();
      } catch (err) {
        setError('Failed to delete deadline');
        console.error(err);
      }
    }
  };

  const handleCloseCase = async () => {
    if (window.confirm('Are you sure you want to close this case?')) {
      try {
        await casesService.closeCase(id);
        fetchCaseDetail();
      } catch (err) {
        setError('Failed to close case');
        console.error(err);
      }
    }
  };

  const handleLogout = () => {
    onLogout();
    navigate('/login');
  };

  if (loading) {
    return (
      <div className="page">
        <nav className="nav-bar">
          <h1>Case Detail</h1>
          <ul className="nav-links">
            <li><Link to="/dashboard">Dashboard</Link></li>
            <li><Link to="/cases">Cases</Link></li>
            <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
          </ul>
        </nav>
        <div className="container" style={{ textAlign: 'center', padding: '2rem' }}>
          Loading case details...
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <nav className="nav-bar">
        <h1>Case Detail</h1>
        <ul className="nav-links">
          <li><Link to="/dashboard">Dashboard</Link></li>
          <li><Link to="/cases">Cases</Link></li>
          <li><Link to="/deadlines">Deadlines</Link></li>
          <li><button className="logout-btn" onClick={handleLogout}>Logout</button></li>
        </ul>
      </nav>

      <div className="container">
        <Link to="/cases" style={{ marginBottom: '1rem', display: 'block' }}>← Back to Cases</Link>

        {error && <div className="alert alert-error">{error}</div>}

        {caseDetail ? (
          <>
            {/* Case Info */}
            <div className="card">
              <h2>{caseDetail.title}</h2>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '1rem', marginTop: '1rem' }}>
                <div>
                  <strong>Reference:</strong>
                  <p>{caseDetail.case_reference_number}</p>
                </div>
                <div>
                  <strong>Status:</strong>
                  <p>{caseDetail.status}</p>
                </div>
                <div>
                  <strong>Created:</strong>
                  <p>{new Date(caseDetail.created_at).toLocaleDateString()}</p>
                </div>
                <div>
                  <strong>Description:</strong>
                  <p>{caseDetail.description || 'N/A'}</p>
                </div>
              </div>

              <div style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
                {caseDetail.status !== 'closed' && (
                  <button className="btn btn-danger" onClick={handleCloseCase}>
                    Close Case
                  </button>
                )}
              </div>
            </div>

            {/* Documents Section */}
            <div className="card">
              <h3>Documents</h3>
              <div style={{ marginBottom: '1rem' }}>
                <label htmlFor="file-upload">Upload Document:</label>
                <input
                  id="file-upload"
                  type="file"
                  onChange={handleUploadDocument}
                  disabled={uploadingFile}
                  style={{ display: 'block', marginTop: '0.5rem' }}
                />
                {uploadingFile && <span className="success">Uploading...</span>}
              </div>

              {documents.length === 0 ? (
                <p>No documents yet. Upload one to get started.</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Filename</th>
                      <th>Uploaded</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {documents.map((doc) => (
                      <tr key={doc.id}>
                        <td>{doc.filename}</td>
                        <td>{new Date(doc.uploaded_at).toLocaleDateString()}</td>
                        <td style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            className="btn btn-secondary"
                            onClick={() => handleDownloadDocument(doc.id)}
                            style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                          >
                            Download
                          </button>
                          <button
                            className="btn btn-danger"
                            onClick={() => handleDeleteDocument(doc.id)}
                            style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>

            {/* Deadlines Section */}
            <div className="card">
              <h3>Deadlines</h3>

              {deadlines.length === 0 ? (
                <p>No deadlines yet. Create one to get started.</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Due Date</th>
                      <th>Description</th>
                      <th>Status</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {deadlines.map((deadline) => (
                      <tr key={deadline.id}>
                        <td>{new Date(deadline.due_date).toLocaleDateString()}</td>
                        <td>{deadline.description}</td>
                        <td>{deadline.status}</td>
                        <td style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            className="btn btn-danger"
                            onClick={() => handleDeleteDeadline(deadline.id)}
                            style={{ padding: '0.5rem 0.75rem', fontSize: '14px' }}
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
            </div>
          </>
        ) : (
          <div className="card">
            <p>Case not found.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default CaseDetail;
