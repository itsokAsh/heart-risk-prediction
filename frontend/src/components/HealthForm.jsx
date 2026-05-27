import { useState } from 'react';

const STEPS = [
  { key: 'personal', label: 'Personal Info' },
  { key: 'medical', label: 'Medical Data' },
  { key: 'exercise', label: 'Exercise Data' }
];

const INITIAL_VALUES = {
  age: '',
  sex: '',
  cp: '',
  trestbps: '',
  chol: '',
  fbs: '',
  restecg: '',
  ca: '',
  thal: '',
  thalach: '',
  exang: '',
  oldpeak: '',
  slope: ''
};

function HealthForm({ onSubmit, isSubmitting }) {
  const [step, setStep] = useState(0);
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState({});

  const handleChange = (field, value) => {
    setValues((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors((prev) => {
        const next = { ...prev };
        delete next[field];
        return next;
      });
    }
  };

  const validateStep = (stepIndex) => {
    const newErrors = {};
    const fields = getStepFields(stepIndex);

    fields.forEach(({ key, label, min, max, type }) => {
      const val = values[key];
      if (val === '' || val === undefined || val === null) {
        newErrors[key] = `${label} is required`;
        return;
      }
      if (type === 'number') {
        const num = Number(val);
        if (isNaN(num)) {
          newErrors[key] = `${label} must be a number`;
        } else if (min !== undefined && num < min) {
          newErrors[key] = `Minimum value is ${min}`;
        } else if (max !== undefined && num > max) {
          newErrors[key] = `Maximum value is ${max}`;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleNext = () => {
    if (validateStep(step)) {
      setStep((prev) => Math.min(prev + 1, 2));
    }
  };

  const handleBack = () => {
    setStep((prev) => Math.max(prev - 1, 0));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (validateStep(step)) {
      const numericData = {};
      Object.keys(values).forEach((key) => {
        numericData[key] = Number(values[key]);
      });
      onSubmit(numericData);
    }
  };

  const getStepFields = (stepIndex) => {
    switch (stepIndex) {
      case 0:
        return [
          { key: 'age', label: 'Age', type: 'number', min: 1, max: 120, help: 'Your age in years' },
          { key: 'sex', label: 'Sex', type: 'select', options: [
            { value: 1, label: 'Male' },
            { value: 0, label: 'Female' }
          ], help: 'Biological sex' },
          { key: 'cp', label: 'Chest Pain Type', type: 'select', options: [
            { value: 0, label: 'Typical Angina' },
            { value: 1, label: 'Atypical Angina' },
            { value: 2, label: 'Non-anginal Pain' },
            { value: 3, label: 'Asymptomatic' }
          ], help: 'Type of chest pain experienced' }
        ];
      case 1:
        return [
          { key: 'trestbps', label: 'Resting Blood Pressure', type: 'number', min: 50, max: 250, help: 'Resting blood pressure in mmHg (on admission)' },
          { key: 'chol', label: 'Serum Cholesterol', type: 'number', min: 100, max: 600, help: 'Serum cholesterol in mg/dl' },
          { key: 'fbs', label: 'Fasting Blood Sugar > 120', type: 'select', options: [
            { value: 0, label: 'No' },
            { value: 1, label: 'Yes' }
          ], help: 'Fasting blood sugar > 120 mg/dl' },
          { key: 'restecg', label: 'Resting ECG', type: 'select', options: [
            { value: 0, label: 'Normal' },
            { value: 1, label: 'ST-T Wave Abnormality' },
            { value: 2, label: 'Left Ventricular Hypertrophy' }
          ], help: 'Resting electrocardiographic results' },
          { key: 'ca', label: 'Number of Major Vessels', type: 'number', min: 0, max: 4, help: 'Number of major vessels colored by fluoroscopy (0-4)' },
          { key: 'thal', label: 'Thalassemia', type: 'select', options: [
            { value: 1, label: 'Normal' },
            { value: 2, label: 'Fixed Defect' },
            { value: 3, label: 'Reversible Defect' }
          ], help: 'Thalassemia blood disorder type' }
        ];
      case 2:
        return [
          { key: 'thalach', label: 'Max Heart Rate Achieved', type: 'number', min: 50, max: 250, help: 'Maximum heart rate achieved during exercise' },
          { key: 'exang', label: 'Exercise Induced Angina', type: 'select', options: [
            { value: 0, label: 'No' },
            { value: 1, label: 'Yes' }
          ], help: 'Exercise induced angina' },
          { key: 'oldpeak', label: 'ST Depression (Oldpeak)', type: 'number', min: 0, max: 10, help: 'ST depression induced by exercise relative to rest' },
          { key: 'slope', label: 'ST Slope', type: 'select', options: [
            { value: 0, label: 'Upsloping' },
            { value: 1, label: 'Flat' },
            { value: 2, label: 'Downsloping' }
          ], help: 'Slope of the peak exercise ST segment' }
        ];
      default:
        return [];
    }
  };

  const fields = getStepFields(step);

  return (
    <form className="health-form" onSubmit={handleSubmit} noValidate>
      {/* Step Indicator */}
      <div className="form-step-indicator" role="progressbar" aria-valuenow={step + 1} aria-valuemin={1} aria-valuemax={3}>
        {STEPS.map((s, i) => (
          <div className="step-item" key={s.key}>
            {i > 0 && (
              <div className={`step-connector ${i <= step ? 'completed' : ''}`} />
            )}
            <div className="step-wrapper">
              <div
                className={`step-circle ${i === step ? 'active' : ''} ${i < step ? 'completed' : ''}`}
              >
                {i < step ? '✓' : i + 1}
              </div>
              <span className={`step-label ${i === step ? 'active' : ''} ${i < step ? 'completed' : ''}`}>
                {s.label}
              </span>
            </div>
          </div>
        ))}
      </div>

      {/* Step Content */}
      <div className="form-step-content" key={step}>
        <h3 className="form-step-title">{STEPS[step].label}</h3>
        <div className="form-grid">
          {fields.map((field) => (
            <div className="form-group" key={field.key}>
              <label className="form-label" htmlFor={`field-${field.key}`}>
                {field.label}
                <span className="form-label-tooltip" title={field.help}>?</span>
              </label>

              {field.type === 'select' ? (
                <select
                  id={`field-${field.key}`}
                  className={`input-field ${errors[field.key] ? 'input-error' : ''}`}
                  value={values[field.key]}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                >
                  <option value="" disabled>Select…</option>
                  {field.options.map((opt) => (
                    <option key={opt.value} value={opt.value}>{opt.label}</option>
                  ))}
                </select>
              ) : (
                <input
                  id={`field-${field.key}`}
                  type="number"
                  className={`input-field ${errors[field.key] ? 'input-error' : ''}`}
                  value={values[field.key]}
                  onChange={(e) => handleChange(field.key, e.target.value)}
                  placeholder={field.min !== undefined ? `${field.min} – ${field.max}` : ''}
                  min={field.min}
                  max={field.max}
                  step={field.key === 'oldpeak' ? '0.1' : '1'}
                />
              )}

              <span className="form-validation-msg">
                {errors[field.key] || ''}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="form-actions">
        {step > 0 ? (
          <button
            type="button"
            className="btn-secondary"
            id="form-back-btn"
            onClick={handleBack}
          >
            ← Back
          </button>
        ) : (
          <div />
        )}

        {step < 2 ? (
          <button
            type="button"
            className="btn-primary"
            id="form-next-btn"
            onClick={handleNext}
          >
            Next →
          </button>
        ) : (
          <button
            type="submit"
            className="btn-primary"
            id="form-submit-btn"
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <>
                <span className="spinner" />
                Analyzing…
              </>
            ) : (
              '🔬 Analyze Risk'
            )}
          </button>
        )}
      </div>
    </form>
  );
}

export default HealthForm;
