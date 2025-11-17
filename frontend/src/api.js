import axios from "axios";
import { API_BASE } from "./config";

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 10000,
});

export const predict = (ticker) => api.get("/api/predict", { params: { ticker } });
export const prediction = (ticker) => api.post("/api/predict_batch", { ticker });
export const summary = (ticker) => api.get("/api/summary", { params: { ticker } });
export const health = () => api.get("/health");