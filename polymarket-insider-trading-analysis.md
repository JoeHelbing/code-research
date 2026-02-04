# Polymarket Real-Time Transaction Data Analysis for Insider Trading Detection

## Executive Summary

This report analyzes the feasibility of building an unsupervised model to detect potential insider trading on Polymarket prediction markets. The platform offers multiple data access methods with varying latencies, from ~100ms WebSocket feeds to ~2-second blockchain confirmations. Key signals for detection include fresh wallet behavior, unusual position sizing, pre-news timing patterns, and wallet clustering—all achievable without ground truth labels using anomaly detection approaches.

---

## 1. Data Sources Overview

Polymarket provides three primary data access layers:

### 1.1 REST APIs

| API | Base URL | Purpose | Latency |
|-----|----------|---------|---------|
| **CLOB API** | `https://clob.polymarket.com` | Order management, prices, orderbooks | ~200-500ms |
| **Gamma API** | `https://gamma-api.polymarket.com` | Market discovery, metadata, events | ~1 second |
| **Data API** | `https://data-api.polymarket.com` | User positions, activity, trade history | ~200-500ms |

### 1.2 WebSocket Streams

| Service | Endpoint | Purpose | Latency |
|---------|----------|---------|---------|
| **CLOB WebSocket** | `wss://ws-subscriptions-clob.polymarket.com/ws/` | Orderbook updates, order status | ~100ms |
| **RTDS** | `wss://ws-live-data.polymarket.com` | Low-latency prices, activity, comments | ~100ms |

### 1.3 On-Chain Data (Polygon)

| Source | Method | Purpose | Latency |
|--------|--------|---------|---------|
| **Polygon RPC** | Direct RPC queries | Raw transaction data, event logs | 2-5 seconds (block time) |
| **PolygonScan** | API/GraphQL | Historical transactions, contract events | Seconds to minutes |
| **Bitquery GraphQL** | GraphQL queries | Processed trade data, market prices | Near real-time |

**Key Contracts:**
- CTF Exchange: `0x4bFb41d5B3570DeFd03C39a9A4D8dE6Bd8B8982E` (binary markets)
- NegRisk CTF Exchange: `0xC5d563A36AE78145C45a50134d48A1215220f80a` (multi-outcome markets)

---

## 2. Available Data Fields

### 2.1 Trade/Activity Data (Data API)

```json
{
  "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
  "timestamp": 1706123456,
  "size": "1000.0",
  "usdcSize": "650.00",
  "price": "0.65",
  "side": "BUY",
  "conditionId": "0x123abc...",
  "transactionHash": "0xdef456...",
  "asset": "21742633143463906290569050155826241533067272736897614950488156847949938836455",
  "outcomeIndex": 0,
  "type": "TRADE",
  "title": "Will X happen by Y date?",
  "slug": "will-x-happen",
  "outcome": "Yes"
}
```

**Query Parameters:**
- `type`: TRADE, SPLIT, MERGE, REDEEM, REWARD, CONVERSION
- `start/end`: Timestamp filters (Unix seconds)
- `side`: BUY or SELL
- `filterType`: CASH or TOKENS
- `filterAmount`: Minimum threshold
- `limit`: Max 500 records per request
- `sortBy`: TIMESTAMP, TOKENS, CASH

### 2.2 WebSocket Market Channel Events

| Event Type | Key Fields | Trigger |
|------------|------------|---------|
| `book` | asset_id, market, timestamp, bids[], asks[], hash | Initial subscription, trades |
| `price_change` | asset_id, price, size, side, best_bid, best_ask | Order placed/cancelled |
| `last_trade_price` | price, side, size, fee_rate_bps, timestamp | Trade execution |
| `best_bid_ask` | best_bid, best_ask, spread, timestamp | Price movement |
| `new_market` | id, question, description, outcomes, assets_ids | Market creation |
| `market_resolved` | winning_asset_id, winning_outcome | Market settlement |

### 2.3 On-Chain Event Data (OrderFilled)

```
Event: OrderFilled
Fields:
  - orderHash: bytes32 (unique order identifier)
  - maker: address (liquidity provider)
  - taker: address (order filler)
  - makerAssetId: uint256 (0 = USDC, else = outcome token)
  - takerAssetId: uint256
  - makerAmountFilled: uint256
  - takerAmountFilled: uint256
```

