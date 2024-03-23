import { configureStore } from '@reduxjs/toolkit';
import settingsReducer from './features/settings/settingsSlice';

export const store = configureStore({
  reducer: {
    settings: settingsReducer,
  },
});
