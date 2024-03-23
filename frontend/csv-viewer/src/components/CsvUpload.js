import React, { useState } from 'react';
import axios from 'axios';
import { Button, Input } from '@mui/material';
import { useSelector } from 'react-redux';

function CsvUpload({ onUploadSuccess }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const settings = useSelector((state) => state.settings);

  const handleFileSelect = (event) => {
    setSelectedFile(event.target.files[0]);
  };

  const handleUpload = () => {
    const formData = new FormData();
    formData.append('document', selectedFile);

    formData.append('chunk_size', parseInt(settings.chunk_size));
    formData.append('sample_size_per_chunk', parseInt(settings.sample_size_per_chunk));
    formData.append('random_state', parseInt(settings.random_state, 0));
    formData.append('valid_threshold', parseFloat(settings.valid_threshold));
    formData.append('category_threshold', parseFloat(settings.category_threshold));

    axios.post(`${process.env.REACT_APP_API_BASE_URL}/api/type-infer/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        'X-API-KEY': process.env.REACT_APP_API_KEY,
      },
    })
    .then(response => {
      console.log(response.data);
      onUploadSuccess(response.data);
      alert('File uploaded and processed successfully.');
    })
    .catch(error => console.error('Error uploading file', error));
  };

  return (
    <div>
      <Input type="file" onChange={handleFileSelect} />
      <Button variant="contained" color="primary" onClick={handleUpload} disabled={!selectedFile}>
        Upload
      </Button>
    </div>
  );
}

export default CsvUpload;
