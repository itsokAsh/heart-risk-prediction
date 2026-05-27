import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

function getRiskLevel(score) {
  if (score > 50) return 'high';
  if (score > 30) return 'moderate';
  return 'low';
}

function formatDate(dateStr) {
  try {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  } catch {
    return dateStr;
  }
}

function AssessmentCard({ id, risk_score, risk_level, created_at, onDelete }) {
  const navigate = useNavigate();
  const [showConfirm, setShowConfirm] = useState(false);
  const level = risk_level || getRiskLevel(risk_score);
  const score = Math.round(risk_score ?? 0);

  const handleClick = (e) => {
    if (e.target.closest('.assessment-card-delete')) return;
    navigate(`/assess?id=${id}`);
  };

  const handleDeleteClick = (e) => {
    e.stopPropagation();
    setShowConfirm(true);
  };

  const confirmDelete = () => {
    setShowConfirm(false);
    onDelete?.(id);
  };

  return (
    <>
      <article
        className="assessment-card"
        id={`assessment-card-${id}`}
        onClick={handleClick}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => e.key === 'Enter' && handleClick(e)}
      >
        <button
          className="assessment-card-delete"
          id={`delete-assessment-${id}`}
          onClick={handleDeleteClick}
          aria-label="Delete assessment"
          type="button"
        >
          ✕
        </button>

        <div className="assessment-card-header">
          <span className="assessment-card-date">
            {formatDate(created_at)}
          </span>
          <span className={`assessment-card-badge ${level}`}>
            {level} risk
          </span>
        </div>

        <div className={`assessment-card-score ${level}`}>
          {score}%
        </div>
        <div className="assessment-card-label">
          Risk Score
        </div>

        <div className="assessment-card-bar">
          <div
            className={`assessment-card-bar-fill ${level}`}
            style={{ width: `${score}%` }}
          />
        </div>
      </article>

      {/* Confirm Delete Dialog */}
      {showConfirm && (
        <div
          className="confirm-overlay"
          onClick={() => setShowConfirm(false)}
          role="dialog"
          aria-modal="true"
        >
          <div className="confirm-dialog" onClick={(e) => e.stopPropagation()}>
            <h4 className="confirm-dialog-title">Delete Assessment?</h4>
            <p className="confirm-dialog-text">
              This action cannot be undone. The assessment and its associated reports will be permanently removed.
            </p>
            <div className="confirm-dialog-actions">
              <button
                className="btn-secondary"
                id={`cancel-delete-${id}`}
                onClick={() => setShowConfirm(false)}
                type="button"
              >
                Cancel
              </button>
              <button
                className="btn-danger"
                id={`confirm-delete-${id}`}
                onClick={confirmDelete}
                type="button"
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

export default AssessmentCard;
