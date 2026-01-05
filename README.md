# Chart Analysis Agent 📊

An AI-powered cryptocurrency chart analysis agent that monitors markets on HyperLiquid, generates candlestick charts with technical indicators, and provides intelligent trading analysis using Claude AI.

## What This Agent Does

1. Fetches real-time market data from HyperLiquid
2. Generates professional candlestick charts with technical indicators
3. Analyzes charts using Claude AI
4. Provides BUY/SELL/NOTHING recommendations with confidence scores
5. Runs continuously, analyzing charts at regular intervals

## Requirements

- Python 3.8 or higher
- A HyperLiquid account (for market data)
- An Anthropic API key (for Claude AI)

## Complete Setup Instructions (For Python Beginners)

### Step 1: Check Python Installation

Open your terminal and check if Python is installed:

```bash
python3 --version
```

You should see something like `Python 3.x.x`. If not, [install Python](https://www.python.org/downloads/).

### Step 2: Clone or Download This Repository

If you have Git:
```bash
git clone <repository-url>
cd ai-agents
```

Or download the ZIP file and extract it, then navigate to the folder.

### Step 3: Create a Virtual Environment (Recommended)

This keeps your project dependencies isolated:

```bash
# Create a new virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

You should see `(venv)` at the start of your terminal prompt.

### Step 4: Install Dependencies

With your virtual environment activated, install the required packages:

```bash
pip install -r requirements.txt
```

This will download and install all necessary libraries. It may take a few minutes.

### Step 5: Set Up Environment Variables

1. Copy the example environment file:
```bash
cp .env_example .env
```

2. Open the `.env` file in a text editor and add your API keys:

```bash
# Get your Anthropic API key from: https://console.anthropic.com/
ANTHROPIC_KEY=sk-ant-your-actual-key-here

# Get your HyperLiquid private key from your HyperLiquid account
# ⚠️ IMPORTANT: This key gives access to your account - keep it safe!
HYPER_LIQUID_ETH_PRIVATE_KEY=0xyour-actual-private-key-here
```

**Where to get API keys:**
- **Anthropic API Key**: Visit [https://console.anthropic.com/](https://console.anthropic.com/) and sign up for an account. You'll get free credits to start.
- **HyperLiquid Private Key**: Export your private key from your HyperLiquid wallet settings (use with caution!)

### Step 6: Verify Installation

Check if everything is set up correctly:

```bash
python3 -c "import pandas, anthropic; print('✅ All dependencies installed!')"
```

If you see "✅ All dependencies installed!", you're ready to go!

### Step 7: Run the Agent

```bash
python src/agents/chartanalysis_agent.py
```

The agent will:
- Connect to HyperLiquid and fetch market data
- Generate charts for BTC and FARTCOIN (configurable)
- Analyze them with Claude AI
- Display results in your terminal
- Repeat every 10 minutes (configurable)

**To stop the agent:** Press `Ctrl+C`

## Configuration

### Change Symbols to Monitor

Edit `src/agents/chartanalysis_agent.py`, line 35:

```python
SYMBOLS = ["BTC", "ETH", "SOL"]  # Add any symbols available on HyperLiquid
```

### Change Timeframes

Edit line 31:

```python
TIMEFRAMES = ['15m', '1h', '4h', '1d']  # Choose from: 1m, 5m, 15m, 1h, 4h, 1d
```

### Change Check Interval

Edit line 30:

```python
CHECK_INTERVAL_MINUTES = 10  # How often to run (in minutes)
```

### Change AI Model

Edit `src/config.py`:

```python
AI_MODEL = "claude-3-haiku-20240307"     # Fast and cheap
# AI_MODEL = "claude-3-sonnet-20240229"  # Balanced (better analysis)
# AI_MODEL = "claude-3-opus-20240229"    # Most powerful (expensive)
```

## Example Output

```
╔══════════════════════════════════════════════════╗
║         Chart Data for BTC 15m - Last 5 Candles  ║
╠══════════════════════════════════════════════════╣
║ Time │ Open │ High │ Low │ Close │ Volume        ║
║ 2025-01-05 12:00 │ 42,150 │ 42,380 │ 42,120 │ 42,250 │ 1,234,567 ║
...

║ Technical Indicators:
║ SMA20: 42,145.50
║ SMA50: 41,890.25
║ SMA200: 40,125.75
║ 24h High: 42,500.00
║ 24h Low: 41,800.00
║ Volume Trend: Increasing
╚══════════════════════════════════════════════════╝

╔══════════════════════════════════════════════════╗
║    🌙 Moon Dev's Chart Analysis - BTC 15m        ║
╠══════════════════════════════════════════════════╣
║  Direction: BULLISH                              ║
║  Action: BUY                                     ║
║  Confidence: 75%                                 ║
╟──────────────────────────────────────────────────╢
║  Analysis: Price broke above SMA20 with strong   ║
║  volume, RSI trending up                         ║
╚══════════════════════════════════════════════════╝
```

## Output Files

Charts are automatically saved to:
- **Location**: `src/data/charts/`
- **Format**: PNG images
- **Naming**: `{SYMBOL}_{TIMEFRAME}_{timestamp}.png`
- **Cleanup**: Old charts are deleted at each run to save space

## Project Structure

```
ai-agents/
├── src/
│   ├── agents/
│   │   ├── base_agent.py              # Base class
│   │   └── chartanalysis_agent.py     # Main agent (THIS ONE!)
│   ├── config.py                       # AI settings
│   ├── nice_funcs_hyperliquid.py      # HyperLiquid utilities
│   └── data/
│       └── charts/                     # Generated charts (auto-created)
├── requirements.txt                     # Python packages
├── .env                                 # Your API keys (create this!)
├── .env_example                        # Template for .env
└── README.md                           # This file
```

## Troubleshooting

### "ModuleNotFoundError"
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate  # Windows

# Then reinstall dependencies
pip install -r requirements.txt
```

### "API key not found"
- Check that your `.env` file exists in the project root
- Verify the key names match exactly: `ANTHROPIC_KEY` and `HYPER_LIQUID_ETH_PRIVATE_KEY`
- Make sure there are no spaces around the `=` sign

### "Connection refused" or network errors
- Check your internet connection
- Verify your HyperLiquid private key is correct
- Try running with a VPN if blocked

### Charts not generating
- Check that the `src/data/charts/` directory exists (it's auto-created)
- Verify you have write permissions in the project directory

## Understanding the Output

- **Direction**: Overall market sentiment (BULLISH/BEARISH/SIDEWAYS)
- **Action**: What to do (BUY/SELL/NOTHING)
- **Confidence**: How confident the AI is (0-100%)
- **Analysis**: Brief reasoning for the recommendation

⚠️ **This is NOT financial advice!** The agent provides analysis for educational purposes only. Always do your own research before making trading decisions.

## Advanced Usage

### Run Once (No Loop)

Comment out the continuous loop in `src/agents/chartanalysis_agent.py`:

```python
# In the run() method, change:
# while True:
#     ...
# To:
self.run_monitoring_cycle()  # Run once and exit
```

### Add More Indicators

Edit line 40 to include more indicators:

```python
INDICATORS = ['SMA20', 'SMA50', 'SMA200', 'RSI', 'MACD', 'EMA', 'VWAP']
```

Then add the calculation logic in the `_generate_chart` method.

## Dependencies Explained

- **pandas** - Data manipulation (handling price data)
- **numpy** - Math operations
- **matplotlib** - Basic plotting
- **mplfinance** - Candlestick charts specifically
- **anthropic** - Claude AI for analysis
- **pandas-ta** - Technical indicators (SMA, RSI, etc.)
- **hyperliquid-python-sdk** - Connect to HyperLiquid
- **eth-account** - Ethereum wallet handling for HyperLiquid
- **python-dotenv** - Load environment variables from .env
- **termcolor** - Colored terminal output

## FAQ

**Q: Do I need a HyperLiquid account with funds?**
A: You need an account to get a private key, but you don't need funds just for reading market data.

**Q: How much does it cost to run?**
A: Anthropic charges per API call. With Haiku model and checking every 10 minutes, expect ~$0.50-1.00/day.

**Q: Can I analyze other exchanges?**
A: Currently only HyperLiquid is supported. Supporting other exchanges would require modifying `nice_funcs_hyperliquid.py`.

**Q: Will this execute trades automatically?**
A: No! This agent only provides analysis. It does NOT execute any trades.

**Q: Can I run this 24/7?**
A: Yes, but monitor your Anthropic API costs. Consider increasing `CHECK_INTERVAL_MINUTES`.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the `CLAUDE.md` file for development details
3. Check your API keys and internet connection

## License

Open source - free for educational and personal use.

Built with ❤️ by Moon Dev 🌙
