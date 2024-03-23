import React, { useState } from 'react';
import AppHeader from './components/AppHeader';
import CsvFileList from './components/CsvFileList';
import CsvFileViewer from './components/CsvFileViewer';
import CsvUpload from './components/CsvUpload';
import SettingsDialog from './components/SettingsDialog';
import { CssBaseline, Container, Grid, Box, Paper, Typography } from '@mui/material';
import theme from './theme';
import { ThemeProvider } from '@mui/material/styles';

function App() {
  const [selectedFileName, setSelectedFileName] = useState('');
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [refreshFileList, setRefreshFileList] = useState(false);

  const handleFileSelect = (fileName) => {
    setSelectedFileName(fileName);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AppHeader onSettingsOpen={() => setIsSettingsOpen(true)} />
      <Container maxWidth="xl">
        <Box sx={{ display: 'flex', marginTop: 3 }}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={3}>
              <Paper elevation={3} sx={{ height: 'calc(100vh - 100px)', overflow: 'auto', position: 'relative', display: 'flex', flexDirection: 'column' }}>
                <Typography variant="h6" component="div" sx={{ padding: 2, borderBottom: '1px solid #ddd' }}>
                  File List
                </Typography>
                <Box sx={{ padding: 2, flexGrow: 1 }}>
                  <CsvFileList onSelectFile={handleFileSelect} refresh={refreshFileList} />
                </Box>
                <Box sx={{ padding: 2, borderTop: '1px solid #ddd', marginTop: 'auto' }}>
                  <CsvUpload onUploadSuccess={() => setRefreshFileList(prev => !prev)} />
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={9}>
              <Paper elevation={3} sx={{ padding: 2, height: 'calc(100vh - 100px)', overflow: 'auto' }}>
                <CsvFileViewer fileName={selectedFileName} />
              </Paper>
            </Grid>
          </Grid>
        </Box>
        <SettingsDialog
          open={isSettingsOpen}
          onClose={() => setIsSettingsOpen(false)}
          onSave={(settings) => {
            console.log("Settings saved:", settings);

          }}
        />
      </Container>
    </ThemeProvider>
  );
}

export default App;
