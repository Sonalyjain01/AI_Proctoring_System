import React from "react";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { AuthProvider, AuthContext } from "./components/AuthContext";
import Login from "./components/Login";
import Register from "./components/Register";
import AdminDashboard from "./components/AdminDashboard";
import ProctoringDashboard from "./components/ProctoringDashboard";

const ProtectedRoute = ({ element, roles }) => {
    return (
        <AuthContext.Consumer>
            {({ auth }) =>
                auth && roles.includes(auth.role) ? (
                    element
                ) : (
                    <Navigate to="/login" />
                )
            }
        </AuthContext.Consumer>
    );
};

const App = () => {
    return (
        <AuthProvider>
            <Router>
                <ToastContainer />
                <Routes>
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/admin" element={<ProtectedRoute element={<AdminDashboard />} roles={["admin"]} />} />
                    <Route path="/dashboard" element={<ProtectedRoute element={<ProctoringDashboard />} roles={["student", "admin"]} />} />
                    <Route path="*" element={<Navigate to="/login" />} />
                </Routes>
            </Router>
        </AuthProvider>
    );
};

export default App;