### 2.4 Enrichable Wallet Metadata

| Data Point | Source | Purpose |
|------------|--------|---------|
| Wallet age | Polygon RPC | Fresh wallet detection |
| Transaction count | Polygon RPC | Activity history |
| Funding source | On-chain tracing | Cluster detection |
| Total positions | Data API | Portfolio analysis |
| Win rate by category | Computed | Expertise detection |

---

## 3. Latency Analysis

### 3.1 Data Feed Latencies

```
┌─────────────────────────────────────────────────────────────────┐
│                     DATA LATENCY SPECTRUM                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WebSocket (CLOB/RTDS)    ████░░░░░░░░░░░░░░░░  ~100ms         │
│  REST APIs                ██████████░░░░░░░░░░  ~200-500ms     │
│  Gamma API                ████████████████░░░░  ~1 second      │
│  Polygon Block Time       ████████████████████  ~2 seconds     │
│  Polygon Finality         ████████████████████████████  ~5 sec │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Practical Implications for Detection

| Use Case | Recommended Source | Expected Delay |
|----------|-------------------|----------------|
| Real-time trade monitoring | WebSocket RTDS | 100-200ms |
| Order book analysis | CLOB WebSocket | ~100ms |
| Historical trade analysis | Data API | N/A (batch) |
| Wallet history lookup | Polygon RPC | 2-5 seconds |
| Funding chain tracing | On-chain indexer | Minutes to hours |

### 3.3 Detection Window Analysis

**Critical timing for insider trading detection:**
- Insiders typically place trades **1-4 hours** before news breaks
- Most suspicious activity occurs in **low-liquidity windows** (off-peak hours)
- Fresh wallets are often created **hours to days** before placing trades

**Conclusion:** The ~100ms WebSocket latency is more than sufficient for detection purposes, as we're looking for patterns over hours, not milliseconds.

---

## 4. Data Collection Architecture

### 4.1 Recommended Real-Time Pipeline

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION PIPELINE                             │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌──────────────────┐
                    │  WebSocket RTDS  │
                    │  (Activity Feed) │
                    └────────┬─────────┘
                             │ ~100ms
                             ▼
┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐
│ CLOB WebSocket│───▶│  Stream Processor │◀───│   Polygon RPC    │
│ (Order Book)  │    │   (Kafka/Redis)   │    │ (Wallet Lookup)  │
└──────────────┘    └────────┬─────────┘    └──────────────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │  Trade Store │ │ Wallet Cache │ │ Feature Store│
     │  (TimescaleDB)│ │   (Redis)    │ │   (Redis)    │
     └──────────────┘ └──────────────┘ └──────────────┘
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌──────────────────┐
                    │  Detection Model │
                    │  (Real-time ML)  │
                    └────────┬─────────┘
                             │
                             ▼
                    ┌──────────────────┐
                    │   Alert System   │
                    └──────────────────┘
```

### 4.2 Data Collection Code Example

```python
import asyncio
import websockets
import json
from datetime import datetime

RTDS_URL = "wss://ws-live-data.polymarket.com"

async def connect_to_polymarket():
    async with websockets.connect(RTDS_URL) as ws:
        # Subscribe to activity feed
        subscribe_msg = {
            "type": "subscribe",
            "channel": "activity",
            "filter": "*"  # All markets
        }
        await ws.send(json.dumps(subscribe_msg))

        async for message in ws:
            data = json.loads(message)
            await process_trade(data)

async def process_trade(trade_data):
    """Extract features for anomaly detection"""
    features = {
        "timestamp": trade_data.get("timestamp"),
        "wallet": trade_data.get("proxyWallet"),
        "market_id": trade_data.get("conditionId"),
        "side": trade_data.get("side"),
        "size_usdc": float(trade_data.get("usdcSize", 0)),
        "price": float(trade_data.get("price", 0)),
        # Enrichment needed:
        # - wallet_age
        # - wallet_tx_count
        # - market_volume_24h
        # - time_to_resolution
    }
    return features
```

### 4.3 Wallet Enrichment via Polygon RPC

