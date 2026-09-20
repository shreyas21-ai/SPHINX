import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Button, TextField, MenuItem, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, TablePagination,
  IconButton, Chip, Dialog, DialogTitle, DialogContent, DialogActions,
  Grid, CircularProgress, Alert, Tooltip
} from '@mui/material';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import VisibilityIcon from '@mui/icons-material/Visibility';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import LockIcon from '@mui/icons-material/Lock';
import SearchIcon from '@mui/icons-material/Search';
import ShieldIcon from '@mui/icons-material/Shield';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { usePurpose } from '../contexts/PurposeContext';

export const PatientsPage = () => {
  const navigate = useNavigate();
  const { role } = useAuth();
  const { requirePurposeConfirmation } = usePurpose();

  const [patients, setPatients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterText, setFilterText] = useState('');

  // Pagination
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  // Add Patient Modal State
  const [openAddModal, setOpenAddModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [newPatient, setNewPatient] = useState({
    first_name: '', last_name: '', dob: '', gender: 'Male',
    phone: '', email: '', address: '', insurance_provider: '',
    policy_number: '', blood_group: 'O+'
  });
  // Edit Patient Modal State (ADMIN only)
  const [openEditModal, setOpenEditModal] = useState(false);
  const [editPatient, setEditPatient] = useState({
    public_id: '', first_name: '', last_name: '', dob: '', gender: 'Male',
    phone: '', email: '', address: '', insurance_provider: '',
    policy_number: '', blood_group: 'O+'
  });
  const [updating, setUpdating] = useState(false);

  // Delete Patient Modal State (ADMIN only)
  const [openDeleteModal, setOpenDeleteModal] = useState(false);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [deleting, setDeleting] = useState(false);

  const fetchPatients = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/patients');
      if (response.data?.status === 'success') {
        setPatients(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch patients.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handleViewPatient = (public_id) => {
    requirePurposeConfirmation(() => {
      navigate(`/patients/${public_id}`);
    });
  };

  const handleCreatePatient = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      const response = await api.post('/patients', newPatient);
      if (response.data?.status === 'success') {
        setOpenAddModal(false);
        setNewPatient({
          first_name: '', last_name: '', dob: '', gender: 'Male',
          phone: '', email: '', address: '', insurance_provider: '',
          policy_number: '', blood_group: 'O+'
        });
        fetchPatients();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create patient record.');
    } finally {
      setSaving(false);
    }
  };

  const handleOpenEdit = (patient) => {
    setEditPatient({
      public_id: patient.public_id,
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
    setUpdating(true);
    try {
      const response = await api.put(`/patients/${editPatient.public_id}`, editPatient);
      if (response.data?.status === 'success') {
        setOpenEditModal(false);
        fetchPatients();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update patient record.');
    } finally {
      setUpdating(false);
    }
  };

  const handleOpenDelete = (patient) => {
    setSelectedPatient(patient);
    setOpenDeleteModal(true);
  };

  const handleDeletePatient = async () => {
    if (!selectedPatient) return;
    setDeleting(true);
    try {
      const response = await api.delete(`/patients/${selectedPatient.public_id}`);
      if (response.data?.status === 'success') {
        setOpenDeleteModal(false);
        setSelectedPatient(null);
        fetchPatients();
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete patient record.');
    } finally {
      setDeleting(false);
    }
  };

  const filteredPatients = patients.filter((p) => {
    const term = filterText.toLowerCase();
    return (
      (p.first_name || '').toLowerCase().includes(term) ||
      (p.last_name || '').toLowerCase().includes(term) ||
      (p.phone || '').toLowerCase().includes(term) ||
      (p.email || '').toLowerCase().includes(term) ||
      (p.blood_group || '').toLowerCase().includes(term)
    );
  });

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box>
          <Typography variant="h4" fontWeight="700">
            {role === 'DOCTOR' ? 'My Patients Directory' : 'Patient Directory & Master Index'}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Demographic fields encrypted with AES-256 • Role-Aware Privacy Masking ({role})
          </Typography>
        </Box>
        {['ADMIN', 'RECEPTIONIST'].includes(role) && (
          <Button
            variant="contained"
            color="primary"
            startIcon={<PersonAddIcon />}
            onClick={() => setOpenAddModal(true)}
          >
            Add New Patient
          </Button>
        )}
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Filter Bar */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                size="small"
                fullWidth
                placeholder="Filter by name, phone, email, or blood group..."
                value={filterText}
                onChange={(e) => setFilterText(e.target.value)}
                InputProps={{
                  startAdornment: <SearchIcon color="action" sx={{ mr: 1 }} />
                }}
              />
            </Grid>
            <Grid item xs={12} sm={6} display="flex" justifyContent="flex-end">
              <Chip
                icon={<ShieldIcon fontSize="small" />}
                label={`Privacy View Mode: ${role}`}
                color="secondary"
                variant="outlined"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Table Container */}
      <TableContainer component={Card} variant="outlined">
        <Table>
          <TableHead sx={{ bgcolor: 'action.hover' }}>
            <TableRow>
              <TableCell fontWeight="700">Patient Identifier</TableCell>
              <TableCell fontWeight="700">Full Name</TableCell>
              <TableCell fontWeight="700">DOB & Gender</TableCell>
              <TableCell fontWeight="700">Phone / Contact</TableCell>
              <TableCell fontWeight="700">Insurance Provider</TableCell>
              <TableCell fontWeight="700">Blood Group</TableCell>
              <TableCell align="right" fontWeight="700">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={32} />
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    Decrypting patient identities...
                  </Typography>
                </TableCell>
              </TableRow>
            ) : filteredPatients.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No patient records found.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredPatients
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((patient) => (
                  <TableRow key={patient.public_id} hover>
                    <TableCell>
                      <Typography variant="caption" fontFamily="monospace" fontWeight="700">
                        #{patient.public_id.substring(0, 8)}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" fontWeight="600">
                        {patient.first_name} {patient.last_name}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      {patient.dob === '[REDACTED_PRIVACY_POLICY]' ? (
                        <Chip label="Redacted" size="small" color="warning" variant="outlined" />
                      ) : (
                        <Typography variant="body2">{patient.dob} ({patient.gender})</Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{patient.phone || 'N/A'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">{patient.insurance_provider || 'None'}</Typography>
                    </TableCell>
                    <TableCell>
                      <Chip label={patient.blood_group || 'Unknown'} size="small" color="primary" variant="outlined" />
                    </TableCell>
                    <TableCell align="right">
                      <Box display="flex" justifyContent="flex-end" gap={1}>
                        <Tooltip title="View Patient Details (Requires Access Purpose)">
                          <Button
                            size="small"
                            variant="outlined"
                            startIcon={<VisibilityIcon />}
                            onClick={() => handleViewPatient(patient.public_id)}
                          >
                            View
                          </Button>
                        </Tooltip>
                        {role === 'ADMIN' && (
                          <>
                            <Tooltip title="Edit Patient Demographics">
                              <IconButton size="small" color="primary" onClick={() => handleOpenEdit(patient)}>
                                <EditIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete Patient Record">
                              <IconButton size="small" color="error" onClick={() => handleOpenDelete(patient)}>
                                <DeleteIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </>
                        )}
                      </Box>
                    </TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25]}
          component="div"
          count={filteredPatients.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>

      {/* Add Patient Modal Dialog */}
      <Dialog open={openAddModal} onClose={() => setOpenAddModal(false)} maxWidth="sm" fullWidth>
        <DialogTitle fontWeight="700">Add New Encrypted Patient Record</DialogTitle>
        <Box component="form" onSubmit={handleCreatePatient}>
          <DialogContent dividers>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField label="First Name" fullWidth required value={newPatient.first_name} onChange={(e) => setNewPatient({ ...newPatient, first_name: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Last Name" fullWidth required value={newPatient.last_name} onChange={(e) => setNewPatient({ ...newPatient, last_name: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Date of Birth" type="date" fullWidth InputLabelProps={{ shrink: true }} value={newPatient.dob} onChange={(e) => setNewPatient({ ...newPatient, dob: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField select label="Gender" fullWidth value={newPatient.gender} onChange={(e) => setNewPatient({ ...newPatient, gender: e.target.value })}>
                  <MenuItem value="Male">Male</MenuItem>
                  <MenuItem value="Female">Female</MenuItem>
                  <MenuItem value="Other">Other</MenuItem>
                </TextField>
              </Grid>
              <Grid item xs={6}>
                <TextField label="Phone Number" fullWidth value={newPatient.phone} onChange={(e) => setNewPatient({ ...newPatient, phone: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Email Address" type="email" fullWidth value={newPatient.email} onChange={(e) => setNewPatient({ ...newPatient, email: e.target.value })} />
              </Grid>
              <Grid item xs={12}>
                <TextField label="Home Address" fullWidth multiline rows={2} value={newPatient.address} onChange={(e) => setNewPatient({ ...newPatient, address: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Insurance Provider" fullWidth value={newPatient.insurance_provider} onChange={(e) => setNewPatient({ ...newPatient, insurance_provider: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField label="Policy Number" fullWidth value={newPatient.policy_number} onChange={(e) => setNewPatient({ ...newPatient, policy_number: e.target.value })} />
              </Grid>
              <Grid item xs={6}>
                <TextField select label="Blood Group" fullWidth value={newPatient.blood_group} onChange={(e) => setNewPatient({ ...newPatient, blood_group: e.target.value })}>
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
            <Button onClick={() => setOpenAddModal(false)} color="inherit">Cancel</Button>
            <Button type="submit" variant="contained" disabled={saving}>
              {saving ? 'Encrypting & Saving...' : 'Save & Encrypt Record'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      {/* Edit Patient Modal Dialog */}
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
            <Button type="submit" variant="contained" disabled={updating}>
              {updating ? 'Re-encrypting & Updating...' : 'Update & Re-encrypt'}
            </Button>
          </DialogActions>
        </Box>
      </Dialog>

      {/* Delete Patient Confirmation Dialog */}
      <Dialog open={openDeleteModal} onClose={() => setOpenDeleteModal(false)} maxWidth="xs" fullWidth>
        <DialogTitle fontWeight="700">Delete Patient Record</DialogTitle>
        <DialogContent dividers>
          <Typography variant="body2">
            Are you sure you want to delete patient <strong>{selectedPatient?.first_name} {selectedPatient?.last_name}</strong>?
          </Typography>
          <Typography variant="caption" color="error" display="block" sx={{ mt: 1 }}>
            This action will remove all associated cryptographic search indices from the master index.
          </Typography>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button onClick={() => setOpenDeleteModal(false)} color="inherit">Cancel</Button>
          <Button onClick={handleDeletePatient} color="error" variant="contained" disabled={deleting}>
            {deleting ? 'Deleting...' : 'Delete Record'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
