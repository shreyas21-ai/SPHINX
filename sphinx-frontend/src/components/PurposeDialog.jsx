import React, { useState } from 'react';
import {
  Dialog, DialogTitle, DialogContent, DialogActions,
  Button, Typography, RadioGroup, FormControlLabel, Radio,
  Box, Alert, Chip, Divider
} from '@mui/material';
import LockIcon from '@mui/icons-material/Lock';
import LocalHospitalIcon from '@mui/icons-material/LocalHospital';
import ReceiptIcon from '@mui/icons-material/Receipt';
import ScienceIcon from '@mui/icons-material/Science';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import AssignmentIndIcon from '@mui/icons-material/AssignmentInd';
import { usePurpose } from '../contexts/PurposeContext';
import { useAuth } from '../contexts/AuthContext';

const ALL_PURPOSE_OPTIONS = [
  { value: 'TREATMENT', label: 'Direct Patient Treatment', icon: <LocalHospitalIcon color="primary" />, desc: 'Diagnosis, medication administration, or active clinical procedure', roles: ['DOCTOR', 'NURSE'] },
  { value: 'BILLING', label: 'Billing & Insurance Claims', icon: <ReceiptIcon color="secondary" />, desc: 'Processing medical insurance claims, invoices, or financial audits', roles: ['INSURANCE_OFFICER'] },
  { value: 'RESEARCH', label: 'Clinical Research & Analytics', icon: <ScienceIcon color="info" />, desc: 'De-identified analytical research or clinical trial evaluation', roles: ['DOCTOR'] },
  { value: 'EMERGENCY', label: 'Emergency Trauma Care', icon: <WarningAmberIcon color="error" />, desc: 'Urgent life-saving emergency medical access', roles: ['DOCTOR', 'NURSE'] },
  { value: 'ADMINISTRATIVE', label: 'Administrative & Appointments', icon: <AssignmentIndIcon color="success" />, desc: 'Patient registration, scheduling, or basic administrative workflow', roles: ['RECEPTIONIST'] },
];

export const PurposeDialog = () => {
  const { isDialogOpen, purpose, handleConfirmPurpose, handleCloseDialog } = usePurpose();
  const { role } = useAuth();

  const availableOptions = ALL_PURPOSE_OPTIONS.filter((opt) => opt.roles.includes(role));
  const defaultOption = availableOptions[0]?.value || 'TREATMENT';

  const [selectedPurpose, setSelectedPurpose] = useState(purpose || defaultOption);

  const onConfirm = () => {
    handleConfirmPurpose(selectedPurpose);
  };

  return (
    <Dialog open={isDialogOpen} onClose={handleCloseDialog} maxWidth="xs" fullWidth>
      <DialogTitle sx={{ pb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
        <LockIcon color="primary" />
        <Typography variant="h6" component="span" fontWeight="600">
          Declare Access Purpose
        </Typography>
      </DialogTitle>
      <Divider />
      <DialogContent sx={{ pt: 2 }}>
        <Alert severity="info" sx={{ mb: 2 }}>
          HIPAA & Enterprise Compliance requires an explicit declaration of intent before record access. This action is permanently logged into Audit History.
        </Alert>

        <Typography variant="subtitle2" color="text.secondary" gutterBottom fontWeight="600">
          Select Purpose of Record Retrieval:
        </Typography>

        <RadioGroup value={selectedPurpose} onChange={(e) => setSelectedPurpose(e.target.value)}>
          {availableOptions.map((opt) => (
            <Box
              key={opt.value}
              sx={{
                border: '1px solid',
                borderColor: selectedPurpose === opt.value ? 'primary.main' : 'divider',
                borderRadius: 2,
                p: 1.5,
                mb: 1.5,
                bgcolor: selectedPurpose === opt.value ? 'action.selected' : 'background.paper',
                cursor: 'pointer',
                transition: 'all 0.2s',
                '&:hover': { borderColor: 'primary.main' }
              }}
              onClick={() => setSelectedPurpose(opt.value)}
            >
              <FormControlLabel
                value={opt.value}
                control={<Radio size="small" />}
                label={
                  <Box sx={{ ml: 0.5 }}>
                    <Box display="flex" alignItems="center" gap={1}>
                      {opt.icon}
                      <Typography variant="subtitle2" fontWeight="700">
                        {opt.label}
                      </Typography>
                    </Box>
                    <Typography variant="caption" color="text.secondary" display="block">
                      {opt.desc}
                    </Typography>
                  </Box>
                }
              />
            </Box>
          ))}
        </RadioGroup>
      </DialogContent>
      <DialogActions sx={{ px: 3, pb: 2 }}>
        <Button onClick={handleCloseDialog} color="inherit">
          Cancel
        </Button>
        <Button onClick={onConfirm} variant="contained" color="primary" startIcon={<LockIcon />}>
          Confirm & Proceed
        </Button>
      </DialogActions>
    </Dialog>
  );
};
