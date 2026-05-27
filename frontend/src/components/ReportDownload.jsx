import { useState, useRef } from 'react';
import api from '../api/client';

const LANGUAGES = [
  { code: 'en', label: '🇬🇧 English' },
  { code: 'es', label: '🇪🇸 Spanish' },
  { code: 'fr', label: '🇫🇷 French' },
  { code: 'de', label: '🇩🇪 German' },
  { code: 'it', label: '🇮🇹 Italian' },
  { code: 'pt', label: '🇵🇹 Portuguese' },
  { code: 'hi', label: '🇮🇳 Hindi' },
  { code: 'zh', label: '🇨🇳 Chinese' }
];

function ReportDownload({ assessmentId }) {
  const [pdfLoading, setPdfLoading] = useState(false);
  const [audioLoading, setAudioLoading] = useState(false);
  const [language, setLanguage] = useState('en');
  const [audioUrl, setAudioUrl] = useState(null);
  const [error, setError] = useState('');
  const audioRef = useRef(null);

  const handleDownloadPdf = async () => {
    setPdfLoading(true);
    setError('');
    try {
      const res = await api.get(`/reports/${assessmentId}/pdf`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'application/pdf' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `heartguard-report-${assessmentId}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to download PDF report');
    } finally {
      setPdfLoading(false);
    }
  };

  const handleGenerateAudio = async () => {
    setAudioLoading(true);
    setError('');
    try {
      const res = await api.get(`/reports/${assessmentId}/audio`, {
        params: { lang: language },
        responseType: 'blob'
      });
      if (audioUrl) {
        window.URL.revokeObjectURL(audioUrl);
      }
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'audio/mpeg' }));
      setAudioUrl(url);
      if (audioRef.current) {
        audioRef.current.load();
        audioRef.current.play().catch(() => {});
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to generate audio report');
    } finally {
      setAudioLoading(false);
    }
  };

  const handleDownloadAudio = () => {
    if (!audioUrl) return;
    const link = document.createElement('a');
    link.href = audioUrl;
    link.setAttribute('download', `heartguard-audio-${language}-${assessmentId}.mp3`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  if (!assessmentId) return null;

  return (
    <section className="report-section" aria-label="Report downloads">
      <h3 className="report-section-title">
        📄 Download Your Report
      </h3>

      {error && <div className="error-banner">{error}</div>}

      <div className="report-actions">
        {/* PDF Download */}
        <div className="report-action-group">
          <label>PDF Report</label>
          <button
            className="btn-primary"
            id="download-pdf-btn"
            onClick={handleDownloadPdf}
            disabled={pdfLoading}
            type="button"
          >
            {pdfLoading ? (
              <>
                <span className="spinner" />
                Generating…
              </>
            ) : (
              '📥 Download PDF'
            )}
          </button>
        </div>

        {/* Language Selector + Audio */}
        <div className="report-action-group">
          <label htmlFor="language-select">Audio Language</label>
          <select
            id="language-select"
            className="language-select"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            {LANGUAGES.map((lang) => (
              <option key={lang.code} value={lang.code}>
                {lang.label}
              </option>
            ))}
          </select>
        </div>

        <div className="report-action-group">
          <label>Audio Report</label>
          <button
            className="btn-secondary"
            id="generate-audio-btn"
            onClick={handleGenerateAudio}
            disabled={audioLoading}
            type="button"
          >
            {audioLoading ? (
              <>
                <span className="spinner" />
                Generating…
              </>
            ) : (
              '🔊 Generate Audio'
            )}
          </button>
        </div>
      </div>

      {/* Audio Player */}
      {audioUrl && (
        <div className="audio-player-wrapper">
          <audio ref={audioRef} controls id="audio-player">
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support audio playback.
          </audio>
          <button
            className="btn-secondary"
            id="download-audio-btn"
            onClick={handleDownloadAudio}
            type="button"
            style={{ marginTop: '10px' }}
          >
            💾 Download Audio
          </button>
        </div>
      )}
    </section>
  );
}

export default ReportDownload;
