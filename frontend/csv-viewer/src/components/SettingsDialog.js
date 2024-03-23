import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { updateSettings } from '../features/settings/settingsSlice';
import { Dialog, DialogTitle, DialogContent, TextField, DialogActions, Button, Snackbar, Alert } from '@mui/material';
import { Tooltip, IconButton } from '@mui/material';
import HelpOutlineIcon from '@mui/icons-material/HelpOutline';


function SettingsDialog({ open, onClose }) {
  const dispatch = useDispatch();
  const settings = useSelector((state) => state.settings);
  const [localSettings, setLocalSettings] = useState(settings);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setLocalSettings({ ...localSettings, [name]: parseFloat(value) });
  };

  const handleSave = () => {
    const errorMessage = validateSettings();
    if (errorMessage) {
      setError(errorMessage);
      return; // Prevent saving if there's an error
    }
    dispatch(updateSettings(localSettings));
    onClose();
  };

  const [error, setError] = useState('');

  const validateSettings = () => {
    const { chunk_size, sample_size_per_chunk, valid_threshold, category_threshold } = settings;
    if (sample_size_per_chunk > chunk_size) {
      return "Sample size must be smaller than chunk size.";
    }
    if (valid_threshold < 0 || valid_threshold > 1 || category_threshold < 0 || category_threshold > 1) {
      return "Threshold values should be >= 0 and <= 1.";
    }
    return "";
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Algorithm Settings</DialogTitle>
      <DialogContent>
        <TextField
          margin="dense"
          id="chunk_size"
          name="chunk_size"
          label="Chunk Size"
          type="number"
          fullWidth
          variant="outlined"
          value={localSettings.chunk_size || settings.chunk_size}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <Tooltip title="The number of rows per chunk for processing. Larger chunk sizes may increase memory usage but can improve processing speed.">
                <IconButton>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ),
          }}
        />
        <TextField
          margin="dense"
          id="sample_size_per_chunk"
          name="sample_size_per_chunk"
          label="Sample Size Per Chunk"
          type="number"
          fullWidth
          variant="outlined"
          value={localSettings.sample_size_per_chunk || settings.sample_size_per_chunk}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <Tooltip title="Is used when the number of rows too large, the algorithm will infer the type by randomly sampling part of the rows rather than checking the whole file rows.">
                <IconButton>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ),
          }}
        />

        <TextField
          margin="dense"
          id="random_state"
          name="random_state"
          label="Random State"
          type="number"
          fullWidth
          variant="outlined"
          value={localSettings.random_state || settings.random_state}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <Tooltip title="Is used together with sample size to initialize the initial state of the random value. Use it only if you want to retry the algorithm with different random sampling, making it more sure about the type.">
                <IconButton>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ),
          }}
        />

        <TextField
          margin="dense"
          id="valid_threshold"
          name="valid_threshold"
          label="Valid Threshold"
          type="number"
          fullWidth
          variant="outlined"
          value={localSettings.valid_threshold || settings.valid_threshold}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <Tooltip title="Is used to determine the majority of rows in the CSV falling into a specific type. For example, if the valid threshold is 0.5, it means the algorithm will decide it is an int type if more than 50% of rows must be int. Use it to increase confidence.">
                <IconButton>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ),
          }}
        />

        <TextField
          margin="dense"
          id="category_threshold"
          name="category_threshold"
          label="Category Threshold"
          type="number"
          fullWidth
          variant="outlined"
          value={localSettings.category_threshold || settings.category_threshold}
          onChange={handleChange}
          InputProps={{
            endAdornment: (
              <Tooltip title="Is used in the category type when at least 50% of rows are unique values (if the value is 0.5).">
                <IconButton>
                  <HelpOutlineIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            ),
          }}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave}>Save</Button>
      </DialogActions>
      {error && (
        <Snackbar open={Boolean(error)} autoHideDuration={6000} onClose={() => setError('')}>
          <Alert onClose={() => setError('')} severity="error" sx={{ width: '100%' }}>
            {error}
          </Alert>
        </Snackbar>
      )}
    </Dialog>
  );
}

export default SettingsDialog;