```python
from web3 import Web3

POLYGON_RPC = "https://polygon-rpc.com"
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC))

def get_wallet_age(address: str) -> dict:
    """Get wallet creation time and transaction count"""
    tx_count = w3.eth.get_transaction_count(address)

    # First transaction timestamp requires indexer or binary search
    # For production, use a service like Covalent or Alchemy

    return {
        "address": address,
        "tx_count": tx_count,
        "is_fresh": tx_count < 5
    }
```

---

## 5. Insider Trading Detection Model Design

### 5.1 Problem Formulation

**Challenge:** No ground truth labels for insider trading exist. We must use unsupervised anomaly detection to identify "informed" trades.

**Key Insight:** Insider trades exhibit statistical anomalies across multiple dimensions:
- **Timing:** Positioned before information becomes public
- **Sizing:** Unusually large relative to trader's history
- **Wallet Behavior:** Fresh wallets, single-market focus
- **Outcome:** Abnormally high win rates in niche categories

### 5.2 Feature Engineering

#### Tier 1: Trade-Level Features
| Feature | Description | Computation |
|---------|-------------|-------------|
| `trade_size_zscore` | Size relative to market median | (size - median) / std |
| `price_distance_from_consensus` | Contrarian indicator | abs(price - 0.5) |
| `time_to_resolution` | Hours until market closes | resolution_time - trade_time |
| `time_of_day` | Hour (0-23) | Extract from timestamp |
| `is_weekend` | Weekend flag | day_of_week in [5, 6] |
| `order_book_impact` | % of visible liquidity | size / book_depth |

#### Tier 2: Wallet-Level Features
| Feature | Description | Computation |
|---------|-------------|-------------|
| `wallet_age_hours` | Time since first transaction | now - first_tx_time |
| `wallet_tx_count` | Total transactions | Count from RPC |
| `is_first_trade` | First trade on Polymarket | Boolean |
| `portfolio_concentration` | % in single market | market_size / total_size |
| `historical_win_rate` | Past accuracy | wins / total_resolved |
| `category_specialization` | Focus on specific topics | entropy(category_distribution) |

#### Tier 3: Temporal Features
| Feature | Description | Computation |
|---------|-------------|-------------|
| `volume_spike` | Ratio to 7-day average | volume_1h / avg_volume_7d |
| `price_momentum` | Recent price change | price_now - price_24h_ago |
| `hours_since_last_news` | Time from related news | NLP event detection |
| `market_age_hours` | How long market has existed | now - market_creation |

#### Tier 4: Cluster Features
| Feature | Description | Computation |
|---------|-------------|-------------|
| `funding_source_cluster` | Shared funding origin | Graph analysis |
| `timing_cluster_score` | Coordinated timing | DBSCAN on timestamps |
| `market_overlap_score` | Same markets as cluster | Jaccard similarity |

### 5.3 Model Architecture

#### Approach 1: Isolation Forest Ensemble

```python
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class InsiderDetector:
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            n_estimators=200,
            contamination=0.01,  # Expect ~1% anomalies
            random_state=42
        )

    def fit(self, features_df):
        X = self.scaler.fit_transform(features_df)
        self.model.fit(X)

    def score(self, features_df):
        X = self.scaler.transform(features_df)
        # Returns anomaly scores: lower = more anomalous
        return self.model.decision_function(X)

    def predict(self, features_df, threshold=-0.5):
        scores = self.score(features_df)
        return scores < threshold
```

#### Approach 2: Autoencoder Anomaly Detection

```python
import torch
import torch.nn as nn

class TradeAutoencoder(nn.Module):
    def __init__(self, input_dim, latent_dim=8):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, 32),
            nn.ReLU(),
            nn.Linear(32, 16),
            nn.ReLU(),
            nn.Linear(16, latent_dim)
        )
        self.decoder = nn.Sequential(
            nn.Linear(latent_dim, 16),
            nn.ReLU(),
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, input_dim)
        )

    def forward(self, x):
        z = self.encoder(x)
        return self.decoder(z)

    def reconstruction_error(self, x):
        x_recon = self.forward(x)
        return torch.mean((x - x_recon) ** 2, dim=1)

# Anomaly = high reconstruction error
# (Model learns "normal" patterns, struggles with anomalies)
```

#### Approach 3: Multi-Signal Scoring System

