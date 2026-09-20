import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Grid, Button, Chip,
  Divider, CircularProgress, Alert, Dialog, DialogTitle,
  DialogContent, DialogActions, TextField, Paper
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import NoteAddIcon from '@mui/icons-material/NoteAdd';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import ShieldIcon from '@mui/icons-material/Shield';
import PersonIcon from '@mui/icons-material/Person';
import HealingIcon from '@mui/icons-material/Healing';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import { MenuItem } from '@mui/material';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { usePurpose } from '../contexts/PurposeContext';
import { PrivacyAwareRecordView } from '../components/PrivacyAwareRecordView';

export const PatientDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { role } = useAuth();
  const { purpose } = usePurpose();

  const [patient, setPatient] = useState(null);
  const [medicalRecords, setMedicalRecords] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Edit Patient Modal State (ADMIN only)
  const [openEditModal, setOpenEditModal] = useState(false);
  const [editPatient, setEditPatient] = useState({
    first_name: '', last_name: '', dob: '', gender: 'Male',
    phone: '', email: '', address: '', insurance_provider: '',
    policy_number: '', blood_group: 'O+'
  });
  const [updatingPatient, setUpdatingPatient] = useState(false);

  // Delete Patient Modal State (ADMIN only)
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [deletingPatient, setDeletingPatient] = useState(false);

  // Add Medical Record Modal State
  const [openRecordModal, setOpenRecordModal] = useState(false);
  const [newRecord, setNewRecord] = useState({
    disease: '', diagnosis: '', medical_history: '', prescription: '',
    lab_reports: '', doctor_notes: '', insurance_details: '',
    treatment_plan: '', allergies: '', vitals: ''
  });
  const [savingRecord, setSavingRecord] = useState(false);

  const fetchPatientData = async () => {
    setLoading(true);
    setError('');
    try {
      const patientRes = await api.get(`/patients/${id}`);
      if (patientRes.data?.status === 'success') {
        setPatient(patientRes.data.data);
      }

      if (role !== 'ADMIN') {
        const recordsRes = await api.get(`/medical-records/patient/${id}`);
        if (recordsRes.data?.status === 'success') {
          setMedicalRecords(recordsRes.data.data);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load patient details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatientData();
  }, [id, role]);

  const handleOpenEdit = () => {
    if (!patient) return;
    setEditPatient({
      first_name: patient.first_name || '',
      last_name: patient.last_name || '',
      dob: patient.dob === '[REDACTED_PRIVACY_POLICY]' ? '' : (patient.dob || ''),
      gender: patient.gender || 'Male',
      phone: patient.phone || '',
      email: patient.email || '',
      address: patient.address || '',
      insurance_provider: patient.insurance_provider || '',
      policy_number: patient.policy_number || '',
      blood_group: patient.blood_group || 'O+'
    });
    setOpenEditModal(true);
  };

  const handleUpdatePatient = async (e) => {
    e.preventDefault();
    setUpdatingPatient(true);
    try {
      const response = await api.put(`/patients/${id}`, editPatient);
      if (response.data?.status === 'success') {
        setOpenEditModal(false);
        fetchPatientData();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update patient record.');
    } finally {
      setUpdatingPatient(false);
    }
  };

  const handleDeletePatient = async () => {
    setDeletingPatient(true);
    try {
      const response = await api.delete(`/patients/${id}`);
      if (response.data?.status === 'success') {
        navigate('/patients');
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete patient record.');
      setDeletingPatient(false);
    }
  };

  const handleCreateMedicalRecord = async (e) => {
    e.preventDefault();
    setSavingRecord(true);
    try {
      const payload = {
        patient_public_id: id,
        ...newRecord
      };
      const response = await api.post('/medical-records', payload);
      if (response.data?.status === 'success') {
        setOpenRecordModal(false);
        setNewRecord({
          disease: '', diagnosis: '', medical_history: '', prescription: '',
          lab_reports: '', doctor_notes: '', insurance_details: '',
          treatment_plan: '', allergies: '', vitals: ''
        });
        fetchPatientData();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create medical record.');
    } finally {
      setSavingRecord(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
        <CircularProgress color="primary" />
      </Box>
    );
  }

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/patients')} color="inherit">
          Back to Directory
        </Button>
        <Box display="flex" gap={1}>
          <Chip icon={<ShieldIcon />} label={`Role Mask: ${role}`} color="secondary" />
          <Chip label={`Audit Purpose: ${purpose}`} color="primary" variant="outlined" />
        </Box>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Patient Master Demographics Banner */}
      {patient && (
        <Card variant="outlined" sx={{ mb: 3 }}>
          <CardContent>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={8}>
                <Box display="flex" alignItems="center" gap={2}>
                  <PersonIcon color="primary" sx={{ fontSize: 44 }} />
                  <Box>
                    <Typography variant="h5" fontWeight="700">
                      {patient.first_name} {patient.last_name}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Patient ID: #{patient.public_id} • Registered {new Date(patient.created_at).toLocaleDateString()}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4} display="flex" justifyContent="flex-end" gap={1}>
                {role === 'ADMIN' && (
                  <>
                    <Button
                      variant="outlined"
                      color="primary"
                      startIcon={<EditIcon />}
                      onClick={handleOpenEdit}
                    >
                      Edit Demographics
                    </Button>
                    <Button
                      variant="outlined"
                      color="error"
                      startIcon={<DeleteIcon />}
                      onClick={() => setOpenDeleteModal(true)}
                    >
                      Delete
                    </Button>
                  </>
                )}
                {role === 'DOCTOR' && (
                  <Button
                    variant="contained"
                    color="primary"
                    startIcon={<NoteAddIcon />}
                    onClick={() => setOpenRecordModal(true)}
                  >
                    Add Medical Record
                  </Button>
                )}
              </Grid>
            </Grid>

            <Divider sx={{ my: 2 }} />

            <Grid container spacing={2}>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">DATE OF BIRTH</Typography>
                <Typography variant="body2">{patient.dob || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">GENDER</Typography>
                <Typography variant="body2">{patient.gender || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">PHONE CONTACT</Typography>
                <Typography variant="body2">{patient.phone || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">BLOOD GROUP</Typography>
                <Chip label={patient.blood_group || 'N/A'} size="small" color="primary" variant="outlined" />
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Restricted Insurance Claim Information Section for INSURANCE_OFFICER */}
      {role === 'INSURANCE_OFFICER' && (
        <Box mt={4}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <ReceiptLongIcon color="primary" />
            <Typography variant="h6" fontWeight="700">
              Insurance Claim Information
            </Typography>
          </Box>

          {medicalRecords.length === 0 ? (
            <Card variant="outlined" sx={{ p: 3 }}>
              <Typography variant="subtitle2" fontWeight="700" color="primary" gutterBottom>
                INSURANCE CLAIM CONTEXT SUMMARY
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} sm={4}>
                  <Typography variant="caption" color="text.secondary" fontWeight="700">DIAGNOSIS</Typography>
                  <Typography variant="body2">Not available</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="caption" color="text.secondary" fontWeight="700">PROCEDURE / TREATMENT</Typography>
                  <Typography variant="body2">Not available</Typography>
                </Grid>
                <Grid item xs={12} sm={4}>
                  <Typography variant="caption" color="text.secondary" fontWeight="700">HOSPITALIZATION DURATION</Typography>
                  <Typography variant="body2">0 days</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'action.hover', borderColor: 'warning.light' }}>
                    <Typography variant="caption" color="text.secondary" fontWeight="700">PRIVATE CLINICAL NOTES</Typography>
                    <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                      <Chip label="REDACTED BY PRIVACY POLICY" color="warning" size="small" variant="outlined" />
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Card>
          ) : (
            medicalRecords.map((record) => (
              <Card key={record.public_id} variant="outlined" sx={{ mb: 2, p: 1 }}>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                    <Typography variant="subtitle1" fontWeight="700" color="primary">
                      Insurance Claim Context (#{record.public_id?.substring(0, 8)})
                    </Typography>
                    <Chip label="Audit Purpose: BILLING" color="secondary" size="small" variant="outlined" />
                  </Box>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" color="text.secondary" fontWeight="700">DIAGNOSIS</Typography>
                      <Typography variant="body2" fontWeight="600">{record.disease || 'Standard Consultation'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" color="text.secondary" fontWeight="700">PROCEDURE / TREATMENT</Typography>
                      <Typography variant="body2">{record.treatment_plan || 'Outpatient Treatment'}</Typography>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Typography variant="caption" color="text.secondary" fontWeight="700">HOSPITALIZATION DURATION</Typography>
                      <Typography variant="body2">0 days</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Typography variant="caption" color="text.secondary" fontWeight="700">TESTS / SERVICES</Typography>
                      <Typography variant="body2">Routine Clinical Evaluation</Typography>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <Paper variant="outlined" sx={{ p: 1.5, bgcolor: 'action.hover', borderColor: 'warning.light' }}>
                        <Typography variant="caption" color="text.secondary" fontWeight="700">PRIVATE CLINICAL NOTES</Typography>
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          <Chip label="REDACTED BY PRIVACY POLICY" color="warning" size="small" variant="outlined" />
                        </Box>
                      </Paper>
                    </Grid>
                  </Grid>
                </CardContent>
              </Card>
            ))
          )}
        </Box>
      )}

      {/* Clinical Medical History Timeline (Forbidden for ADMIN & INSURANCE_OFFICER) */}
      {role !== 'ADMIN' && role !== 'INSURANCE_OFFICER' && (
        <Box mt={4}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <HealingIcon color="primary" />
            <Typography variant="h6" fontWeight="700">
              Encrypted Clinical Medical Records Timeline ({medicalRecords.length})
            </Typography>
          </Box>

          {medicalRecords.length === 0 ? (
            <Alert severity="info">No medical records on file for this patient.</Alert>
          ) : (
            medicalRecords.map((record) => (
              <PrivacyAwareRecordView key={record.public_id} record={record} />
            ))
          )}
        </Box>
      )}

      {/* Edit Patient Modal Dialog (ADMIN only) */}
      <Dialog open={openEditModal} onClose={() => setOpenEditModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight="700">Edit Encrypted Patient Record</DialogTitle>
        <Box component="form" onSubmit={handleUpdatePatient}>
          <DialogContent dividers>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField label="First Name" fullWidth required value={editPatient.first_name} onChange={(e) => setEditPatient({ ...editPatient, first_name: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Last Name" fullWidth required value={editPatient.last_name} onChange={(e) => setEditPatient({ ...editPatient, last_name: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Date of Birth" type="date" fullWidth InputLabelProps={{ shrink: true }} value={editPatient.dob} onChange={(e) => setEditPatient({ ...editPatient, dob: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField select label="Gender" fullWidth value={editPatient.gender} onChange={(e) => setEditPatient({ ...editPatient, gender: e.target.value })}>
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField label="Phone Number" fullWidth value={editPatient.phone} onChange={(e) => setEditPatient({ ...editPatient, phone: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Email Address" type="email" fullWidth value={editPatient.email} onChange={(e) => setEditPatient({ ...editPatient, email: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Home Address" fullWidth multiline rows={2} value={editPatient.address} onChange={(e) => setEditPatient({ ...editPatient, address: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Insurance Provider" fullWidth value={editPatient.insurance_provider} onChange={(e) => setEditPatient({ ...editPatient, insurance_provider: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Policy Number" fullWidth value={editPatient.policy_number} onChange={(e) => setEditPatient({ ...editPatient, policy_number: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField select label="Blood Group" fullWidth value={editPatient.blood_group} onChange={(e) => setEditPatient({ ...editPatient, blood_group: e.target.value })}>
                  <MenuItem value="A+">A+</MenuItem>
                  <MenuItem value="A-">A-</MenuItem>
                  <MenuItem value="B+">B+</MenuItem>
                  <MenuItem value="B-">B-</MenuItem>
                  <MenuItem value="O+">O+</MenuItem>
                  <MenuItem value="O-">O-</MenuItem>
                  <MenuItem value="AB+">AB+</MenuItem>
                  <MenuItem value="AB-">AB-</MenuItem>
                </TextField>
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, py: 2 }}>
            <Button onClick={() => setOpenEditModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" disabled={updatingPatient}>
              {updatingPatient ? 'Re-encrypting & Updating...' : 'Update Record'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      {/* Delete Patient Confirmation Dialog (ADMIN only) */}
      <Dialog open={openDeleteModal} onClose={() => setOpenDeleteModal(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="700">Delete Patient Record</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2">
            Are you sure you want to delete patient <strong>{patient?.first_name} {patient?.last_name}</strong>?
          </Typography>
          <Typography variant="caption" color="error" display="block" sx={{ mt: 1 }}>
            This action will remove all associated cryptographic search indices from the master index.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenDeleteModal(false)} color="inherit">Cancel</Button>
          <Button onClick={handleDeletePatient} color="error" variant="contained" disabled={deletingPatient}>
            {deletingPatient ? 'Deleting...' : 'Delete Record'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Add Record Modal Dialog */}
      <Dialog open={openRecordModal} onClose={() => setOpenRecordModal(false)} maxWidth="md" fullWidth>
        <DialogTitle fontWeight="700">Create Encrypted Medical Record (AES-256)</DialogTitle>
        <Box component="form" onSubmit={handleCreateMedicalRecord}>
          <DialogContent dividers>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField label="Disease / Condition Name" fullWidth required value={newRecord.disease} onChange={(e) => setNewRecord({ ...newRecord, disease: e.target.value })} placeholder="e.g. Type 2 Diabetes Mellitus" />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Blood Pressure / Vitals" fullWidth value={newRecord.vitals} onChange={(e) => setNewRecord({ ...newRecord, vitals: e.target.value })} placeholder="e.g. BP 120/80 mmHg, HR 72 bpm" />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Clinical Diagnosis" fullWidth multiline rows={2} value={newRecord.diagnosis} onChange={(e) => setNewRecord({ ...newRecord, diagnosis: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Prescribed Medications" fullWidth multiline rows={2} value={newRecord.prescription} onChange={(e) => setNewRecord({ ...newRecord, prescription: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Allergies" fullWidth value={newRecord.allergies} onChange={(e) => setNewRecord({ ...newRecord, allergies: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Treatment Plan" fullWidth multiline rows={2} value={newRecord.treatment_plan} onChange={(e) => setNewRecord({ ...newRecord, treatment_plan: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Doctor Confidential Notes" fullWidth multiline rows={2} value={newRecord.doctor_notes} onChange={(e) => setNewRecord({ ...newRecord, doctor_notes: e.target.value })} />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions sx={{ px: 3, py: 2 }}>
            <Button onClick={() => setOpenRecordModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" disabled={savingRecord}>
              {savingRecord ? 'Encrypting & Indexing...' : 'Save & Encrypt Record'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>
    </Box>
  );
};
