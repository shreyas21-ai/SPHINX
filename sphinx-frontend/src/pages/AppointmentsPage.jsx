import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Button, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Chip, Alert,
  Dialog, DialogTitle, DialogContent, DialogActions, TextField, Grid, MenuItem, CircularProgress
} from '@mui/material';
import EventIcon from '@mui/icons-material/Event';
import AddIcon from '@mui/icons-material/Add';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';

export const AppointmentsPage = () => {
  const { role } = useAuth();

  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  // Dropdown options for Schedule Dialog
  const [patientsList, setPatientsList] = useState([]);
  const [doctorsList, setDoctorsList] = useState([]);
  const [nursesList, setNursesList] = useState([]);

  // Schedule Modal State
  const [openBookModal, setOpenBookModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [newApt, setNewApt] = useState({
    patient_public_id: '',
    doctor_public_id: '',
    nurse_public_id: '',
    appointment_date: '',
    reason: ''
  });

  const fetchAppointments = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/appointments');
      if (response.data?.status === 'success') {
        setAppointments(response.data.data || []);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch appointments from server.');
    } finally {
      setLoading(false);
    }
  };

  const fetchDropdownOptions = async () => {
    try {
      const [patRes, docRes, nurRes] = await Promise.all([
        api.get('/patients'),
        api.get('/users/doctors').catch(() => ({ data: { data: [] } })),
        api.get('/users/nurses').catch(() => ({ data: { data: [] } }))
      ]);

      if (patRes.data?.status === 'success') {
        setPatientsList(patRes.data.data || []);
      }
      if (docRes.data?.status === 'success') {
        setDoctorsList(docRes.data.data || []);
      }
      if (nurRes.data?.status === 'success') {
        setNursesList(nurRes.data.data || []);
      }
    } catch (err) {
      console.error("Failed to load options for scheduling:", err);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const handleOpenScheduleModal = () => {
    fetchDropdownOptions();
    setOpenBookModal(true);
  };

  const handleScheduleSubmit = async () => {
    if (!newApt.patient_public_id || !newApt.doctor_public_id || !newApt.appointment_date) {
      setError('Please select Patient, Doctor, and Appointment Date & Time.');
      return;
    }

    setSubmitting(true);
    setError('');
    setSuccessMsg('');
    try {
      const response = await api.post('/appointments', newApt);
      if (response.data?.status === 'success') {
        setSuccessMsg('Appointment scheduled successfully.');
        setOpenBookModal(false);
        setNewApt({ patient_public_id: '', doctor_public_id: '', nurse_public_id: '', appointment_date: '', reason: '' });
        fetchAppointments();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to schedule appointment.');
    } finally {
      setSubmitting(false);
    }
  };

  const updateStatus = async (public_id, newStatus) => {
    setError('');
    setSuccessMsg('');
    try {
      const response = await api.patch(`/appointments/${public_id}/status`, { status: newStatus });
      if (response.data?.status === 'success') {
        setSuccessMsg(`Appointment status updated to ${newStatus}.`);
        fetchAppointments();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update appointment status.');
    }
  };

  const canSchedule = ['ADMIN', 'DOCTOR', 'RECEPTIONIST'].includes(role);
  const canUpdateStatus = ['ADMIN', 'DOCTOR', 'RECEPTIONIST'].includes(role);
  const canComplete = ['ADMIN', 'DOCTOR'].includes(role);
  const canCancel = ['ADMIN', 'DOCTOR', 'RECEPTIONIST'].includes(role);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <EventIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h4" fontWeight="700">
              Patient Appointment Scheduling
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Clinical consultation schedule and status updates ({role})
            </Typography>
          </Box>
        </Box>
        {canSchedule && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<AddIcon />}
            onClick={handleOpenScheduleModal}
          >
            Schedule Appointment
          </Button>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>{error}</Alert>}
      {successMsg && <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccessMsg('')}>{successMsg}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" py={5}>
          <CircularProgress />
        </Box>
      ) : appointments.length === 0 ? (
        <Card variant="outlined" sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="h6" fontWeight="600" color="text.secondary">
            No scheduled appointments found in database.
          </Typography>
          <Typography variant="body2" color="text.secondary" mt={1}>
            {canSchedule ? 'Click "Schedule Appointment" above to create a new appointment.' : 'Currently no active appointments assigned to view.'}
          </Typography>
        </Card>
      ) : (
        <TableContainer component={Card} variant="outlined">
          <Table>
            <TableHead sx={{ bgcolor: 'action.hover' }}>
              <TableRow>
                <TableCell fontWeight="700">Appointment ID</TableCell>
                <TableCell fontWeight="700">Patient</TableCell>
                <TableCell fontWeight="700">Assigned Doctor</TableCell>
                <TableCell fontWeight="700">Assigned Nurse</TableCell>
                <TableCell fontWeight="700">Scheduled Date & Time</TableCell>
                <TableCell fontWeight="700">Reason</TableCell>
                <TableCell fontWeight="700">Status</TableCell>
                {canUpdateStatus && <TableCell align="right" fontWeight="700">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {appointments.map((apt) => (
                <TableRow key={apt.public_id} hover>
                  <TableCell fontFamily="monospace" fontWeight="700">#{apt.public_id?.substring(0, 8)}</TableCell>
                  <TableCell fontWeight="600">{apt.patient_name || 'Patient'}</TableCell>
                  <TableCell>{apt.doctor_name || 'Doctor'}</TableCell>
                  <TableCell>{apt.nurse_name || 'Unassigned'}</TableCell>
                  <TableCell>{new Date(apt.appointment_date).toLocaleString()}</TableCell>
                  <TableCell>{apt.reason || 'Consultation'}</TableCell>
                  <TableCell>
                    <Chip
                      label={apt.status}
                      size="small"
                      color={apt.status === 'COMPLETED' ? 'success' : apt.status === 'CANCELLED' ? 'error' : 'warning'}
                      variant="outlined"
                    />
                  </TableCell>
                  {canUpdateStatus && (
                    <TableCell align="right">
                      {apt.status === 'SCHEDULED' && (
                        <Box display="flex" gap={1} justifyContent="flex-end">
                          {canComplete && (
                            <Button
                              size="small"
                              color="success"
                              startIcon={<CheckCircleIcon />}
                              onClick={() => updateStatus(apt.public_id, 'COMPLETED')}
                            >
                              Complete
                            </Button>
                          )}
                          {canCancel && (
                            <Button
                              size="small"
                              color="error"
                              startIcon={<CancelIcon />}
                              onClick={() => updateStatus(apt.public_id, 'CANCELLED')}
                            >
                              Cancel
                            </Button>
                          )}
                        </Box>
                      )}
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Schedule Modal */}
      <Dialog open={openBookModal} onClose={() => setOpenBookModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight="700">Schedule New Patient Appointment</DialogTitle>
        <DialogContent dividers>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                select
                label="Select Patient"
                fullWidth
                value={newApt.patient_public_id}
                onChange={(e) => setNewApt({ ...newApt, patient_public_id: e.target.value })}
              >
                {patientsList.map((p) => (
                  <MenuItem key={p.public_id} value={p.public_id}>
                    {p.first_name} {p.last_name} (#{p.public_id?.substring(0, 6)})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                select
                label="Assigned Doctor"
                fullWidth
                value={newApt.doctor_public_id}
                onChange={(e) => setNewApt({ ...newApt, doctor_public_id: e.target.value })}
              >
                {doctorsList.map((d) => (
                  <MenuItem key={d.public_id} value={d.public_id}>
                    Dr. {d.first_name} {d.last_name} ({d.email})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                select
                label="Assign Nurse"
                fullWidth
                value={newApt.nurse_public_id}
                onChange={(e) => setNewApt({ ...newApt, nurse_public_id: e.target.value })}
              >
                <MenuItem value="">Unassigned</MenuItem>
                {nursesList.map((n) => (
                  <MenuItem key={n.public_id} value={n.public_id}>
                    {n.first_name} {n.last_name} ({n.email})
                  </MenuItem>
                ))}
              </TextField>
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Appointment Date & Time"
                type="datetime-local"
                fullWidth
                InputLabelProps={{ shrink: true }}
                value={newApt.appointment_date}
                onChange={(e) => setNewApt({ ...newApt, appointment_date: e.target.value })}
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                label="Reason for Consultation"
                fullWidth
                multiline
                rows={2}
                value={newApt.reason}
                onChange={(e) => setNewApt({ ...newApt, reason: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenBookModal(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleScheduleSubmit}
            disabled={submitting}
          >
            {submitting ? 'Booking...' : 'Confirm Booking'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
