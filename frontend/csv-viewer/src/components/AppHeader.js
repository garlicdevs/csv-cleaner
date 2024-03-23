import { AppBar, Toolbar, IconButton, Typography } from '@mui/material';
import SettingsIcon from '@mui/icons-material/Settings';

function AppHeader({ onSettingsOpen }) {
  return (
    <AppBar position="static" style={{ width: '100%' }}>
      <Toolbar>
        <IconButton edge="start" color="inherit" aria-label="settings" onClick={onSettingsOpen}>
          <SettingsIcon />
        </IconButton>
        <Typography variant="h6" style={{ flexGrow: 1, marginLeft: 5 }}>
          CSV Cleaner
        </Typography>
      </Toolbar>
    </AppBar>
  );
}

export default AppHeader;
