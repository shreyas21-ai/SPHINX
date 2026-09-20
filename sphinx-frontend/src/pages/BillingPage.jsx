import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, Button, TextField,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  IconButton, Chip, Divider, Alert, CircularProgress, Paper, MenuItem
} from '@mui/material';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import AddCircleIcon from '@mui/icons-material/AddCircle';
import DeleteIcon from '@mui/icons-material/Delete';
import CalculateIcon from '@mui/icons-material/Calculate';
import ShieldIcon from '@mui/icons-material/Shield';
import PersonIcon from '@mui/icons-material/Person';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { usePurpose } from '../contexts/PurposeContext';

const DEFAULT_ITEMS = [
  { item_name: 'Consultation', quantity: 1, unit_price: 500 },
  { item_name: 'Lab tests', quantity: 1, unit_price: 800 },
  { item_name: 'Room', quantity: 1, unit_price: 2000 },
  { item_name: 'Medicines', quantity: 1, unit_price: 700 },
  { item_name: 'Treatment', quantity: 1, unit_price: 6000 }
];

export const BillingPage = () => {
  const { role } = useAuth();
  const { purpose } = usePurpose();

  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState('');
  const [patientDetails, setPatientDetails] = useState(null);
  const [clinicalRecord, setClinicalRecord] = useState(null);
  const [billingHistory, setBillingHistory] = useState([]);
  const [loadingPatients, setLoadingPatients] = useState(true);

  // Billing Itemizer State
  const [items, setItems] = useState(DEFAULT_ITEMS);
  const [approvedAmount, setApprovedAmount] = useState(8000);
  const [claimNotes, setClaimNotes] = useState('');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const fetchPatients = async () => {
    setLoadingPatients(true);
    try {
      const res = await api.get('/patients');
      if (res.data?.status === 'success') {
        setPatients(res.data.data);
        if (res.data.data.length > 0) {
          setSelectedPatientId(res.data.data[0].public_id);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to fetch patients.');
    } finally {
      setLoadingPatients(false);
    }
  };

  const fetchPatientBillingData = async (patientPublicId) => {
    if (!patientPublicId) return;
    setError('');
    setSuccess('');
    try {
      // 1. Fetch Patient Demographics & Insurance info
      const patRes = await api.get(`/patients/${patientPublicId}`);
      if (patRes.data?.status === 'success') {
        setPatientDetails(patRes.data.data);
      }

      // 2. Fetch Patient Medical Records for claim context (diagnosis & treatment procedure)
      try {
        const medRes = await api.get(`/medical-records/patient/${patientPublicId}`);
        if (medRes.data?.status === 'success' && medRes.data.data.length > 0) {
          setClinicalRecord(medRes.data.data[0]);
        } else {
          setClinicalRecord(null);
        }
      } catch {
        setClinicalRecord(null);
      }

      // 3. Fetch Billing History
      const billRes = await api.get(`/billing/patient/${patientPublicId}`);
      if (billRes.data?.status === 'success') {
        setBillingHistory(billRes.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load patient claim data.');
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  useEffect(() => {
    if (selectedPatientId) {
      fetchPatientBillingData(selectedPatientId);
    }
  }, [selectedPatientId]);

  // Billing Math Calculations
  const handleItemChange = (index, field, value) => {
    const updated = [...items];
    updated[index][field] = field === 'item_name' ? value : Math.max(0, Number(value));
    setItems(updated);
  };

  const handleAddItem = () => {
    setItems([...items, { item_name: '', quantity: 1, unit_price: 0 }]);
  };

  const handleRemoveItem = (index) => {
    setItems(items.filter((_, i) => i !== index));
  };

  const calculateTotalBill = () => {
    return items.reduce((sum, item) => sum + (Number(item.quantity || 0) * Number(item.unit_price || 0)), 0);
  };

  const totalBill = calculateTotalBill();
  const patientPayable = Math.max(0, totalBill - Number(approvedAmount || 0));

  const handleSaveClaim = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');
    try {
      const payload = {
        patient_public_id: selectedPatientId,
        items: items,
        approved_amount: Number(approvedAmount),
        insurance_provider: patientDetails?.insurance_provider || 'Direct Insurance',
        policy_number: patientDetails?.policy_number || 'POL-GENERAL',
        claim_notes: claimNotes
      };

      const res = await api.post('/billing', payload);
      if (res.data?.status === 'success') {
        setSuccess('Billing statement and insurance claim processed and saved!');
        fetchPatientBillingData(selectedPatientId);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save billing statement.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <ReceiptLongIcon color="primary" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h4" fontWeight="700">
              Insurance Claims & Hospital Billing Engine
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Calculate Total Bill • Determine Insurance Coverage • Calculate Patient Payable Amount ({role})
            </Typography>
          </Box>
        </Box>
        <Chip icon={<ShieldIcon />} label={`Audit Purpose: ${purpose}`} color="secondary" />
      </Box>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      {success && <Alert severity="success" sx={{ mb: 3 }}>{success}</Alert>}

      {/* Patient Selector */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={6}>
              <TextField
                select
                fullWidth
                label="Select Patient for Billing / Claim Statement"
                value={selectedPatientId}
                onChange={(e) => setSelectedPatientId(e.target.value)}
                disabled={loadingPatients}
              >
                {patients.map((p) => (
                  <MenuItem key={p.public_id} value={p.public_id}>
                    {p.first_name} {p.last_name} (#{p.public_id.substring(0, 8)}) - {p.insurance_provider || 'No Insurance'}
                  </MenuItem>
                ))}
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6} display="flex" justifyContent="flex-end">
              {patientDetails && (
                <Box display="flex" gap={1}>
                  <Chip label={`Provider: ${patientDetails.insurance_provider || 'N/A'}`} color="primary" variant="outlined" />
                  <Chip label={`Policy #: ${patientDetails.policy_number || 'N/A'}`} color="secondary" variant="outlined" />
                </Box>
              )}
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Patient Insurance & Claim-Relevant Clinical Context Banner */}
      {patientDetails && (
        <Card variant="outlined" sx={{ mb: 3, bgcolor: 'action.hover' }}>
          <CardContent>
            <Typography variant="subtitle2" fontWeight="700" color="primary" gutterBottom>
              PATIENT CLAIM CONTEXT SUMMARY
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">PATIENT NAME</Typography>
                <Typography variant="body2" fontWeight="600">{patientDetails.first_name} {patientDetails.last_name}</Typography>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">INSURANCE PROVIDER</Typography>
                <Typography variant="body2">{patientDetails.insurance_provider || 'N/A'}</Typography>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">DIAGNOSIS (CLAIM RELEVANT)</Typography>
                <Typography variant="body2">{clinicalRecord?.disease || 'Standard Consultation / Checkup'}</Typography>
              </Grid>
              <Grid item xs={12} sm={3}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">PROCEDURE / TREATMENT</Typography>
                <Typography variant="body2">{clinicalRecord?.treatment_plan || 'Outpatient Treatment'}</Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Interactive Billing Calculation Workbench */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card variant="outlined">
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6" fontWeight="700">
                  Itemized Hospital Charges & Services
                </Typography>
                <Button startIcon={<AddCircleIcon />} onClick={handleAddItem} size="small" variant="outlined">
                  Add Item
                </Button>
              </Box>
              <Divider sx={{ mb: 2 }} />

              <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                <Table size="small">
                  <TableHead sx={{ bgcolor: 'action.hover' }}>
                    <TableRow>
                      <TableCell fontWeight="700">Service / Item Description</TableCell>
                      <TableCell fontWeight="700" width="100">Quantity</TableCell>
                      <TableCell fontWeight="700" width="130">Unit Price (₹)</TableCell>
                      <TableCell align="right" fontWeight="700" width="130">Item Amount (₹)</TableCell>
                      <TableCell width="60" align="center">Action</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {items.map((item, index) => {
                      const itemAmount = Number(item.quantity || 0) * Number(item.unit_price || 0);
                      return (
                        <TableRow key={index}>
                          <TableCell>
                            <TextField
                              size="small"
                              fullWidth
                              value={item.item_name}
                              onChange={(e) => handleItemChange(index, 'item_name', e.target.value)}
                              placeholder="e.g. Room charges, Lab test..."
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              type="number"
                              value={item.quantity}
                              onChange={(e) => handleItemChange(index, 'quantity', e.target.value)}
                              inputProps={{ min: 1 }}
                            />
                          </TableCell>
                          <TableCell>
                            <TextField
                              size="small"
                              type="number"
                              value={item.unit_price}
                              onChange={(e) => handleItemChange(index, 'unit_price', e.target.value)}
                              inputProps={{ min: 0 }}
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight="700">
                              ₹{itemAmount.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <IconButton size="small" color="error" onClick={() => handleRemoveItem(index)}>
                              <DeleteIcon fontSize="small" />
                            </IconButton>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>

              <TextField
                fullWidth
                multiline
                rows={2}
                label="Claim Notes / Remarks"
                value={claimNotes}
                onChange={(e) => setClaimNotes(e.target.value)}
                placeholder="Optional notes regarding claim evaluation..."
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Total & Final Payable Calculator Card */}
        <Grid item xs={12} md={4}>
          <Card variant="outlined" sx={{ bgcolor: 'primary.50' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="700" gutterBottom display="flex" alignItems="center" gap={1}>
                <CalculateIcon color="primary" /> Billing & Claim Summary
              </Typography>
              <Divider sx={{ my: 2 }} />

              <Box display="flex" justifyContent="space-between" mb={1.5}>
                <Typography variant="body2" color="text.secondary">TOTAL HOSPITAL BILL:</Typography>
                <Typography variant="h6" fontWeight="700">₹{totalBill.toLocaleString()}</Typography>
              </Box>

              <Box mb={2}>
                <Typography variant="caption" color="text.secondary" fontWeight="700" display="block" mb={0.5}>
                  APPROVED INSURANCE COVERAGE (₹):
                </Typography>
                <TextField
                  fullWidth
                  type="number"
                  size="small"
                  value={approvedAmount}
                  onChange={(e) => setApprovedAmount(Math.max(0, Number(e.target.value)))}
                  inputProps={{ min: 0 }}
                />
              </Box>

              <Divider sx={{ my: 2 }} />

              <Paper variant="outlined" sx={{ p: 2, bgcolor: 'background.paper', borderColor: 'primary.main' }}>
                <Typography variant="caption" color="text.secondary" fontWeight="700">
                  FINAL PATIENT PAYABLE AMOUNT:
                </Typography>
                <Typography variant="h4" fontWeight="800" color="primary">
                  ₹{patientPayable.toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary" display="block">
                  Calculation: ₹{totalBill.toLocaleString()} (Total) - ₹{Number(approvedAmount).toLocaleString()} (Approved) = ₹{patientPayable.toLocaleString()}
                </Typography>
              </Paper>

              <Button
                fullWidth
                variant="contained"
                color="primary"
                size="large"
                sx={{ mt: 3, py: 1.5, fontWeight: '700' }}
                onClick={handleSaveClaim}
                disabled={saving || items.length === 0}
              >
                {saving ? 'Processing Claim...' : 'Save & Record Insurance Claim'}
              </Button>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Generated Billing Statements History */}
      <Box mt={4}>
        <Typography variant="h6" fontWeight="700" mb={2}>
          Generated Billing & Claim Statements History ({billingHistory.length})
        </Typography>

        {billingHistory.length === 0 ? (
          <Alert severity="info">No billing statements generated yet for this patient.</Alert>
        ) : (
          billingHistory.map((statement) => (
            <Card key={statement.public_id} variant="outlined" sx={{ mb: 2 }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                  <Typography variant="subtitle1" fontWeight="700">
                    Statement #{statement.public_id.substring(0, 8)}
                  </Typography>
                  <Chip label={statement.claim_status} color="success" size="small" />
                </Box>
                <Typography variant="caption" color="text.secondary" display="block" mb={2}>
                  Generated on {new Date(statement.created_at).toLocaleString()} • Policy #{statement.policy_number} ({statement.insurance_provider})
                </Typography>

                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">TOTAL BILL</Typography>
                    <Typography variant="subtitle2" fontWeight="700">₹{statement.total_bill?.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">INSURANCE COVERED</Typography>
                    <Typography variant="subtitle2" fontWeight="700" color="success.main">₹{statement.approved_amount?.toLocaleString()}</Typography>
                  </Grid>
                  <Grid item xs={4}>
                    <Typography variant="caption" color="text.secondary">PATIENT PAYABLE</Typography>
                    <Typography variant="subtitle2" fontWeight="700" color="primary.main">₹{statement.patient_payable?.toLocaleString()}</Typography>
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          ))
        )}
      </Box>
    </Box>
  );
};
