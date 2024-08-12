
# MyApp
#### Provide non-hft trading platform that allowed multiple strategy in the same instrument. Could improve the capital efficiency and risk management.

#### Supported exchanges: Deribit. Others coming soon

#### WIP. Tested in Python 3.8 and Ubuntu 20.04 environment

## Hedging:

- [x] Check Market


```mermaid
flowchart LR

A[Check Market] --> B{Is Bearish?}
B -->|Yes| C{Is fully hedged?}
B -->|No| D[Any hedging?]
D -->|Yes| E{Is fully hedged?}
D -->|No| A[Check Market]
```
- [x] Automatic **hedging** for equity balances in crypto spot


```mermaid
flowchart LR

A[Hard] -->|Text| B(Round)
B --> C{Current < Open 1H?}
C -->|Yes| D{Current < Open 15M?}
C -->|No| E[Result 2]
D -->|Yes| F{Current < Open 5M?}
D -->|No| G[Result 2]
```
