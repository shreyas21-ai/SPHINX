import React from 'react';
import {
  Card, CardContent, Typography, Grid, Chip, Box, Divider, Paper
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import HealingIcon from '@mui/icons-material/Healing';
import AssignmentIcon from '@mui/icons-material/Assignment';
import MedicationIcon from '@mui/icons-material/Medication';
import NoteAltIcon from '@mui/icons-material/NoteAlt';
import ReceiptLongIcon from '@mui/icons-material/ReceiptLong';
import ShieldIcon from '@mui/icons-material/Shield';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import { useAuth } from '../contexts/AuthContext';

const REDACTED_STRING = "[REDACTED_PRIVACY_POLICY]";

const FieldCard = ({ title, value, icon, fullWidth = false }) => {
  const isRedacted = value === REDACTED_STRING;

  return (
    <Grid item xs={12} sm={fullWidth ? 12 : 6} md={fullWidth ? 12 : 4}>
      <Paper
        variant="outlined"
        sx={{
          p: 2,
          height: '100%',
          bgcolor: isRedacted ? 'action.hover' : 'background.paper',
          borderColor: isRedacted ? 'warning.light' : 'divider',
          position: 'relative'
        }}
      >
        <Box display="flex" alignItems="center" gap={1} mb={1}>
          {icon}
          <Typography variant="caption" color="text.secondary" fontWeight="700" textTransform="uppercase">
            {title}
          </Typography>
        </Box>
        {isRedacted ? (
          <Chip
            icon={<LockIcon fontSize="small" />}
            label="Redacted by Privacy Policy"
            color="warning"
            size="small"
            variant="outlined"
          />
        ) : (
          <Typography variant="body1" fontWeight="500" sx={{ whiteSpace: 'pre-line' }}>
            {value || 'None'}
          </Typography>
        )}
      </Paper>
    </Grid>
  );
};

export const PrivacyAwareRecordView = ({ record }) => {
  const { role } = useAuth();

  if (!record) return null;

  return (
    <Card variant="outlined" sx={{ mb: 3 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            <HealingIcon color="primary" />
            <Typography variant="h6" fontWeight="700">
              Clinical Medical Record #{record.public_id?.substring(0, 8)}
            </Typography>
          </Box>
          <Box display="flex" gap={1}>
            <Chip
              icon={<ShieldIcon />}
              label={`Privacy Mask Mode: ${role}`}
              color="secondary"
              size="small"
            />
            <Chip
              label={new Date(record.created_at).toLocaleDateString()}
              variant="outlined"
              size="small"
            />
          </Box>
        </Box>

        <Divider sx={{ mb: 2.5 }} />

        <Grid container spacing={2}>
          <FieldCard
            title="Primary Disease"
            value={record.disease}
            icon={<HealingIcon color="error" />}
          />
          <FieldCard
            title="Diagnosis"
            value={record.diagnosis}
            icon={<AssignmentIcon color="primary" />}
          />
          <FieldCard
            title="Vitals"
            value={record.vitals}
            icon={<MonitorHeartIcon color="success" />}
          />
          <FieldCard
            title="Prescriptions & Medicines"
            value={record.prescription}
            icon={<MedicationIcon color="info" />}
          />
          <FieldCard
            title="Allergies"
            value={record.allergies}
            icon={<ShieldIcon color="warning" />}
          />
          <FieldCard
            title="Insurance Details"
            value={record.insurance_details}
            icon={<ReceiptLongIcon color="secondary" />}
          />
          <FieldCard
            title="Treatment Plan"
            value={record.treatment_plan}
            icon={<AssignmentIcon color="primary" />}
            fullWidth
          />
          <FieldCard
            title="Doctor Clinical Notes"
            value={record.doctor_notes}
            icon={<NoteAltIcon color="action" />}
            fullWidth
          />
        </Grid>
      </CardContent>
    </Card>
  );
};
