"""
Chuck the Chart Agent generates and analyzes trading charts using AI vision capabilities.
"""

import os
import pandas as pd
import pandas_ta as ta
import mplfinance as mpf
from pathlib import Path
import time
from dotenv import load_dotenv
from src import nice_funcs_hyperliquid as hl
from src.models.claude_model import ClaudeModel
from src.agents.base_agent import BaseAgent
import traceback
import re
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from typing import cast, Dict, Optional

# Rich console for pretty output
console = Console()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Configuration
CHECK_INTERVAL_MINUTES = 10  # 3 hours and 53 minutes
TIMEFRAMES = ['15m']#['15m', '1h', '4h', '1d']  # Multiple timeframes to analyze
LOOKBACK_BARS = 250  # Number of candles to analyze (250 for valid SMA200)

# Trading Pairs to Monitor
SYMBOLS = ["BTC", "SOL"]  # Add or modify symbols here

# Chart Settings
CHART_STYLE = 'charles'  # mplfinance style
VOLUME_PANEL = True  # Show volume panel
INDICATORS = ['SMA20', 'SMA50', 'SMA200', 'RSI']  # Technical indicators to display

# AI Settings - Override config.py if set
from src import config

# Only set these if you want to override config.py settings
AI_MODEL = False  # Set to model name to override config.AI_MODEL
AI_TEMPERATURE = 0  # Set > 0 to override config.AI_TEMPERATURE
AI_MAX_TOKENS = 0  # Set > 0 to override config.AI_MAX_TOKENS

# AI Analysis Prompt
CHART_ANALYSIS_PROMPT = """You must respond in exactly 3 lines:
Line 1: Only write BUY, SELL, or NOTHING
Line 2: One short reason why
Line 3: Only write "Confidence: X%" where X is 0-100

Analyze the chart data for {symbol} {timeframe}:

{chart_data}

Remember:
- Look for confluence between multiple indicators
- Volume should confirm price action
- Consider the timeframe context
"""

