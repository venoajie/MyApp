import {WebSocket} from 'ws';

const coin = 'btcusdt';

const ws = new WebSocket(`wss://fstream.binance.com/ws/${coin}@trade`);

ws.on('message', (data?: string) => {
    if (data) {
        const trade = JSON.parse(data); // parsing a single-trade record
        console.log(trade);
    }
});