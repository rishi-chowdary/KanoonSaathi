import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8080/api",
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("lexilegal_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      const isAuthRoute =
        window.location.pathname === "/login" ||
        window.location.pathname === "/register";

      localStorage.removeItem("lexilegal_token");

      if (!isAuthRoute && typeof window !== "undefined") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export const simplifyLegalText = async (payload) => {
  const response = await api.post("/simplify", payload, { timeout: 180000 });
  return response.data;
};

export const reExplainDocumentClause = async (documentId, clauseId, mode = "simple_english") => {
  const response = await api.post(
    `/documents/${documentId}/clauses/${clauseId}/re-explain?mode=${encodeURIComponent(mode)}`,
    {},
    { timeout: 180000 }
  );
  return response.data;
};

export const getDocumentRisks = async (documentId, params = {}) => {
  const response = await api.get(`/documents/${documentId}/risks`, { params });
  return response.data;
};

export const getDocumentKeyInfo = async (documentId) => {
  const response = await api.get(`/documents/${documentId}/key-info`);
  return response.data;
};

export const getDocumentMissingProvisions = async (documentId) => {
  const response = await api.get(`/documents/${documentId}/missing`);
  return response.data;
};

export default api;
