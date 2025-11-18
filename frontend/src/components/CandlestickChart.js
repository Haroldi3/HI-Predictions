import React from "react";
import { View } from "react-native";
import {
    VictoryChart,
    VictoryCandlestick,
    VictoryAxis,
    VictoryTheme,
} from "victory-native";

export default function CandlestickChart({ candles }) {
    if (!candles || candles.length === 0) return null;

    const data = candles.map((candles, idx) => ({
        x: idx,
        open: candles.open,
        close: candles.close,
        high: candles.high,
        low: candles.low,
    }));
    
    // Candle stick formatting/coloring (return here to change colors when predictive VS. actual charts are released)
    return (
        <View style={{ height: 260, marginTop: 20 }}>
            <VictoryChart
                theme={VictoryTheme.material}
                domainPadding={{ x: 10, y: 20 }}
            >
                <VictoryAxis tickFormat={() => ""} />
                <VictoryAxis dependentAxis />
                <VictoryCandlestick
                    data = {data}
                    candleRatio = {0.8}
                    candleWidth = {8}
                />
                </VictoryChart>
        </View>
    );
}
