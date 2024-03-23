import { List, ListItem, ListItemText } from '@mui/material';
import { useEffect, useState } from 'react';
import axios from 'axios';

function CsvFileList({ onSelectFile, refresh }) {
  const [files, setFiles] = useState([]);

  useEffect(() => {
    axios.get(`${process.env.REACT_APP_API_BASE_URL}/api/list-csv-files/`, { headers: { 'X-API-KEY': process.env.REACT_APP_API_KEY } })
      .then(response => {
        // Assuming the response is an array of objects with fileName as a key
        setFiles(response.data);
      })
      .catch(error => console.error('Error fetching files', error));
  }, [refresh]);

  return (
    <List>
      {files.map((file, index) => (
        // Use file.fileName to access the name of the file
        <ListItem button key={index} onClick={() => onSelectFile(file.fileName)}>
          <ListItemText primary={file.fileName} />
        </ListItem>
      ))}
    </List>
  );
}

export default CsvFileList;
