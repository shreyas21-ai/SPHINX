import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeContextProvider } from './contexts/ThemeContext';
import { AuthProvider } from './contexts/AuthContext';
import { PurposeProvider } from './contexts/PurposeContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { MainLayout } from './layouts/MainLayout';
import { AuthLayout } from './layouts/AuthLayout';

import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { SecureSearchPage } from './pages/SecureSearchPage';
import { PatientsPage } from './pages/PatientsPage';
import { PatientDetailPage } from './pages/PatientDetailPage';
import { MedicalRecordsPage } from './pages/MedicalRecordsPage';
import { AppointmentsPage } from './pages/AppointmentsPage';
import { AuditLogsPage } from './pages/AuditLogsPage';
import { UserManagementPage } from './pages/UserManagementPage';
import { ProfilePage } from './pages/ProfilePage';
import { BillingPage } from './pages/BillingPage';
import { NotFoundPage } from './pages/ErrorPages';

export const App = () => {
  return (
    <ThemeContextProvider>
      <AuthProvider>
        <PurposeProvider>
          <BrowserRouter>
            <Routes>
              {/* Public Auth Routes */}
              <Route element={<AuthLayout />}>
                <Route path="/login" element={<LoginPage />} />
              </Route>

              {/* Protected System Application Routes */}
              <Route element={<ProtectedRoute />}>
                <Route element={<MainLayout />}>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/patients" element={<PatientsPage />} />
                  <Route path="/patients/:id" element={<PatientDetailPage />} />
                  <Route path="/appointments" element={<AppointmentsPage />} />
                  <Route path="/profile" element={<ProfilePage />} />

                  {/* Cryptographic Search (Doctor & Nurse only) */}
                  <Route element={<ProtectedRoute allowedRoles={['DOCTOR', 'NURSE']} />}>
                    <Route path="/search" element={<SecureSearchPage />} />
                  </Route>

                  {/* Medical Records (Doctor, Nurse, Insurance Officer) */}
                  <Route element={<ProtectedRoute allowedRoles={['DOCTOR', 'NURSE', 'INSURANCE_OFFICER']} />}>
                    <Route path="/medical-records" element={<MedicalRecordsPage />} />
                  </Route>

                  {/* Insurance Officer Only Billing & Claims Workflow */}
                  <Route element={<ProtectedRoute allowedRoles={['INSURANCE_OFFICER']} />}>
                    <Route path="/billing" element={<BillingPage />} />
                  </Route>

                  {/* Admin Only Routes */}
                  <Route element={<ProtectedRoute allowedRoles={['ADMIN']} />}>
                    <Route path="/audit-logs" element={<AuditLogsPage />} />
                    <Route path="/users" element={<UserManagementPage />} />
                  </Route>
                </Route>
              </Route>

              {/* Catch-all 404 Route */}
              <Route path="*" element={<NotFoundPage />} />
            </Routes>
          </BrowserRouter>
        </PurposeProvider>
      </AuthProvider>
    </ThemeContextProvider>
  );
};

export default App;
