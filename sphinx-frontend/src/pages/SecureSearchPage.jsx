import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, TextField, Button, MenuItem,
  Grid, Chip, Alert, CircularProgress, Divider, Paper
} from '@mui/material';
import LockSearchIcon from '@mui/icons-material/ManageSearch';
import KeyIcon from '@mui/icons-material/Key';
import SpeedIcon from '@mui/icons-material/Speed';
import HistoryIcon from '@mui/icons-material/History';
import ShieldIcon from '@mui/icons-material/Shield';
import PersonIcon from '@mui/icons-material/Person';
import api from '../services/api';
import { usePurpose } from '../contexts/PurposeContext';
import { PrivacyAwareRecordView } from '../components/PrivacyAwareRecordView';

export const SecureSearchPage = () => {
  const navigate = useNavigate();
  const { purpose, requirePurposeConfirmation } = usePurpose();

  const [query, setQuery] = useState('');
  const [fieldName, setFieldName] = useState('disease');
  const [searchType, setSearchType] = useState('SUBSTRING');
  const [bloodGroup, setBloodGroup] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const [searchHistory, setSearchHistory] = useState([
    { query: 'Diab', field: 'disease', type: 'SUBSTRING' },
    { query: 'Rav', field: 'name', type: 'SUBSTRING' },
    { query: 'Diabetes', field: 'disease', type: 'EXACT' },
  ]);

  const executeSearch = async () => {
    setError('');
    setLoading(true);

    try {
      const payload = {
        query: query.trim(),
        field_name: fieldName,
        search_type: searchType,
        blood_group: bloodGroup,
        purpose: purpose || 'TREATMENT'
      };

      const response = await api.post('/search', payload);
      if (response.data?.status === 'success') {
        setResults(response.data.data);

        // Add to search history
        if (query.trim()) {
          setSearchHistory((prev) => [
            { query: query.trim(), field: fieldName, type: searchType },
            ...prev.filter(h => h.query !== query.trim()).slice(0, 4)
          ]);
        }
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Cryptographic search failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    requirePurposeConfirmation(() => {
      executeSearch();
    });
  };

  const handleViewPatient = (public_id) => {
    requirePurposeConfirmation(() => {
      navigate(`/patients/${public_id}`);
    });
  };

  const applyHistoryItem = (item) => {
    setQuery(item.query);
    setFieldName(item.field);
    setSearchType(item.type);
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={3}>
        <LockSearchIcon color="primary" sx={{ fontSize: 36 }} />
        <Box>
          <Typography variant="h4" fontWeight="700">
            Cryptographic Searchable Index Console
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Search sensitive medical data over HMAC blind tokens without full-database decryption
          </Typography>
        </Box>
      </Box>

      {/* Search Input Controls Card */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent>
          <Box component="form" onSubmit={handleSearchSubmit}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <TextField
                  label="Search Query Term"
                  fullWidth
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="e.g. Diab, Diabetes, Rav, Penicillin"
                />
              </Grid>

              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  label="Target Field"
                  fullWidth
                  value={fieldName}
                  onChange={(e) => setFieldName(e.target.value)}
                >
                  <MenuItem value="disease">Disease / Condition</MenuItem>
                  <MenuItem value="diagnosis">Clinical Diagnosis</MenuItem>
                  <MenuItem value="allergies">Allergies</MenuItem>
                  <MenuItem value="name">Patient Name</MenuItem>
                  <MenuItem value="blood_group">Blood Group</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} sm={3}>
                <TextField
                  select
                  label="Index Query Type"
                  fullWidth
                  value={searchType}
                  onChange={(e) => setSearchType(e.target.value)}
                >
                  <MenuItem value="SUBSTRING">Secure Substring (N-Gram HMAC)</MenuItem>
                  <MenuItem value="EXACT">Exact Match (Deterministic HMAC)</MenuItem>
                  <MenuItem value="MULTI_FIELD">Multi-Field Criteria</MenuItem>
                </TextField>
              </Grid>

              <Grid item xs={12} sm={2}>
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  size="large"
                  disabled={loading}
                  startIcon={loading ? <CircularProgress size={20} color="inherit" /> : <LockSearchIcon />}
                  sx={{ py: 1.8 }}
                >
                  {loading ? 'Searching...' : 'Search'}
                </Button>
              </Grid>

              {searchType === 'MULTI_FIELD' && (
                <Grid item xs={12} sm={4}>
                  <TextField
                    label="Blood Group Filter"
                    fullWidth
                    value={bloodGroup}
                    onChange={(e) => setBloodGroup(e.target.value)}
                    placeholder="e.g. O+, A-, B+"
                  />
                </Grid>
              )}
            </Grid>
          </Box>

          <Divider sx={{ my: 2 }} />

          {/* Search Suggestions & History Tags */}
          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
            <Typography variant="caption" color="text.secondary" fontWeight="700" display="flex" alignItems="center" gap={0.5}>
              <HistoryIcon fontSize="small" /> Recent Search Queries:
            </Typography>
            {searchHistory.map((item, idx) => (
              <Chip
                key={idx}
                label={`${item.field}: "${item.query}" (${item.type})`}
                size="small"
                onClick={() => applyHistoryItem(item)}
                clickable
                variant="outlined"
                color="primary"
              />
            ))}
          </Box>
        </CardContent>
      </Card>

      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}

      {/* Results Section */}
      {results && (
        <Box>
          {/* Telemetry Header Banner */}
          <Paper variant="outlined" sx={{ p: 2, mb: 3, bgcolor: 'action.hover', borderColor: 'primary.light' }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <SpeedIcon color="success" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontWeight="700">DB DECRYPTION COST</Typography>
                    <Typography variant="subtitle2" fontWeight="700" color="success.main">
                      {results.search_telemetry?.full_db_scanned ? 'FULL SCAN (WARNING)' : 'ZERO Full-DB Scans'}
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <KeyIcon color="primary" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontWeight="700">DECRYPTED MATCHES</Typography>
                    <Typography variant="subtitle2" fontWeight="700">
                      {results.total_matching_medical_records} Records • {results.total_matching_patients} Patients
                    </Typography>
                  </Box>
                </Box>
              </Grid>

              <Grid item xs={12} sm={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <ShieldIcon color="secondary" />
                  <Box>
                    <Typography variant="caption" color="text.secondary" fontWeight="700">AUDITED PURPOSE</Typography>
                    <Typography variant="subtitle2" fontWeight="700" color="secondary.main">
                      {purpose}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>
          </Paper>

          {/* Results List */}
          {results.medical_records?.length === 0 && results.patients?.length === 0 ? (
            <Alert severity="warning">No encrypted records matched the specified HMAC token query.</Alert>
          ) : (
            <Box display="flex" flexDirection="column" gap={3}>
              {/* Patient Matches */}
              {results.patients?.length > 0 && (
                <Box>
                  <Typography variant="h6" fontWeight="700" mb={2}>
                    Matching Patient Profiles ({results.patients.length})
                  </Typography>
                  <Grid container spacing={2}>
                    {results.patients.map((pat) => (
                      <Grid item xs={12} sm={6} key={pat.public_id}>
                        <Card variant="outlined" sx={{ p: 2, height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                          <Box>
                            <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                              <Box display="flex" alignItems="center" gap={1}>
                                <PersonIcon color="primary" />
                                <Typography variant="subtitle1" fontWeight="700" color="primary.main">
                                  {pat.first_name} {pat.last_name}
                                </Typography>
                              </Box>
                              <Chip label={pat.blood_group || 'Unknown'} size="small" color="primary" variant="outlined" />
                            </Box>
                            <Typography variant="caption" color="text.secondary" fontFamily="monospace" display="block" mb={1}>
                              Public ID: #{pat.public_id?.substring(0, 8)}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              DOB & Gender: {pat.dob === '[REDACTED_PRIVACY_POLICY]' ? 'Redacted' : `${pat.dob} (${pat.gender})`}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Phone: {pat.phone || 'N/A'}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Insurance: {pat.insurance_provider || 'None'}
                            </Typography>
                          </Box>
                          <Box mt={2}>
                            <Button
                              size="small"
                              variant="outlined"
                              fullWidth
                              onClick={() => handleViewPatient(pat.public_id)}
                            >
                              View Patient Profile
                            </Button>
                          </Box>
                        </Card>
                      </Grid>
                    ))}
                  </Grid>
                </Box>
              )}

              {/* Medical Record Matches */}
              {results.medical_records?.length > 0 && (
                <Box>
                  <Typography variant="h6" fontWeight="700" mb={2}>
                    Decrypted Medical Records ({results.medical_records.length})
                  </Typography>
                  {results.medical_records.map((rec) => (
                    <PrivacyAwareRecordView key={rec.public_id} record={rec} />
                  ))}
                </Box>
              )}
            </Box>
          )}
        </Box>
      )}
    </Box>
  );
};
