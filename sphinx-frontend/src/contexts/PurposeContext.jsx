import React, { createContext, useContext, useState } from 'react';

const PurposeContext = createContext();

export const PurposeProvider = ({ children }) => {
  const [purpose, setPurpose] = useState(() => localStorage.getItem('sphinx_access_purpose') || 'TREATMENT');
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [pendingCallback, setPendingCallback] = useState(null);

  const updatePurpose = (newPurpose) => {
    setPurpose(newPurpose);
    localStorage.setItem('sphinx_access_purpose', newPurpose);
  };

  const requirePurposeConfirmation = (callback) => {
    setPendingCallback(() => callback);
    setIsDialogOpen(true);
  };

  const handleConfirmPurpose = (selectedPurpose) => {
    updatePurpose(selectedPurpose);
    setIsDialogOpen(false);
    if (pendingCallback) {
      pendingCallback(selectedPurpose);
      setPendingCallback(null);
    }
  };

  const handleCloseDialog = () => {
    setIsDialogOpen(false);
    setPendingCallback(null);
  };

  return (
    <PurposeContext.Provider
      value={{
        purpose,
        updatePurpose,
        requirePurposeConfirmation,
        isDialogOpen,
        handleConfirmPurpose,
        handleCloseDialog,
      }}
    >
      {children}
    </PurposeContext.Provider>
  );
};

export const usePurpose = () => useContext(PurposeContext);
