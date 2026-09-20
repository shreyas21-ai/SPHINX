import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, TablePagination, TextField,
  MenuItem, Button, Chip, CircularProgress, Alert, Grid, Paper
} from '@mui/material';
import SecurityIcon from '@mui/icons-material/Security';
import DownloadIcon from '@mui/icons-material/Download';
import FilterListIcon from '@mui/icons-material/FilterList';
import api from '../services/api';

export const AuditLogsPage = () => {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [roleFilter, setRoleFilter] = useState('ALL');
  const [purposeFilter, setPurposeFilter] = useState('ALL');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);

  const fetchAuditLogs = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.get('/audit/logs');
      if (response.data?.status === 'success') {
        setLogs(response.data.data);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAuditLogs();
  }, []);

  const filteredLogs = logs.filter((log) => {
    if (roleFilter !== 'ALL' && log.user_role !== roleFilter) return false;
    if (purposeFilter !== 'ALL' && log.purpose !== purposeFilter) return false;
    return true;
  });

  const exportToCSV = () => {
    if (logs.length === 0) return;
    const headers = ["ID", "Timestamp", "User / Performed By", "User Role", "Action", "Purpose", "Patient ID", "IP Address", "User Agent"];
    const rows = logs.map(l => [
      l.id, l.timestamp, `"${l.user_name || ''}"`, l.user_role, l.action, l.purpose, l.patient_id || 'N/A', l.ip_address, `"${l.user_agent}"`
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `SPHINX_Audit_Trail_${new Date().toISOString().substring(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Box display="flex" alignItems="center" gap={1.5}>
          <SecurityIcon color="warning" sx={{ fontSize: 36 }} />
          <Box>
            <Typography variant="h4" fontWeight="700">
              HIPAA Access Audit Trail
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Immutable logging of record accesses, purpose declarations, and caller telemetry
            </Typography>
          </Box>
        </Box>
        <Button
          variant="contained"
          color="secondary"
          startIcon={<DownloadIcon />}
          onClick={exportToCSV}
        >
          Export CSV Log
        </Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {/* Filter Card */}
      <Card variant="outlined" sx={{ mb: 3 }}>
        <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} sm={4}>
              <TextField
                select
                size="small"
                label="Filter by Role"
                fullWidth
                value={roleFilter}
                onChange={(e) => setRoleFilter(e.target.value)}
              >
                <MenuItem value="ALL">All Roles</MenuItem>
                <MenuItem value="ADMIN">ADMIN</MenuItem>
                <MenuItem value="DOCTOR">DOCTOR</MenuItem>
                <MenuItem value="NURSE">NURSE</MenuItem>
                <MenuItem value="RECEPTIONIST">RECEPTIONIST</MenuItem>
                <MenuItem value="INSURANCE_OFFICER">INSURANCE_OFFICER</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4}>
              <TextField
                select
                size="small"
                label="Filter by Purpose"
                fullWidth
                value={purposeFilter}
                onChange={(e) => setPurposeFilter(e.target.value)}
              >
                <MenuItem value="ALL">All Purposes</MenuItem>
                <MenuItem value="TREATMENT">TREATMENT</MenuItem>
                <MenuItem value="BILLING">BILLING</MenuItem>
                <MenuItem value="RESEARCH">RESEARCH</MenuItem>
                <MenuItem value="EMERGENCY">EMERGENCY</MenuItem>
                <MenuItem value="ADMINISTRATIVE">ADMINISTRATIVE</MenuItem>
              </TextField>
            </Grid>

            <Grid item xs={12} sm={4} display="flex" justifyContent="flex-end">
              <Chip
                icon={<FilterListIcon />}
                label={`Total Events: ${filteredLogs.length}`}
                color="primary"
                variant="outlined"
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Audit Log Table */}
      <TableContainer component={Card} variant="outlined">
        <Table>
          <TableHead sx={{ bgcolor: 'action.hover' }}>
            <TableRow>
              <TableCell fontWeight="700">Log ID</TableCell>
              <TableCell fontWeight="700">Timestamp</TableCell>
              <TableCell fontWeight="700">User / Performed By</TableCell>
              <TableCell fontWeight="700">Caller Role</TableCell>
              <TableCell fontWeight="700">Operation Action</TableCell>
              <TableCell fontWeight="700">Declared Purpose</TableCell>
              <TableCell fontWeight="700">IP Address</TableCell>
              <TableCell fontWeight="700">Target Patient</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <CircularProgress size={32} />
                </TableCell>
              </TableRow>
            ) : filteredLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center" sx={{ py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    No audit log records found.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              filteredLogs
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((log) => (
                  <TableRow key={log.id} hover>
                    <TableCell fontFamily="monospace" fontWeight="700">#{log.id}</TableCell>
                    <TableCell>{new Date(log.timestamp).toLocaleString()}</TableCell>
                    <TableCell fontWeight="600">{log.user_name || (log.user_id ? `User #${log.user_id}` : 'System')}</TableCell>
                    <TableCell>
                      <Chip label={log.user_role} size="small" color="primary" variant="outlined" />
                    </TableCell>
                    <TableCell fontWeight="600">{log.action}</TableCell>
                    <TableCell>
                      <Chip
                        label={log.purpose}
                        size="small"
                        color={log.purpose === 'EMERGENCY' ? 'error' : log.purpose === 'BILLING' ? 'secondary' : 'info'}
                      />
                    </TableCell>
                    <TableCell fontFamily="monospace">{log.ip_address || '127.0.0.1'}</TableCell>
                    <TableCell>{log.patient_id ? `#PAT-${log.patient_id}` : 'Global'}</TableCell>
                  </TableRow>
                ))
            )}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[10, 25, 50]}
          component="div"
          count={filteredLogs.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={(e, newPage) => setPage(newPage)}
          onRowsPerPageChange={(e) => {
            setRowsPerPage(parseInt(e.target.value, 10));
            setPage(0);
          }}
        />
      </TableContainer>
    </Box>
  );
};
