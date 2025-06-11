import axios from "axios";

const api = axios.create({
  baseURL: "https://sua-api.com", // Substitua pela sua URL
});

export const fetchReputationData = () => api.get("/reputation");
export const loginUser = (credentials) => api.post("/login", credentials);