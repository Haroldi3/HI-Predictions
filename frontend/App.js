import React, { useState } from "react";
import {
  SafeAreaView,
  View,
  Text,
  TextInput,
  Pressable,
  ActivityIndicator,
  StyleSheet,
  ScrollView,
} from "react-native";
import { API_BASE } from "./src/config";

const WATCHLIST = ["AAPL", "MSFT", "NVDA", "AMZN", "TSLA"];

export default function App() {
  const [ticker, setTicker] = useState("AAPL");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleSelectWatch = (t) => {
    setTicker(t);
    setResult(null);
    setError("");
  };

  const handlePredict = async () => {
    const t = ticker.trim().toUpperCase();
    if (!t) return;

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const url = `${API_BASE}/api/predict?ticker=${encodeURIComponent(t)}`;
      const res = await fetch(url);

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(msg || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
    } catch (e) {
      console.log("Predict error:", e.message);
      setError("Could not fetch prediction. Check network/backend.");
    } finally {
      setLoading(false);
    }
  };

  const renderResult = () => {
    if (!result) return null;

    const up = result.direction === "UP";
    const conf = Number(result.confidence || 0);
    const score = Number(result.trend_score || 0);

    return (
      <View style={styles.card}>
        <View style={styles.cardHeader}>
          <Text style={styles.cardTicker}>{result.ticker}</Text>
          <Text style={[styles.cardDirection, up ? styles.up : styles.down]}>
            {up ? "UP" : "DOWN"}
          </Text>
        </View>

        <Text style={styles.cardLabel}>Confidence</Text>
        <Text style={styles.cardValue}>{(conf * 100).toFixed(1)}%</Text>

        <Text style={styles.cardLabel}>Trend score</Text>
        <Text style={styles.cardValue}>{score.toFixed(2)}</Text>

        <Text style={styles.cardNote}>
          This is an AI-generated trend estimate based on recent price action,
          indicators, and news sentiment. Not financial advice.
        </Text>
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.safe}>
      <ScrollView
        contentContainerStyle={styles.container}
        keyboardShouldPersistTaps="handled"
      >
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.title}>HI Predictions</Text>
          <Text style={styles.subtitle}>AI Stock Trend Preview</Text>
        </View>

        {/* Watchlist */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Watchlist</Text>
          <View style={styles.watchlistRow}>
            {WATCHLIST.map((t) => (
              <Pressable
                key={t}
                onPress={() => handleSelectWatch(t)}
                style={[
                  styles.watchChip,
                  ticker.toUpperCase() === t && styles.watchChipActive,
                ]}
              >
                <Text
                  style={[
                    styles.watchChipText,
                    ticker.toUpperCase() === t && styles.watchChipTextActive,
                  ]}
                >
                  {t}
                </Text>
              </Pressable>
            ))}
          </View>
        </View>

        {/* Input + button */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Choose a ticker</Text>
          <TextInput
            value={ticker}
            onChangeText={(txt) => setTicker(txt.toUpperCase())}
            autoCapitalize="characters"
            placeholder="AAPL"
            placeholderTextColor="#777"
            style={styles.input}
          />

          <Pressable onPress={handlePredict} style={styles.button}>
            {loading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.buttonText}>Predict Trend</Text>
            )}
          </Pressable>

          {error ? <Text style={styles.errorText}>{error}</Text> : null}
        </View>

        {/* Result card */}
        {renderResult()}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: {
    flex: 1,
    backgroundColor: "#050812",
  },
  container: {
    padding: 16,
  },
  header: {
    marginBottom: 24,
  },
  title: {
    color: "#f5f7ff",
    fontSize: 24,
    fontWeight: "800",
  },
  subtitle: {
    color: "#808aa0",
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    color: "#c3c8d9",
    fontSize: 14,
    fontWeight: "600",
    marginBottom: 8,
  },
  watchlistRow: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
  },
  watchChip: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 999,
    borderWidth: 1,
    borderColor: "#2a3243",
    backgroundColor: "#0b1020",
  },
  watchChipActive: {
    backgroundColor: "#16a34a",
    borderColor: "#16a34a",
  },
  watchChipText: {
    color: "#c3c8d9",
    fontSize: 13,
    fontWeight: "600",
  },
  watchChipTextActive: {
    color: "#ffffff",
  },
  input: {
    marginTop: 4,
    paddingHorizontal: 12,
    paddingVertical: 10,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#2a3243",
    backgroundColor: "#0b1020",
    color: "#f5f7ff",
    fontSize: 16,
  },
  button: {
    marginTop: 12,
    backgroundColor: "#16a34a",
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
  },
  buttonText: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 16,
  },
  errorText: {
    color: "#f97373",
    marginTop: 8,
  },
  card: {
    marginTop: 8,
    borderRadius: 14,
    padding: 16,
    backgroundColor: "#0b1020",
    borderWidth: 1,
    borderColor: "#2a3243",
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 12,
    alignItems: "center",
  },
  cardTicker: {
    color: "#f5f7ff",
    fontSize: 20,
    fontWeight: "800",
  },
  cardDirection: {
    fontSize: 20,
    fontWeight: "800",
  },
  up: {
    color: "#22c55e",
  },
  down: {
    color: "#f97373",
  },
  cardLabel: {
    color: "#808aa0",
    marginTop: 8,
    fontSize: 13,
  },
  cardValue: {
    color: "#f5f7ff",
    fontSize: 16,
    fontWeight: "700",
  },
  cardNote: {
    color: "#6b7280",
    fontSize: 12,
    marginTop: 10,
  },
});