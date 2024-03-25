import React, { useEffect, useState } from 'react';
import axios from 'axios';
import Papa from 'papaparse';
import { Accordion, AccordionSummary, AccordionDetails, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography, Box, TablePagination } from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import { Button, FormControl, InputLabel, Select, MenuItem, Grid } from '@mui/material';
import ReactJson from 'react-json-view';


function CsvFileViewer({ fileName }) {
  const [fileData, setFileData] = useState([]);
  const [metadata, setMetadata] = useState({});
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(50);
  const [userDefinedTypes, setUserDefinedTypes] = useState({});

  const dataTypes = [
    'Int8', 'Int16', 'Int32', 'Int64',
    'float16', 'float32', 'float64',
    'complex64', 'complex128',
    'object', 'bool',
    'category', 'datetime64[ns]', 'timedelta64[ns]'
  ];

  const handleUserDefinedTypeChange = (column, type) => {
    setUserDefinedTypes(prev => ({ ...prev, [column]: type }));
  };

  const saveUserDefinedTypes = () => {
      const data = {
        file_name: fileName,
        columns: Object.entries(userDefinedTypes).map(([name, new_dtype]) => ({
          name,
          new_dtype
        }))
      };

      axios.post(`${process.env.REACT_APP_API_BASE_URL}/api/update-dtype/`, data, {
        headers: { 'X-API-KEY': process.env.REACT_APP_API_KEY }
      })
      .then(() => {
        alert('Data types updated successfully.');
        fetchMetadata(); // Fetch the updated metadata after successful update
      })
      .catch(error => console.error('Error updating data types', error));
    };

  const fetchMetadata = () => {
      const metadataUrl = `${process.env.REACT_APP_API_BASE_URL}/api/fetch-file-metadata/${fileName}`;
      axios.get(metadataUrl, { headers: { 'X-API-KEY': process.env.REACT_APP_API_KEY } })
        .then((response) => {
          console.log("Fetched updated metadata:", response.data);
          setMetadata(response.data.metadata);

          // Initialize userDefinedTypes with user_defined_type from metadata
          const initialUserDefinedTypes = {};
          response.data.metadata.forEach(column => {
            initialUserDefinedTypes[column.name] = column.user_defined_type || column.pandas_type;
          });
          setUserDefinedTypes(initialUserDefinedTypes);
        })
        .catch(error => console.error('Error fetching updated metadata', error));
    };

  useEffect(() => {
    if (fileName) {
      // Fetch metadata
      fetchMetadata();

      // Fetch and parse CSV file
      const fileUrl = `${process.env.REACT_APP_API_BASE_URL}/api/fetch-file-content/${fileName}`;
      axios.get(fileUrl, { responseType: 'blob', headers: { 'X-API-KEY': process.env.REACT_APP_API_KEY } })
        .then(response => {
          const reader = new FileReader();
          reader.onload = function(event) {
            Papa.parse(event.target.result, { header: true, skipEmptyLines: true, complete: results => setFileData(results.data) });
          };
          reader.readAsText(response.data);
        })
        .catch(error => console.error('Error downloading and parsing file', error));
    }
  }, [fileName]);

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = event => {
    setRowsPerPage(+event.target.value);
    setPage(0);
  };

  return (
    <Box>
      {fileData.length > 0 && (
        <>
          <Accordion defaultExpanded>
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Typography>Table Content</Typography>
            </AccordionSummary>
            <AccordionDetails>
              <TableContainer component={Paper}>
                <Table sx={{ minWidth: 650 }}>
                  <TableHead sx={{ backgroundColor: 'primary.main' }}>
                    <TableRow>
                      {Object.keys(fileData[0] || {}).map((header, index) => (
                        <TableCell key={index} sx={{ color: 'common.white', fontWeight: 'bold' }}>{header}</TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {fileData.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage).map((row, rowIndex) => (
                      <TableRow key={rowIndex} sx={{ '&:last-child td, &:last-child th': { border: 0 } }}>
                        {Object.values(row).map((cell, cellIndex) => (
                          <TableCell key={cellIndex}>{cell}</TableCell>
                        ))}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <TablePagination
                component="div"
                count={fileData.length}
                page={page}
                onPageChange={handleChangePage}
                rowsPerPage={rowsPerPage}
                onRowsPerPageChange={handleChangeRowsPerPage}
              />
            </AccordionDetails>
          </Accordion>
        </>
      )}

      {Object.keys(metadata).length > 0 && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>Metadata</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <ReactJson
              src={metadata}
              theme="rjv-default"
              collapsed={false}
              enableClipboard={false}
              displayDataTypes={false}
            />
          </AccordionDetails>
        </Accordion>
      )}

      {metadata.length > 0 && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography>User-Defined Custom Types</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {metadata.map((column, index) => (
                <Grid item xs={4} key={index}> {/* xs={4} makes it 3 items per row */}
                  <Box display="flex" alignItems="center">
                    <FormControl variant="outlined" size="small" fullWidth>
                      <InputLabel>{column.name}</InputLabel>
                      <Select
                        label={column.name}
                        value={userDefinedTypes[column.name] || column.pandas_type}
                        onChange={(e) => handleUserDefinedTypeChange(column.name, e.target.value)}
                        style={{ width: 200 }}
                      >
                        {dataTypes.map((type) => (
                          <MenuItem key={type} value={type}>{type}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Box>
                </Grid>
              ))}
            </Grid>
            <Button variant="contained" color="primary" onClick={saveUserDefinedTypes} style={{ marginTop: 16 }}>Save Types</Button>
          </AccordionDetails>
        </Accordion>
      )}
    </Box>
  );
}

export default CsvFileViewer;