```python
class MultiSignalScorer:
    """Rule-based scoring with learned thresholds"""

    SIGNALS = {
        "fresh_wallet_large_bet": {
            "condition": lambda f: f["wallet_age_hours"] < 24 and f["trade_size_usdc"] > 5000,
            "weight": 3.0
        },
        "niche_market_concentration": {
            "condition": lambda f: f["portfolio_concentration"] > 0.8 and f["market_volume_24h"] < 50000,
            "weight": 2.0
        },
        "pre_resolution_spike": {
            "condition": lambda f: f["time_to_resolution"] < 24 and f["volume_spike"] > 5,
            "weight": 2.5
        },
        "extreme_position": {
            "condition": lambda f: f["trade_size_zscore"] > 3,
            "weight": 1.5
        },
        "off_hours_trading": {
            "condition": lambda f: f["time_of_day"] in range(2, 6),  # 2am-6am
            "weight": 1.0
        },
        "single_market_wallet": {
            "condition": lambda f: f["wallet_market_count"] == 1 and f["trade_size_usdc"] > 1000,
            "weight": 2.0
        }
    }

    def score(self, features: dict) -> float:
        total = 0
        triggered = []
        for name, signal in self.SIGNALS.items():
            if signal["condition"](features):
                total += signal["weight"]
                triggered.append(name)
        return total, triggered
```

### 5.4 Recommended Hybrid Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                      HYBRID DETECTION ARCHITECTURE                          │
└─────────────────────────────────────────────────────────────────────────────┘

                         ┌─────────────────┐
                         │  Trade Stream   │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │   Feature Extraction    │
                    │  (Trade + Wallet + Ctx) │
                    └────────────┬────────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              ▼                  ▼                  ▼
     ┌──────────────┐   ┌──────────────┐   ┌──────────────┐
     │  Isolation   │   │  Autoencoder │   │ Rule-Based   │
     │    Forest    │   │   Anomaly    │   │   Signals    │
     └──────┬───────┘   └──────┬───────┘   └──────┬───────┘
            │                  │                  │
            └──────────────────┼──────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │   Score Aggregator  │
                    │  (Weighted Ensemble)│
                    └──────────┬──────────┘
                               │
                    ┌──────────┴──────────┐
                    ▼                     ▼
           ┌──────────────┐      ┌──────────────┐
           │  High Alert  │      │  Watchlist   │
           │  (Score > θ₁)│      │  (Score > θ₂)│
           └──────────────┘      └──────────────┘
```

---

## 6. "Fast Follow" Strategy Implementation

### 6.1 Concept

When the model detects a potential insider trade with high confidence, automatically (or with human approval) place a following trade to profit from the presumed information.

### 6.2 Alert Pipeline

```python
class FastFollowPipeline:
    def __init__(self, detector, threshold=0.8):
        self.detector = detector
        self.threshold = threshold
        self.followed_trades = set()

    async def process_trade(self, trade: dict):
        features = await self.enrich_features(trade)
        score, signals = self.detector.score(features)

        if score >= self.threshold:
            alert = {
                "timestamp": datetime.utcnow().isoformat(),
                "trade": trade,
                "anomaly_score": score,
                "triggered_signals": signals,
                "recommended_action": self.compute_action(trade, score)
            }
            await self.emit_alert(alert)

    def compute_action(self, trade: dict, score: float) -> dict:
        return {
            "direction": trade["side"],  # Follow the insider
            "market": trade["conditionId"],
            "suggested_size": min(trade["usdcSize"] * 0.1, 1000),  # 10% of insider, max $1k
            "confidence": score,
            "urgency": "HIGH" if score > 0.9 else "MEDIUM"
        }