class ChartAnalysisAgent(BaseAgent):
    """Chuck the Chart Analysis Agent"""
    
    def __init__(self):
        """Initialize Chuck the Chart Agent"""
        super().__init__('chartanalysis')

        # Set up directories
        self.charts_dir = PROJECT_ROOT / "src" / "data" / "charts"
        self.charts_dir.mkdir(parents=True, exist_ok=True)

        # Store analysis results for summary table
        self.cycle_results = []

        # Load environment variables
        load_dotenv()

        # Validate HyperLiquid key
        hyperliquid_key = os.getenv("HYPER_LIQUID_ETH_PRIVATE_KEY")
        if not hyperliquid_key or hyperliquid_key == "your_hyperliquid_eth_private_key_here":
            raise ValueError(
                "🚨 HYPER_LIQUID_ETH_PRIVATE_KEY not configured!\n"
                "   Please edit your .env file and add your HyperLiquid private key.\n"
                "   Get one from your HyperLiquid account settings."
            )

        # Set AI parameters - use config values unless overridden
        self.ai_model = AI_MODEL if AI_MODEL else config.AI_MODEL
        self.ai_temperature = AI_TEMPERATURE if AI_TEMPERATURE > 0 else config.AI_TEMPERATURE
        self.ai_max_tokens = AI_MAX_TOKENS if AI_MAX_TOKENS > 0 else config.AI_MAX_TOKENS

        # Initialize Claude model
        anthropic_key = os.getenv("ANTHROPIC_KEY")
        if not anthropic_key or anthropic_key == "your_anthropic_api_key_here":
            raise ValueError(
                "🚨 ANTHROPIC_KEY not configured!\n"
                "   Please edit your .env file and add your Anthropic API key.\n"
                "   Get one at: https://console.anthropic.com/"
            )
        self.model = ClaudeModel(api_key=anthropic_key, model_name=self.ai_model)
        
        print("📊 Chuck the Chart Agent initialized!")
        print(f"🤖 Using AI Model: {self.ai_model}")
        if AI_MODEL or AI_TEMPERATURE > 0 or AI_MAX_TOKENS > 0:
            print("⚠️ Note: Using some override settings instead of config.py defaults")
        print(f"🎯 Analyzing {len(TIMEFRAMES)} timeframes: {', '.join(TIMEFRAMES)}")
        print(f"📈 Using indicators: {', '.join(INDICATORS)}")
        
    def _generate_chart(self, symbol, timeframe, data):
        """Generate a chart using mplfinance"""
        try:
            # Prepare data
            df = data.copy()
            if 'timestamp' in df.columns:
                df.index = pd.to_datetime(df['timestamp'], utc=True)
            else:
                df.index = pd.to_datetime(df.index, utc=True)
            df.sort_index(inplace=True)
            if df.index.tz is not None:
                df.index = df.index.tz_convert('UTC').tz_localize(None)
            df.index.name = 'Date'
            
            # Check if data is valid
            if df.empty:
                print("No data available for chart generation")
                return None
                
            # Indicators are already calculated before calling this helper
            # Create addplot for indicators
            ap = []
            colors = ['blue', 'orange', 'purple']
            panel_ratios = [8]  # Base price chart height
            if VOLUME_PANEL:
                panel_ratios.append(3)  # Dedicated volume height
            for i, sma in enumerate(['SMA20', 'SMA50', 'SMA200']):
                if sma in INDICATORS and sma in df.columns and not df[sma].isna().all():
                    ap.append(mpf.make_addplot(df[sma], color=colors[i]))

            if 'RSI' in INDICATORS and 'RSI' in df.columns and not df['RSI'].isna().all():
                # Plot RSI on its own lower panel (separate from volume)
                rsi_panel_index = len(panel_ratios)
                panel_ratios.append(2)
                ap.append(
                    mpf.make_addplot(
                        df['RSI'],
                        panel=rsi_panel_index,
                        color='magenta',
                        ylabel='RSI (14)',
                        ylim=(0, 100)
                    )
                )
            
            # Save chart
            filename = f"{symbol}_{timeframe}_{int(time.time())}.png"
            chart_path = self.charts_dir / filename

            # Create the chart - only add addplot if we have indicators
            plot_kwargs = {
                'type': 'candle',
                'style': CHART_STYLE,
                'volume': VOLUME_PANEL,
                'title': f"\n{symbol} {timeframe} Chart Analysis",
                'savefig': chart_path,
                'datetime_format': '%Y-%m-%d %H:%M',
                'xrotation': 45
            }

            if ap:  # Only add addplot if there are indicators
                plot_kwargs['addplot'] = ap
            if len(panel_ratios) > 1:
                plot_kwargs['panel_ratios'] = tuple(panel_ratios)

            mpf.plot(df, **plot_kwargs)
            
            return chart_path
            
        except Exception as e:
            print(f"❌ Error generating chart: {str(e)}")
            traceback.print_exc()
            return None

    def _calculate_indicator(self, data: pd.DataFrame, indicator: str) -> None:
        """Ensure a specific indicator column exists on the dataframe"""
        indicator = indicator.upper()
        close_series = cast(pd.Series, data['close'])

        if indicator.startswith('SMA') and indicator[3:].isdigit():
            period = int(indicator[3:])
            if indicator not in data.columns:
                data[indicator] = close_series.rolling(window=period).mean()
            return

        if indicator.startswith('EMA') and indicator[3:].isdigit():
            period = int(indicator[3:])
            if indicator not in data.columns:
                data[indicator] = ta.ema(close_series, length=period).rename(indicator)
            return

        if indicator == 'RSI':
            if 'RSI' not in data.columns:
                data['RSI'] = ta.rsi(close_series, length=14).rename('RSI')
            return

    def _format_indicator_value(self, data: pd.DataFrame, indicator: str) -> Optional[str]:
        """Return a friendly string for the latest value of the indicator"""
        indicator = indicator.upper()

        if indicator in data.columns and (indicator.startswith('SMA') or indicator.startswith('EMA') or indicator == 'VWAP'):
            latest = data[indicator].iloc[-1]
            return f"{latest:.2f}" if not pd.isna(latest) else "Not enough data"

        if indicator == 'RSI' and 'RSI' in data.columns:
            latest = data['RSI'].iloc[-1]
            return f"{latest:.2f}" if not pd.isna(latest) else "Not enough data"

        return None

    def _get_indicator_snapshot(self, data: pd.DataFrame) -> Dict[str, str]:
        """Compute and format all configured indicators"""
        snapshot: Dict[str, str] = {}
        for indicator in INDICATORS:
            normalized = indicator.upper()
            self._calculate_indicator(data, normalized)
            formatted_value = self._format_indicator_value(data, normalized)
            if formatted_value:
                snapshot[indicator] = formatted_value
        return snapshot
            
    def _analyze_chart(self, symbol, timeframe, data, indicators_snapshot: Dict[str, str]):
        """Analyze chart data using Claude"""
        try:
            # Format the chart data
            indicator_lines = "\n".join(f"- {name}: {value}" for name, value in indicators_snapshot.items()) or "No indicators available"
            chart_data = (
                f"Recent price action (last 5 candles):\n{data.tail(5).to_string()}\n\n"
                f"Technical Indicators:\n"
                f"{indicator_lines}\n\n"
                f"Current price: {data['close'].iloc[-1]:.2f}\n"
                f"24h High: {data['high'].max():.2f}\n"
                f"24h Low: {data['low'].min():.2f}\n"
                f"Volume trend: {'Increasing' if data['volume'].iloc[-1] > data['volume'].mean() else 'Decreasing'}"
            )
            
            # Prepare the context
            context = CHART_ANALYSIS_PROMPT.format(
                symbol=symbol,
                timeframe=timeframe,
                chart_data=chart_data
            )
            
            print(f"\n🤖 Analyzing {symbol} with AI...")

            # Get AI analysis using ClaudeModel
            response = self.model.generate_response(
                system_prompt="You are a technical chart analyst. Analyze the given chart data and provide trading signals.",
                user_content=context,
                max_tokens=self.ai_max_tokens,
                temperature=self.ai_temperature
            )

            if not response or not response.content:
                print("❌ No response from AI")
                return None

            # Get the content (already cleaned by ClaudeModel)
            content = response.content
            
            # Split into lines and clean each line
            lines = [line.strip() for line in content.split('\n') if line.strip()]
            
            if not lines:
                print("❌ Empty response from AI")
                return None
            
            # First line should be the action
            action = lines[0].strip().upper()
            if action not in ['BUY', 'SELL', 'NOTHING']:
                print(f"⚠️ Invalid action: {action}")
                return None
            
            # Rest is analysis
            analysis = lines[1] if len(lines) > 1 else ""
            
            # Extract confidence from third line
            confidence = 50  # Default confidence
            if len(lines) > 2:
                try:
                    matches = re.findall(r'(\d+)%', lines[2])
                    if matches:
                        confidence = int(matches[0])
                except:
                    print("⚠️ Could not parse confidence, using default")
            
            # Determine direction based on action
            if action == 'BUY':
                direction = 'BULLISH'
            elif action == 'SELL':
                direction = 'BEARISH'
            else:
                direction = 'SIDEWAYS'
            
            return {
                'direction': direction,
                'analysis': analysis,
                'action': action,
                'confidence': confidence
            }
            
        except Exception as e:
            print(f"❌ Error in chart analysis: {str(e)}")
            traceback.print_exc()
            return None

    def analyze_symbol(self, symbol, timeframe):
        """Analyze a single symbol on a specific timeframe"""
        try:
            # Get market data
            data = hl.get_data(
                symbol=symbol,
                timeframe=timeframe,
                bars=LOOKBACK_BARS,
                add_indicators=True
            )
            
            if data is None or data.empty:
                print(f"❌ No data available for {symbol} {timeframe}")
                return

            indicators_snapshot = self._get_indicator_snapshot(data)
            
            chart_path = self._generate_chart(symbol, timeframe, data)
            if chart_path:
                print(f"📈 Chart saved to: {chart_path}")
            
            # Technical indicators table
            volume_trend = "Increasing" if data['volume'].iloc[-1] > data['volume'].mean() else "Decreasing"

            indicators_table = Table(title="Technical Indicators", expand=False)
            indicators_table.add_column("Indicator", style="cyan")
            indicators_table.add_column("Value", justify="right")

            if indicators_snapshot:
                for name, value in indicators_snapshot.items():
                    indicators_table.add_row(name, value)
            else:
                indicators_table.add_row("Indicators", "Not available")

            indicators_table.add_row("24h High", f"{data['high'].max():.2f}")
            indicators_table.add_row("24h Low", f"{data['low'].min():.2f}")
            indicators_table.add_row("Volume Trend", volume_trend)

            console.print(indicators_table)

            # Analyze with AI
            console.print(f"\n[bold]Analyzing {symbol} {timeframe}...[/bold]")
            analysis = self._analyze_chart(symbol, timeframe, data, indicators_snapshot)

            if analysis and all(k in analysis for k in ['direction', 'analysis', 'action', 'confidence']):
                # Color-code direction and action
                direction = analysis['direction']
                action = analysis['action']
                confidence = analysis['confidence']

                dir_color = "green" if direction == "BULLISH" else "red" if direction == "BEARISH" else "yellow"
                action_color = "green" if action == "BUY" else "red" if action == "SELL" else "yellow"

                analysis_text = f"""[bold {dir_color}]Direction:[/bold {dir_color}] {direction}
[bold {action_color}]Action:[/bold {action_color}] {action}
[bold]Confidence:[/bold] {confidence}%

[dim]{analysis['analysis']}[/dim]"""

                console.print(Panel(analysis_text, title=f"Chart Analysis - {symbol} {timeframe}", border_style=dir_color, expand=False))

                # Store result for summary table
                self.cycle_results.append({
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'direction': direction,
                    'action': action,
                    'confidence': confidence,
                    'analysis': analysis['analysis']
                })
            else:
                console.print("[red]Invalid analysis result[/red]")
            
        except Exception as e:
            print(f"❌ Error analyzing {symbol} {timeframe}: {str(e)}")
            traceback.print_exc()
            
    def _cleanup_old_charts(self):
        """Remove all existing charts from the charts directory"""
        try:
            for chart in self.charts_dir.glob("*.png"):
                chart.unlink()
            print("🧹 Cleaned up old charts")
        except Exception as e:
            print(f"⚠️ Error cleaning up charts: {str(e)}")

    def _print_summary_table(self):
        """Print a summary table of all analysis results"""
        if not self.cycle_results:
            return

        summary_table = Table(title="Analysis Summary", expand=False)
        summary_table.add_column("Symbol", style="cyan", justify="center")
        summary_table.add_column("Timeframe", justify="center")
        summary_table.add_column("Direction", justify="center")
        summary_table.add_column("Action", justify="center")
        summary_table.add_column("Confidence", justify="right")
        summary_table.add_column("Analysis", overflow="fold")

        for result in self.cycle_results:
            dir_color = "green" if result['direction'] == "BULLISH" else "red" if result['direction'] == "BEARISH" else "yellow"
            action_color = "green" if result['action'] == "BUY" else "red" if result['action'] == "SELL" else "yellow"

            summary_table.add_row(
                result['symbol'],
                result['timeframe'],
                f"[{dir_color}]{result['direction']}[/{dir_color}]",
                f"[{action_color}]{result['action']}[/{action_color}]",
                f"{result['confidence']}%",
                result['analysis']
            )

        console.print("\n")
        console.print(summary_table)

    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        try:
            # Clear previous cycle results
            self.cycle_results = []

            # Clean up old charts before starting new cycle
            self._cleanup_old_charts()

            for symbol in SYMBOLS:
                for timeframe in TIMEFRAMES:
                    self.analyze_symbol(symbol, timeframe)
                    time.sleep(2)  # Small delay between analyses

            # Print summary table at end of cycle
            self._print_summary_table()

        except Exception as e:
            print(f"❌ Error in monitoring cycle: {str(e)}")
            
    def run(self):
        """Run the chart analysis monitor continuously"""
        print("\n🚀 Starting chart analysis monitoring...")
        
        while True:
            try:
                self.run_monitoring_cycle()
                print(f"\n💤 Sleeping for {CHECK_INTERVAL_MINUTES} minutes...")
                time.sleep(CHECK_INTERVAL_MINUTES * 60)
                
            except KeyboardInterrupt:
                print("\n👋 Chuck the Chart Agent shutting down gracefully...")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {str(e)}")
                time.sleep(60)  # Sleep for a minute before retrying

if __name__ == "__main__":
    # Create and run the agent
    print("\nChart Analysis Agent Starting Up...")
    print("👋 Hey! I'm Chuck, your friendly chart analysis agent! 📊")
    print(f"🎯 Monitoring {len(SYMBOLS)} symbols: {', '.join(SYMBOLS)}")
    agent = ChartAnalysisAgent()
    
    # Run the continuous monitoring cycle
    agent.run()
