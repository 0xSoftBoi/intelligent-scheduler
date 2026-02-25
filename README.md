# Intelligent Scheduler System

AI-powered scheduling system that optimizes meetings based on energy patterns, productivity analytics, and intelligent task batching.

## Features

- **Energy Pattern Analysis**: Tracks and analyzes your energy levels throughout the day
- **Meeting Optimization Engine**: Schedules meetings based on energy levels, meeting types, and productivity patterns
- **Communication Batching**: Groups similar tasks to minimize context switching
- **No-Meeting Day Enforcement**: Protects dedicated focus days
- **Calendar Integration**: Seamless integration with Google Calendar and Outlook
- **Real-time Adjustments**: Webhook handlers for dynamic schedule optimization
- **Predictive Analytics**: Machine learning models for productivity prediction

## Architecture

```
intelligent-scheduler/
├── src/
│   ├── energy_analysis/        # Energy pattern analysis algorithms
│   ├── optimization/            # Meeting optimization engine
│   ├── batching/                # Communication batching system
│   ├── enforcement/             # No-meeting day enforcement
│   ├── integrations/            # Calendar integrations (Google, Outlook)
│   ├── webhooks/                # Webhook handlers
│   └── ml_models/               # Machine learning models
├── tests/                       # Unit and integration tests
├── docs/                        # API documentation
├── config/                      # Configuration files
└── requirements.txt             # Python dependencies
```

## Quick Start

### Prerequisites

- Python 3.9+
- pip or conda
- Virtual environment (recommended)
- API credentials for Google Calendar and/or Outlook

### Installation

1. Clone the repository:
```bash
git clone https://github.com/0xSoftBoi/intelligent-scheduler.git
cd intelligent-scheduler
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up configuration:
```bash
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API credentials
```

5. Initialize the database:
```bash
python scripts/init_db.py
```

6. Run the application:
```bash
python src/main.py
```

## Configuration

Edit `config/config.yaml` to configure:

- Calendar integration credentials
- Webhook endpoints
- ML model parameters
- Energy analysis settings
- Meeting optimization preferences

## API Documentation

Detailed API documentation is available in the [docs/API.md](docs/API.md) file.

### Quick API Overview

**Base URL**: `http://localhost:8000/api/v1`

**Key Endpoints**:
- `POST /schedule/optimize` - Optimize meeting schedule
- `GET /energy/patterns` - Get energy patterns
- `POST /meetings/batch` - Batch similar meetings
- `PUT /settings/no-meeting-days` - Configure no-meeting days
- `POST /webhooks/calendar` - Calendar webhook receiver

## Usage Examples

See [docs/EXAMPLES.md](docs/EXAMPLES.md) for detailed usage examples.

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test suite
pytest tests/test_energy_analysis.py
```

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Roadmap

- [ ] Add Slack integration
- [ ] Implement team-wide optimization
- [ ] Add mobile app support
- [ ] Enhanced ML models with deep learning
- [ ] Multi-timezone optimization

## Support

For issues and questions, please use the [GitHub Issues](https://github.com/0xSoftBoi/intelligent-scheduler/issues) page.
