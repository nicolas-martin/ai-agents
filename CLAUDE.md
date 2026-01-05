# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimal Chart Analysis Agent that generates and analyzes trading charts using AI vision capabilities. The agent monitors specified cryptocurrency symbols on HyperLiquid, generates candlestick charts with technical indicators, and provides AI-powered analysis with trading recommendations.

## Quick Start

### Environment Setup
```bash
# Use existing conda environment (DO NOT create new virtual environments)
conda activate tflow

# Install dependencies
pip install -r requirements.txt
```

### Environment Variables
Create a `.env` file in the project root with:
```bash
ANTHROPIC_KEY=your_anthropic_api_key_here
OPENAI_KEY=your_openai_api_key_here
HYPER_LIQUID_ETH_PRIVATE_KEY=your_hyperliquid_private_key_here
```

### Running the Agent
```bash
# Run the chart analysis agent
python src/agents/chartanalysis_agent.py
```

## Project Structure

```
├── src/
│   ├── agents/
│   │   ├── base_agent.py              # Base class for agents
│   │   └── chartanalysis_agent.py     # Chart analysis agent (main)
│   ├── config.py                       # AI model configuration
│   ├── nice_funcs_hyperliquid.py      # HyperLiquid data fetching utilities
│   └── data/                           # Runtime data (charts, audio)
├── requirements.txt                     # Python dependencies
├── .env_example                        # Example environment variables
└── README.md                           # Project documentation
```

## Chart Analysis Agent

The Chart Analysis Agent (`chartanalysis_agent.py`) is the core of this project.

### Features
- **Multi-timeframe Analysis**: Analyzes charts on 15m, 1h, 4h, and 1d timeframes
- **Technical Indicators**: SMA20, SMA50, SMA200, RSI, MACD, Bollinger Bands
- **AI-Powered Analysis**: Uses Claude to analyze chart patterns and provide trading signals
- **Voice Announcements**: Text-to-speech announcements via OpenAI TTS
- **Automated Monitoring**: Runs continuously with configurable check intervals

### Configuration (chartanalysis_agent.py)

Key settings at the top of the file:
```python
CHECK_INTERVAL_MINUTES = 10        # How often to run analysis
TIMEFRAMES = ['15m', '1h', '4h', '1d']  # Timeframes to analyze
LOOKBACK_BARS = 15                 # Number of candles to analyze
SYMBOLS = ["BTC", "FARTCOIN"]      # Symbols to monitor
```

AI Settings (can override config.py):
```python
AI_MODEL = False              # Set to model name to override config.AI_MODEL
AI_TEMPERATURE = 0            # Set > 0 to override config.AI_TEMPERATURE
AI_MAX_TOKENS = 0             # Set > 0 to override config.AI_MAX_TOKENS
```

### How It Works

1. **Data Collection**: Fetches OHLCV data from HyperLiquid via `nice_funcs_hyperliquid.py`
2. **Chart Generation**: Creates candlestick charts with technical indicators using mplfinance
3. **AI Analysis**: Claude analyzes the chart data and provides:
   - Trading direction (BULLISH/BEARISH/SIDEWAYS)
   - Action recommendation (BUY/SELL/NOTHING)
   - Confidence level (0-100%)
   - Brief reasoning
4. **Voice Announcement**: Converts analysis to speech via OpenAI TTS
5. **Continuous Monitoring**: Repeats at configured intervals

### Output

- **Charts**: Saved to `src/data/charts/` as PNG files
- **Audio**: Saved to `src/audio/` as MP3 files
- **Console**: Real-time analysis printed with formatted boxes

## Dependencies

### Core Libraries
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical operations
- **matplotlib**: Chart plotting foundation
- **mplfinance**: Candlestick chart generation

### AI/LLM
- **anthropic**: Claude API for chart analysis
- **openai**: OpenAI API for text-to-speech

### Technical Analysis
- **pandas-ta**: Technical indicators (SMA, RSI, MACD, Bollinger Bands)

### HyperLiquid Integration
- **eth-account**: Ethereum account management for HyperLiquid
- **hyperliquid-python-sdk**: HyperLiquid API client

### Utilities
- **python-dotenv**: Environment variable management
- **termcolor**: Colored terminal output

## HyperLiquid Integration

The agent uses HyperLiquid for real-time market data. Key functions in `nice_funcs_hyperliquid.py`:

- `get_data(symbol, timeframe, bars, add_indicators)`: Fetches OHLCV data with optional technical indicators
- `get_position(symbol, account)`: Gets current position information
- `market_buy(symbol, usd_size, account)`: Places market buy order
- `market_sell(symbol, usd_size, account)`: Places market sell order
- `kill_switch(symbol, account)`: Emergency position close

## Development Guidelines

### Code Style
- Keep files under 800 lines
- Use descriptive variable names
- Add comments for complex logic
- Use colored terminal output for better UX

### Making Changes
- **Adding Symbols**: Edit `SYMBOLS` list in `chartanalysis_agent.py`
- **Changing Timeframes**: Edit `TIMEFRAMES` list in `chartanalysis_agent.py`
- **Adjusting AI Model**: Edit `AI_MODEL` in `src/config.py` or override in agent file
- **Modifying Indicators**: Edit `INDICATORS` list in `chartanalysis_agent.py`

### Testing
```bash
# Run the agent once (it will loop continuously)
python src/agents/chartanalysis_agent.py

# Press Ctrl+C to stop gracefully
```

## Troubleshooting

### Common Issues

1. **API Key Errors**: Ensure `.env` file exists with valid API keys
2. **Module Not Found**: Run `pip install -r requirements.txt`
3. **HyperLiquid Connection**: Check `HYPER_LIQUID_ETH_PRIVATE_KEY` is valid
4. **Audio Not Playing**: Check `afplay` command works on your system (macOS only)

### Debug Mode

To see detailed chart data, check the console output which shows:
- Last 5 candles with OHLCV data
- Technical indicator values
- AI analysis reasoning
- Confidence scores

## Architecture Notes

### Base Agent Pattern
All agents inherit from `BaseAgent` class which provides:
- Agent type identification
- Start time tracking
- Optional exchange manager integration

### Data Flow
```
HyperLiquid API → nice_funcs_hyperliquid.py → chartanalysis_agent.py →
→ mplfinance (chart) → Claude (analysis) → OpenAI TTS (voice) → Console/Files
```

### File Organization
- Agent outputs are stored in `src/data/charts/` and `src/audio/`
- Old charts are cleaned up on each run to save space
- All paths use `pathlib.Path` for cross-platform compatibility

## Important Notes

- This is an **educational project** - not financial advice
- The agent provides analysis but does not execute trades automatically
- Always verify AI analysis against your own research
- HyperLiquid private key gives access to your account - keep it secure
- Audio announcements require macOS `afplay` command (may need modification for other OS)

## Future Enhancements

Potential improvements you could make:
- Add more technical indicators (Volume Profile, Ichimoku, etc.)
- Implement trade execution based on signals
- Add risk management rules
- Create a web dashboard for visualization
- Support additional exchanges
- Add backtesting capabilities
