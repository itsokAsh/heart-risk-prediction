# HeartGuard

Full-stack heart disease risk assessment with a FastAPI backend, PostgreSQL, and a React frontend (in progress). The backend exposes prediction, report generation, and authentication APIs.

## Features

- Heart disease risk prediction using XGBoost
- Input validation for health metrics
- Personalized health recommendations
- PDF report generation
- Multi-language audio reports
- JWT authentication and assessment history

## Local Development (Docker)

### Prerequisites
- Docker Desktop

### Setup
1. Copy env template:
```bash
cp .env.example .env
```

2. Start services:
```bash
docker compose up --build
```

### URLs
- Backend API: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`

### Environment Notes
- `.env` is used by the backend container. For Docker Compose, `DATABASE_URL` should use `postgres` as the hostname.
- `JWT_SECRET` should be a strong 32+ byte value in production.
- Rotate `JWT_SECRET` carefully: changing it will invalidate all existing tokens. Plan a maintenance window or support dual secrets if you need seamless rotation.

## API Quick Start

1. Register a user: `POST /api/auth/register`
2. Login to get a token: `POST /api/auth/login`
3. Send prediction payload: `POST /api/predict`
4. Download reports: `GET /api/reports/{assessment_id}/pdf`, `GET /api/reports/{assessment_id}/audio`

## API Reference (Backend)

### Auth
- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/auth/me`

### Prediction
- `POST /api/predict`

### Assessments
- `GET /api/assessments`
- `GET /api/assessments/{id}`
- `DELETE /api/assessments/{id}`

### Reports
- `GET /api/reports/{assessment_id}/pdf`
- `GET /api/reports/{assessment_id}/audio?lang=en`

## Project Structure

- `backend/`: FastAPI app, ML logic, migrations, tests
- `frontend/`: React app (in progress)
- `docker-compose.yml`: Local container orchestration
- `.env.example`: Environment template

## Dependencies

- Backend dependencies are in [backend/requirements.txt](backend/requirements.txt)

## Notes

- All health recommendations are general guidelines. Always consult with healthcare professionals for medical advice.
- The risk prediction model is based on statistical analysis and should not be used as the sole basis for medical decisions.

## Input Features

- **Age**: Age in years
- **Sex**: Male/Female
- **Chest Pain Type**: Type of chest pain experienced
- **Blood Pressure**: Resting blood pressure (mm Hg)
- **Cholesterol**: Serum cholesterol level (mg/dL)
- **Blood Sugar**: Fasting blood sugar > 120 mg/dL
- **ECG Results**: Resting electrocardiographic results
- **Max Heart Rate**: Maximum heart rate achieved
- **Exercise Angina**: Exercise-induced angina
- **ST Depression**: ST depression induced by exercise
- **ST Slope**: Slope of peak exercise ST segment
- **Number of Vessels**: Number of major vessels colored by fluoroscopy
- **Thalassemia**: Type of thalassemia

## Model Details

The application uses an XGBoost classifier trained on the UCI Heart Disease dataset. The model is optimized for both accuracy and interpretability, with the following characteristics:

- Cross-validation during training
- Feature standardization
- Hyperparameter optimization
- Regular retraining capability

## Security and Privacy

- No personal health data is stored beyond assessments tied to accounts
- PDF and audio reports are generated on demand

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see [License.txt](License.txt) for details.

## Disclaimer

This application is for educational purposes only and should not be used as a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition. 