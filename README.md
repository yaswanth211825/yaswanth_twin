# Twin - AI Personality System

A sophisticated AI personality system that creates a digital twin with a unique personality based on Yaswanth's characteristics. The system includes a Flask web application for message review and approval workflow.

## 🎭 Features

- **AI Personality Engine**: Creates responses based on a detailed personality profile
- **Multi-language Support**: Telugu, English, Hindi, Malayalam, and Tamil
- **Message Review System**: Web interface for reviewing and approving AI responses
- **Embedding Cache**: Optimized performance with cached embeddings
- **Thread-safe Operations**: Concurrent processing capabilities

## 🏗️ Project Structure

```
Twin/
├── app.py                 # Flask web application
├── version_13.py          # AI personality engine
├── personality.yaml       # Personality configuration
├── yaswanth_finetune.jsonl # Training data
├── env/                   # Virtual environment (gitignored)
├── embeddings_cache.json  # Cached embeddings (gitignored)
└── README.md             # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd Twin
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install flask openai python-dotenv pyyaml scikit-learn requests
   ```

4. **Environment Setup**
   Create a `.env` file in the project root:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

The Flask app will start on `http://localhost:5000`

## 🎯 API Endpoints

### Web Interface
- `GET /` - Review page for pending messages
- `POST /` - Update pending message
- `POST /approve` - Approve and finalize message

### API Endpoints
- `POST /generate` - Generate AI response for review
- `GET /status` - Get current message status

## 🧠 AI Personality System

The AI personality is based on Yaswanth's characteristics:

### Personality Traits
- **Style**: Eminem-inspired characteristics with Telugu native fluency
- **Languages**: Telugu (80%), English, Hindi, Malayalam, Tamil
- **Tone**: Lyrical, heartfelt, cinematic with romantic undertones
- **Behavior**: Hopeless romantic, witty, charming, and emotionally intelligent

### Key Features
- **Multi-language responses** with cultural context
- **Mood-aware interactions** that adapt to the user's emotional state
- **Poetic and filmi dialogues** when appropriate
- **Cached embeddings** for improved performance

## 🔧 Configuration

### Personality Customization
Edit `personality.yaml` to modify:
- Speaking style and tone
- Language preferences
- Behavioral traits
- Response patterns

### Training Data
The system uses `yaswanth_finetune.jsonl` for:
- Conversation history
- Response patterns
- Contextual learning

## 🛡️ Security

- API keys are stored in `.env` file (not committed to git)
- Sensitive files are excluded via `.gitignore`
- Thread-safe operations prevent race conditions

## 📝 Usage Examples

### Generate AI Response
```bash
curl -X POST http://localhost:5000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "indu_message": "Hello, how are you?",
    "yaswanth_reply": "Nenu baagunnanu, meeru ela unnaru?"
  }'
```

### Check Status
```bash
curl http://localhost:5000/status
```

## 🎨 Web Interface

The web interface provides:
- **Review Page**: View pending messages and edit responses
- **Approval Workflow**: Approve final responses
- **Real-time Updates**: See message status changes

## 🔄 Development

### Adding New Features
1. Modify `version_13.py` for AI engine changes
2. Update `app.py` for web interface changes
3. Edit `personality.yaml` for personality adjustments

### Testing
```bash
# Test the Flask app
python app.py

# Test the AI engine
python version_13.py
```

## 📊 Performance

- **Embedding Cache**: Reduces API calls and improves response time
- **Thread Pool**: Concurrent processing for multiple requests
- **Memory Efficient**: Optimized data structures and caching

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is private and proprietary.

## 🆘 Support

For issues and questions:
1. Check the configuration files
2. Verify API key setup
3. Review the logs for error messages

---

**Note**: This system creates a digital twin with a specific personality. Use responsibly and ensure all interactions are appropriate and consensual.
