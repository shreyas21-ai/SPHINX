import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Grid, Card, CardContent, Typography, Box, Button, CircularProgress,
  Paper, Divider, Chip, Avatar, Skeleton, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Alert, AlertTitle, Collapse, IconButton
} from '@mui/material';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import PeopleIcon from '@mui/icons-material/People';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import EventIcon from '@mui/icons-material/Event';
import LockSearchIcon from '@mui/icons-material/ManageSearch';
import SecurityIcon from '@mui/icons-material/Security';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import ShieldIcon from '@mui/icons-material/Shield';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import CalculateIcon from '@mui/icons-material/Calculate';
import { ResponsiveContainer, PieChart, Pie, Cell, BarChart, Bar, XAxis, YAxis, Tooltip, Legend } from 'recharts';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const StatCard = ({ title, value, icon, color, subtitle, loading }) => (
  <Card variant="outlined">
    <CardContent>
      <Box display="flex" justifyContent="space-between" alignItems="flex-start">
        <Box>
          <Typography variant="caption" color="text.secondary" fontWeight="700" textTransform="uppercase">
            {title}
          </Typography>
          {loading ? (
            <Skeleton width={80} height={40} />
          ) : (
            <Typography variant="h4" fontWeight="700" sx={{ my: 0.5 }}>
              {value ?? 0}
            </Typography>
          )}
          <Typography variant="caption" color="text.secondary">
            {subtitle}
          </Typography>
        </Box>
        <Avatar sx={{ bgcolor: `${color}.main`, width: 48, height: 48 }}>
          {icon}
        </Avatar>
      </Box>
    </CardContent>
  </Card>
);