```

### 6.3 Risk Considerations

| Risk | Mitigation |
|------|------------|
| False positives | Require multiple signals, human review |
| Front-running detection | Randomize timing, limit size |
| Market impact | Cap position sizes, avoid thin markets |
| Legal/ethical | Document as "following public trades" |

---

## 7. Model Evaluation Without Ground Truth

### 7.1 Proxy Metrics

Since we lack labeled insider trades, use these evaluation approaches:

| Metric | Description | How to Compute |
|--------|-------------|----------------|
| **Win Rate Correlation** | Do flagged trades win more often? | Compare win rates: flagged vs. random |
| **Pre-News Timing** | Do alerts precede news events? | Cross-reference with news APIs |
| **Wallet Cluster Accuracy** | Do flagged wallets cluster together? | Graph analysis post-hoc |
| **Volume Prediction** | Do alerts precede volume spikes? | Measure volume T+1h to T+24h |
| **Resolution Accuracy** | Did flagged trades predict correctly? | Outcome tracking |

### 7.2 Backtesting Framework

```python
class BacktestEvaluator:
    def __init__(self, detector, news_api):
        self.detector = detector
        self.news_api = news_api

    def evaluate(self, historical_trades: list) -> dict:
        results = {
            "total_alerts": 0,
            "alerts_before_news": 0,
            "alert_win_rate": 0,
            "baseline_win_rate": 0,
            "avg_time_to_news": []
        }

        for trade in historical_trades:
            score, _ = self.detector.score(trade)
            if score > self.threshold:
                results["total_alerts"] += 1

                # Check if news followed
                news = self.news_api.get_related_news(
                    trade["market"],
                    start=trade["timestamp"],
                    end=trade["timestamp"] + timedelta(hours=24)
                )
                if news:
                    results["alerts_before_news"] += 1
                    results["avg_time_to_news"].append(
                        (news[0]["timestamp"] - trade["timestamp"]).seconds / 3600
                    )

        return results
```

---

## 8. Known Limitations & Challenges

### 8.1 Data Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| No wallet identity | Can't link to real-world insiders | Cluster analysis, funding tracing |
| API rate limits | May miss trades during spikes | Multiple connections, caching |
| WebSocket disconnects | Data gaps | Reconnection logic, backfill |
| Historical data depth | Limited backtesting | Archive own data stream |

### 8.2 Detection Challenges

| Challenge | Description |
|-----------|-------------|
| **Sophisticated insiders** | May split across wallets, use mixers |
| **Noise from whales** | Large traders aren't necessarily informed |
| **Market efficiency** | Information may be priced in legitimately |
| **Category diversity** | Different markets have different patterns |

### 8.3 Volume Double-Counting Issue

Per Paradigm's research, naive volume calculations double-count trades. A $4.13 YES token sale can appear as $8.26 in volume. Adjust calculations accordingly:

```python
def correct_volume(order_filled_events: list) -> float:
    """Compute actual USD volume without double-counting"""
    total = 0
    for event in order_filled_events:
        # Only count the USDC side
        if event["makerAssetId"] == 0:  # Maker provided USDC
            total += event["makerAmountFilled"] / 1e6  # USDC has 6 decimals
        elif event["takerAssetId"] == 0:  # Taker provided USDC
            total += event["takerAmountFilled"] / 1e6
    return total
