import { createSlice } from '@reduxjs/toolkit';

export const settingsSlice = createSlice({
  name: 'settings',
  initialState: {
    chunk_size: 1000000,
    sample_size_per_chunk: 1000000,
    random_state: 0,
    valid_threshold: 0.5,
    category_threshold: 0.5,
  },
  reducers: {
    updateSettings: (state, action) => {
      return { ...state, ...action.payload };
    },
  },
});

export const { updateSettings } = settingsSlice.actions;

export default settingsSlice.reducer;