const COLORS = ['#0284c7', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export const DashboardPage = () => {
  const navigate = useNavigate();
  const { user, role } = useAuth();

  const [stats, setStats] = useState(null);
  const [patientsList, setPatientsList] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState(null);
  const [alertsExpanded, setAlertsExpanded] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/dashboard/stats');
        if (response.data?.status === 'success') {
          setStats(response.data.data);
        }
        if (role === 'NURSE') {
          const patRes = await api.get('/patients').catch(() => ({ data: { data: [] } }));
          if (patRes.data?.status === 'success') {
            setPatientsList(patRes.data.data || []);
          }
        }
        // Fetch security alerts for ADMIN only
        if (role === 'ADMIN') {
          const alertRes = await api.get('/dashboard/alerts').catch(() => null);
          if (alertRes?.data?.status === 'success') {
            setAlerts(alertRes.data.data);
          }
        }
      } catch (err) {
        console.error("Failed to load dashboard stats:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, [role]);

  if (role === 'NURSE') {
    return (
      <Box>
        {/* Nurse Header Banner */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight="700">
              Healthcare Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Welcome back, {user?.first_name} {user?.last_name} (NURSE) • Patient Care Overview
            </Typography>
          </Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<LockSearchIcon />}
            onClick={() => navigate('/search')}
            size="large"
          >
            Cryptographic Search
          </Button>
        </Box>

        {/* Nurse Metric Cards */}
        <Grid container spacing={2.5} mb={3}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="MY ASSIGNED PATIENTS"
              value={stats?.statistics?.patient_count}
              subtitle="Authorized patients under nursing care"
              icon={<PeopleIcon />}
              color="primary"
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="TODAY'S APPOINTMENTS"
              value={stats?.statistics?.today_appointments}
              subtitle="Consultations scheduled for today"
              icon={<EventIcon />}
              color="warning"
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="UPCOMING APPOINTMENTS"
              value={stats?.statistics?.upcoming_appointments_count}
              subtitle="Scheduled upcoming consultations"
              icon={<EventIcon />}
              color="secondary"
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="RECENT PATIENT ACCESSES"
              value={stats?.statistics?.today_searches}
              subtitle="Patient record lookups today"
              icon={<LockSearchIcon />}
              color="info"
              loading={loading}
            />
          </Grid>
        </Grid>

        {/* Section 1: Today's Schedule */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="700" mb={1}>
              Today's Schedule
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {!stats?.upcoming_appointments || stats.upcoming_appointments.length === 0 ? (
              <Typography variant="body2" color="text.secondary" py={2}>
                No scheduled appointments found for today.
              </Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead sx={{ bgcolor: 'action.hover' }}>
                    <TableRow>
                      <TableCell fontWeight="700">Time</TableCell>
                      <TableCell fontWeight="700">Patient</TableCell>
                      <TableCell fontWeight="700">Assigned Doctor</TableCell>
                      <TableCell fontWeight="700">Assigned Nurse</TableCell>
                      <TableCell fontWeight="700">Reason</TableCell>
                      <TableCell fontWeight="700">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {stats.upcoming_appointments.map((apt) => (
                      <TableRow key={apt.public_id} hover>
                        <TableCell fontWeight="600">{new Date(apt.appointment_date).toLocaleString()}</TableCell>
                        <TableCell fontWeight="600">{apt.patient_name || 'Patient'}</TableCell>
                        <TableCell>{apt.doctor_name || 'Doctor'}</TableCell>
                        <TableCell>{apt.nurse_name || 'Unassigned'}</TableCell>
                        <TableCell>{apt.reason || 'Consultation'}</TableCell>
                        <TableCell>
                          <Chip
                            label={apt.status}
                            size="small"
                            color={apt.status === 'COMPLETED' ? 'success' : apt.status === 'CANCELLED' ? 'error' : 'warning'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Section 2: My Patients Overview */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
              <Typography variant="h6" fontWeight="700">
                My Patients
              </Typography>
              <Button size="small" onClick={() => navigate('/patients')}>View All Patients</Button>
            </Box>
            <Divider sx={{ mb: 2 }} />

            {patientsList.length === 0 ? (
              <Typography variant="body2" color="text.secondary" py={2}>
                No patient records loaded.
              </Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead sx={{ bgcolor: 'action.hover' }}>
                    <TableRow>
                      <TableCell fontWeight="700">Patient</TableCell>
                      <TableCell fontWeight="700">Blood Group</TableCell>
                      <TableCell fontWeight="700">Gender / Contact</TableCell>
                      <TableCell align="right" fontWeight="700">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {patientsList.slice(0, 5).map((p) => (
                      <TableRow key={p.public_id} hover>
                        <TableCell fontWeight="600">{p.first_name} {p.last_name}</TableCell>
                        <TableCell>
                          <Chip label={p.blood_group || 'N/A'} size="small" variant="outlined" color="primary" />
                        </TableCell>
                        <TableCell>{p.gender || 'N/A'} • {p.phone || 'N/A'}</TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            variant="outlined"
                            onClick={() => navigate(`/patients/${p.public_id}`)}
                          >
                            View Patient
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Nurse Quick Actions */}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/search')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <LockSearchIcon color="primary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  Cryptographic Search
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Search encrypted patient records using blind HMAC search index under nursing scope.
              </Typography>
              <Button size="small" endIcon={<ArrowForwardIcon />}>Launch Console</Button>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/patients')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <PeopleIcon color="secondary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  Patient Directory
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                View authorized patient records and clinical history for patients under nursing care.
              </Typography>
              <Button size="small" color="secondary" endIcon={<ArrowForwardIcon />}>View Patient Directory</Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  }

  if (role === 'INSURANCE_OFFICER') {
    return (
      <Box>
        {/* Insurance Officer Header Banner */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight="700">
              Insurance Claims & Billing Dashboard
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Welcome back, {user?.first_name} {user?.last_name} ({role}) • Claim Processing Console
            </Typography>
          </Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<ReceiptLongIcon />}
            onClick={() => navigate('/billing')}
            size="large"
          >
            Billing & Claims Engine
          </Button>
        </Box>

        {/* Top 4 Stat Cards */}
        <Grid container spacing={2.5} mb={4}>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="TOTAL PATIENTS"
              value={stats?.statistics?.patient_count || 0}
              subtitle="Registered patient profiles"
              icon={<PeopleIcon color="primary" fontSize="large" />}
              accentColor="primary"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="PROCESSED CLAIMS"
              value={stats?.statistics?.total_claims || 0}
              subtitle="Generated billing statements"
              icon={<ReceiptLongIcon color="success" fontSize="large" />}
              accentColor="success"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="TOTAL BILL AMOUNT"
              value={stats?.statistics?.total_bill_amount ? `₹${stats.statistics.total_bill_amount.toLocaleString()}` : '₹0'}
              subtitle="Gross itemized hospital charges"
              icon={<CalculateIcon color="warning" fontSize="large" />}
              accentColor="warning"
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <StatCard
              title="APPROVED COVERAGE"
              value={stats?.statistics?.approved_amount ? `₹${stats.statistics.approved_amount.toLocaleString()}` : '₹0'}
              subtitle="Insurance covered claim payouts"
              icon={<ShieldIcon color="info" fontSize="large" />}
              accentColor="info"
            />
          </Grid>
        </Grid>

        {/* Quick Action Navigation */}
        <Typography variant="h6" fontWeight="700" mb={2}>
          Insurance Officer Workspaces
        </Typography>
        <Grid container spacing={2.5}>
          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/billing')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <ReceiptLongIcon color="primary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  Billing & Claims Engine
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Select patients, view claim summary context, itemize hospital charges, and process insurance payouts.
              </Typography>
              <Button size="small" endIcon={<ArrowForwardIcon />}>Open Billing Engine</Button>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'secondary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/patients')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <PeopleIcon color="secondary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  Patient Directory
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Access role-masked patient profiles, insurance provider details, policy numbers, and contact info under purpose BILLING.
              </Typography>
              <Button size="small" color="secondary" endIcon={<ArrowForwardIcon />}>View Patient Directory</Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  }

  if (role === 'DOCTOR') {
    return (
      <Box>
        {/* Doctor Header Banner */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          <Box>
            <Typography variant="h4" fontWeight="700">
              Doctor Clinical Workspace
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Welcome back, Dr. {user?.first_name} {user?.last_name} • Scoped Patient Care Console
            </Typography>
          </Box>
          <Button
            variant="contained"
            color="primary"
            startIcon={<LockSearchIcon />}
            onClick={() => navigate('/search')}
            size="large"
          >
            Secure Search
          </Button>
        </Box>

        {/* Doctor Metric Cards */}
        <Grid container spacing={2.5} mb={3}>
          <Grid item xs={12} sm={4}>
            <StatCard
              title="My Patients"
              value={stats?.statistics?.patient_count}
              subtitle="Authorized patients under my care"
              icon={<PeopleIcon />}
              color="primary"
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard
              title="My Today's Appointments"
              value={stats?.statistics?.today_appointments}
              subtitle="Consultations scheduled for today"
              icon={<EventIcon />}
              color="warning"
              loading={loading}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <StatCard
              title="My Secure Searches Today"
              value={stats?.statistics?.today_searches}
              subtitle="Cryptographic index lookups"
              icon={<LockSearchIcon />}
              color="info"
              loading={loading}
            />
          </Grid>
        </Grid>

        {/* Doctor Upcoming Appointments Table */}
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" fontWeight="700" mb={1}>
              My Assigned Today's & Upcoming Appointments
            </Typography>
            <Divider sx={{ mb: 2 }} />

            {!stats?.upcoming_appointments || stats.upcoming_appointments.length === 0 ? (
              <Typography variant="body2" color="text.secondary" py={2}>
                No upcoming appointments currently assigned to you.
              </Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead sx={{ bgcolor: 'action.hover' }}>
                    <TableRow>
                      <TableCell fontWeight="700">Appointment ID</TableCell>
                      <TableCell fontWeight="700">Scheduled Date & Time</TableCell>
                      <TableCell fontWeight="700">Reason / Clinical Notes</TableCell>
                      <TableCell fontWeight="700">Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {stats.upcoming_appointments.map((apt) => (
                      <TableRow key={apt.public_id}>
                        <TableCell>#{apt.public_id?.substring(0, 8)}</TableCell>
                        <TableCell>{new Date(apt.appointment_date).toLocaleString()}</TableCell>
                        <TableCell>{apt.reason || 'General Consultation'}</TableCell>
                        <TableCell>
                          <Chip label={apt.status} size="small" color={apt.status === 'COMPLETED' ? 'success' : 'primary'} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </CardContent>
        </Card>

        {/* Doctor Quick Actions */}
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/search')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <LockSearchIcon color="primary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  Secure Cryptographic Search
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                Search encrypted patient records using HMAC blind index (Exact & Substring).
              </Typography>
              <Button size="small" endIcon={<ArrowForwardIcon />}>Launch Console</Button>
            </Paper>
          </Grid>

          <Grid item xs={12} sm={6}>
            <Paper
              variant="outlined"
              sx={{
                p: 2.5,
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main', bgcolor: 'action.hover' }
              }}
              onClick={() => navigate('/patients')}
            >
              <Box display="flex" alignItems="center" gap={1.5} mb={1}>
                <PeopleIcon color="secondary" fontSize="large" />
                <Typography variant="subtitle1" fontWeight="700">
                  My Patients Directory
                </Typography>
              </Box>
              <Typography variant="body2" color="text.secondary" mb={2}>
                View authorized patient records and clinical history for patients under your care.
              </Typography>
              <Button size="small" color="secondary" endIcon={<ArrowForwardIcon />}>View My Patients</Button>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    );
  }

  // Admin / General View
  const purposeChartData = stats?.audit_summary?.events_by_purpose
    ? Object.entries(stats.audit_summary.events_by_purpose).map(([name, value]) => ({ name, value }))
    : [
        { name: 'TREATMENT', value: 12 },
        { name: 'BILLING', value: 5 },
        { name: 'RESEARCH', value: 3 },
        { name: 'EMERGENCY', value: 1 },
      ];

  const roleChartData = stats?.audit_summary?.events_by_role
    ? Object.entries(stats.audit_summary.events_by_role).map(([name, value]) => ({ name, value }))
    : [
        { name: 'DOCTOR', value: 14 },
        { name: 'NURSE', value: 8 },
        { name: 'RECEPTIONIST', value: 6 },
        { name: 'INSURANCE_OFFICER', value: 4 },
      ];

  return (
    <Box>
      {/* Header Banner */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="700">
            Enterprise Healthcare Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Welcome back, {user?.first_name} {user?.last_name} ({role}) • Privacy-First Retrieval Platform
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="primary"
          startIcon={<LockSearchIcon />}
          onClick={() => navigate('/search')}
          size="large"
        >
          Cryptographic Search
        </Button>
      </Box>

      {/* Metric Cards Grid */}
      <Grid container spacing={2.5} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Total Registered Patients"
            value={stats?.statistics?.patient_count}
            subtitle="Encrypted at rest (AES-256)"
            icon={<PeopleIcon />}
            color="primary"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Active Doctors"
            value={stats?.statistics?.doctor_count}
            subtitle="Licensed medical staff"
            icon={<LocalHospitalIcon />}
            color="secondary"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Appointments"
            value={stats?.statistics?.today_appointments}
            subtitle="Scheduled consultations"
            icon={<EventIcon />}
            color="warning"
            loading={loading}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard
            title="Today's Cryptographic Searches"
            value={stats?.statistics?.today_searches}
            subtitle="Zero full-DB decryptions"
            icon={<LockSearchIcon />}
            color="info"
            loading={loading}
          />
        </Grid>
      </Grid>

      {/* ── Security Alert Panel (ADMIN only) ── */}
      {alerts !== null && (
        <Card
          variant="outlined"
          sx={{
            mb: 3,
            borderColor: alerts.total_alerts > 0 ? 'warning.main' : 'success.main',
            bgcolor: alerts.total_alerts > 0 ? 'warning.50' : 'success.50'
          }}
        >
          <CardContent>
            <Box display="flex" justifyContent="space-between" alignItems="center">
              <Box display="flex" alignItems="center" gap={1}>
                <WarningAmberIcon
                  color={alerts.total_alerts > 0 ? 'warning' : 'success'}
                />
                <Typography variant="h6" fontWeight="700">
                  Security Activity Alerts
                </Typography>
                <Chip
                  label={alerts.total_alerts === 0 ? 'No Alerts' : `${alerts.total_alerts} Active`}
                  color={alerts.total_alerts > 0 ? 'warning' : 'success'}
                  size="small"
                />
              </Box>
              <IconButton
                size="small"
                onClick={() => setAlertsExpanded(prev => !prev)}
                aria-label="toggle alerts"
              >
                {alertsExpanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
              </IconButton>
            </Box>

            <Collapse in={alertsExpanded}>
              <Divider sx={{ my: 1.5 }} />

              {/* Summary row */}
              <Box display="flex" gap={2} flexWrap="wrap" mb={2}>
                <Chip size="small" label={`Failed Logins: ${alerts.summary.repeated_failed_logins}`} color={alerts.summary.repeated_failed_logins > 0 ? 'error' : 'default'} />
                <Chip size="small" label={`Excessive Searches: ${alerts.summary.excessive_searches}`} color={alerts.summary.excessive_searches > 0 ? 'warning' : 'default'} />
                <Chip size="small" label={`Off-Hours Logins: ${alerts.summary.off_hours_logins}`} color={alerts.summary.off_hours_logins > 0 ? 'info' : 'default'} />
                <Chip size="small" label="Large Downloads: N/A (no download endpoint)" color="default" />
              </Box>

              {alerts.total_alerts === 0 ? (
                <Alert severity="success" sx={{ borderRadius: 2 }}>
                  No active security alerts. All activity patterns are within normal parameters.
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead sx={{ bgcolor: 'action.hover' }}>
                      <TableRow>
                        <TableCell><strong>Severity</strong></TableCell>
                        <TableCell><strong>Type</strong></TableCell>
                        <TableCell><strong>User</strong></TableCell>
                        <TableCell><strong>Role</strong></TableCell>
                        <TableCell><strong>Detail</strong></TableCell>
                        <TableCell><strong>Detection</strong></TableCell>
                        <TableCell><strong>Recommendation</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {alerts.alerts.map((alert, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell>
                            <Chip
                              label={alert.severity}
                              size="small"
                              color={alert.severity === 'HIGH' ? 'error' : alert.severity === 'MEDIUM' ? 'warning' : 'info'}
                            />
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', fontFamily: 'monospace' }}>
                            {alert.alert_type}
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.8rem' }}>{alert.user_email}</TableCell>
                          <TableCell>
                            <Chip label={alert.user_role} size="small" variant="outlined" />
                          </TableCell>
                          <TableCell sx={{ maxWidth: 260, fontSize: '0.8rem' }}>{alert.detail}</TableCell>
                          <TableCell>
                            <Chip
                              label={alert.detection_method === 'ISOLATION_FOREST' ? 'ML: IsoForest' : 'Rule'}
                              size="small"
                              color={alert.detection_method === 'ISOLATION_FOREST' ? 'secondary' : 'default'}
                            />
                          </TableCell>
                          <TableCell sx={{ fontSize: '0.75rem', color: 'text.secondary' }}>
                            {alert.recommendation}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}

              {/* Limitation notice */}
              {alerts.limitations?.length > 0 && (
                <Alert severity="info" sx={{ mt: 1.5, borderRadius: 2, fontSize: '0.75rem' }}>
                  <AlertTitle>Monitoring Limitation</AlertTitle>
                  {alerts.limitations[0]}
                </Alert>
              )}

              <Typography variant="caption" color="text.secondary" display="block" mt={1}>
                Generated at: {alerts.generated_at ? new Date(alerts.generated_at).toLocaleString() : '—'}
              </Typography>
            </Collapse>
          </CardContent>
        </Card>
      )}

      {/* Analytics Charts */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" fontWeight="700" gutterBottom>
              Record Access Events by Purpose
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" mb={2}>
              HIPAA Purpose breakdown stored in Audit Logs
            </Typography>
            <Box height={260}>
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={purposeChartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={5}
                    dataKey="value"
                  >
                    {purposeChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card variant="outlined" sx={{ p: 2 }}>
            <Typography variant="h6" fontWeight="700" gutterBottom>
              System Access Events by User Role
            </Typography>
            <Typography variant="caption" color="text.secondary" display="block" mb={2}>
              Role-based data exposure tracking
            </Typography>
            <Box height={260}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={roleChartData}>
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#0284c7" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};