```

---

## 9. Implementation Roadmap

### Phase 1: Data Infrastructure (Week 1-2)
- [ ] Set up WebSocket connections to RTDS and CLOB
- [ ] Implement Polygon RPC integration for wallet lookups
- [ ] Deploy TimescaleDB for trade storage
- [ ] Build Redis cache for real-time features

### Phase 2: Feature Pipeline (Week 3-4)
- [ ] Implement trade-level feature extraction
- [ ] Build wallet enrichment service
- [ ] Create temporal feature aggregations
- [ ] Develop cluster detection module

### Phase 3: Model Development (Week 5-6)
- [ ] Train Isolation Forest on historical data
- [ ] Implement autoencoder anomaly detector
- [ ] Build rule-based signal scorer
- [ ] Create ensemble aggregation logic

### Phase 4: Evaluation & Tuning (Week 7-8)
- [ ] Run backtests against historical trades
- [ ] Correlate alerts with news events
- [ ] Tune thresholds for precision/recall
- [ ] Document false positive patterns

### Phase 5: Production Deployment (Week 9-10)
- [ ] Deploy real-time scoring service
- [ ] Implement alerting system
- [ ] Build monitoring dashboard
- [ ] Create human review workflow

---

## 10. Tools & Libraries

### Python Packages
```
websockets>=11.0       # WebSocket client
web3>=6.0              # Polygon RPC
pandas>=2.0            # Data manipulation
scikit-learn>=1.3      # Isolation Forest, preprocessing
torch>=2.0             # Autoencoder
redis>=4.0             # Feature caching
timescaledb            # Time-series storage
kafka-python>=2.0      # Stream processing
```

### External Services
- **Polygon RPC**: Alchemy, Infura, or public endpoints
- **News API**: NewsAPI, GDELT, or custom scraper
- **Alerting**: Slack, Telegram, Discord webhooks

---

## 11. Sources

### Official Polymarket Documentation
- [Developer Quickstart](https://docs.polymarket.com/quickstart/overview)
- [CLOB Introduction](https://docs.polymarket.com/developers/CLOB/introduction)
- [WebSocket Overview](https://docs.polymarket.com/developers/CLOB/websocket/wss-overview)
- [Market Channel Events](https://docs.polymarket.com/developers/CLOB/websocket/market-channel)
- [API Endpoints](https://docs.polymarket.com/quickstart/reference/endpoints)
- [Data API Activity](https://docs.polymarket.com/developers/misc-endpoints/data-api-activity)

### Technical Resources
- [Polymarket Real-Time Data Client (GitHub)](https://github.com/Polymarket/real-time-data-client)
- [Polymarket Insider Tracker (GitHub)](https://github.com/pselamy/polymarket-insider-tracker)
- [Decoding Polymarket On-Chain Data](https://yzc.me/x01Crypto/decoding-polymarket)
- [Polymarket CTF Exchange on PolygonScan](https://polygonscan.com/address/0x4bfb41d5b3570defd03c39a9a4d8de6bd8b8982e)
- [Paradigm: Polymarket Volume Double-Counting](https://www.paradigm.xyz/2025/12/polymarket-volume-is-being-double-counted)

### Detection Approaches
- [PolyTrack: Detect Insider Trading Guide](https://www.polytrackhq.app/blog/detect-insider-trading-polymarket)
- [Polywhaler - Whale Tracker](https://www.polywhaler.com/)
- [Bloomberg: Race to Unmask Insider Bets](https://www.bloomberg.com/news/articles/2026-01-21/race-to-unmask-insider-bets-in-prediction-markets-is-heating-up)
- [Unusual Whales Polymarket Tool](https://phemex.com/news/article/unusual-whales-launches-tool-to-track-insider-trading-on-polymarket-54994)

### Machine Learning for Market Manipulation
- [ML Detection of Market Manipulation (Medium)](https://theaiquant.medium.com/unveiling-the-shadows-machine-learning-detection-of-market-manipulation-6d043aed2d10)
- [Stock Manipulation Detection via ML (ScienceDirect)](https://www.sciencedirect.com/science/article/abs/pii/S1057521921002143)
- [Ensemble Learning for Manipulation Detection](https://www.sciencedirect.com/science/article/abs/pii/S0957417424003440)

### Latency & Performance
- [How Latency Impacts Polymarket Bot Performance](https://www.quantvps.com/blog/how-latency-impacts-polymarket-trading-performance)
- [Polygon Block Time Chart](https://polygonscan.com/chart/blocktime)
- [Bitquery Polymarket API](https://docs.bitquery.io/docs/examples/polymarket-api/)

---

## Appendix A: Sample API Responses

### Trade Activity Response
```json
{
  "history": [
    {
      "proxyWallet": "0x56687bf447db6ffa42ffe2204a05edaa20f55839",
      "conditionId": "0x123...",
      "title": "Will BTC reach $100k by March 2026?",
      "slug": "btc-100k-march-2026",
      "outcome": "Yes",
      "outcomeIndex": 0,
      "side": "BUY",
      "price": "0.42",
      "size": "500.00",
      "usdcSize": "210.00",
      "timestamp": 1706918400,
      "transactionHash": "0xabc...",
      "type": "TRADE"
    }
  ],
  "nextCursor": "eyJsaW1pdCI6MTAwLCJvZmZzZXQiOjEwMH0="
}
```

### WebSocket Trade Event
```json
{
  "event_type": "last_trade_price",
  "asset_id": "21742633143463906290569050155826241533067272736897614950488156847949938836455",
  "market": "0x123abc...",
  "price": "0.65",
  "side": "BUY",
  "size": "1000.00",
  "fee_rate_bps": 0,
  "timestamp": 1706918400000
}
```

---

*Report generated: February 2026*
