import Papa from 'papaparse';
import * as XLSX from 'xlsx';

// Function to load and parse file (CSV or Excel)
export const loadCSVData = (file) => {
  return new Promise((resolve, reject) => {
    const fileExtension = file.name.split('.').pop().toLowerCase();
    
    if (fileExtension === 'csv') {
      // Handle CSV files
      Papa.parse(file, {
        header: true,
        dynamicTyping: true, // Automatically convert numeric values
        skipEmptyLines: true,
        complete: (results) => {
          if (results.errors.length) {
            // Check for specific error types
            const error = results.errors[0];
            if (error.type === 'TooFewFields') {
              reject(new Error(`CSV format error: The file has incorrect number of columns. Expected 12 columns but found ${error.row.length}. Please check if your CSV file has all required columns.`));
            } else if (error.type === 'TooManyFields') {
              reject(new Error(`CSV format error: The file has too many columns. Expected 12 columns but found ${error.row.length}. Please check if your CSV file has the correct format.`));
            } else {
              reject(new Error(`CSV parsing error: ${error.message}. Please check if your CSV file is properly formatted.`));
            }
          } else if (!results.data || results.data.length === 0) {
            reject(new Error('The CSV file is empty or contains no valid data'));
          } else {
            // Validate the number of columns
            const expectedColumns = 12;
            const actualColumns = Object.keys(results.data[0] || {}).length;
            
            if (actualColumns !== expectedColumns) {
              reject(new Error(`CSV format error: The file has ${actualColumns} columns but ${expectedColumns} are required. Please check if your CSV file has all required columns.`));
            } else {
              resolve(results.data);
            }
          }
        },
        error: (error) => {
          reject(new Error(`Failed to parse CSV: ${error.message}. Please check if your CSV file is properly formatted.`));
        }
      });
    } else if (['xlsx', 'xls'].includes(fileExtension)) {
      // Handle Excel files
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = e.target.result;
          const workbook = XLSX.read(data, { type: 'array' });
          
          if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
            throw new Error('Excel file contains no sheets');
          }
          
          const firstSheetName = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheetName];
          
          if (!worksheet) {
            throw new Error('Could not read the first sheet');
          }
          
          const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          
          if (!jsonData || jsonData.length < 2) {
            throw new Error('Excel file is empty or contains no valid data');
          }
          
          // Convert to the same format as CSV data
          const headers = jsonData[0];
          const rows = jsonData.slice(1).map(row => {
            const obj = {};
            headers.forEach((header, index) => {
              obj[header] = row[index];
            });
            return obj;
          });
          
          resolve(rows);
        } catch (error) {
          reject(new Error(`Failed to process Excel file: ${error.message}`));
        }
      };
      reader.onerror = (error) => reject(new Error(`Failed to read Excel file: ${error.message}`));
      reader.readAsArrayBuffer(file);
    } else {
      reject(new Error('Unsupported file format. Please upload a CSV or Excel file (.csv, .xlsx, .xls)'));
    }
  });
};

// Function to validate and prepare the CSV data for training
export const prepareTrainingData = (data) => {
  // Check if data has required columns
  const requiredColumns = [
    'category', 'subcategory', 'brand', 'model', 
    'age_years', 'condition', 'weight_kg', 'original_price',
    'scrap_material', 'location', 'demand_supply_index', 'estimated_price'
  ];
  
  // Get the actual columns from the data
  const actualColumns = Object.keys(data[0] || {});
  
  // Check if all required columns exist
  const missingColumns = requiredColumns.filter(col => !actualColumns.includes(col));
  
  if (missingColumns.length > 0) {
    throw new Error(`Missing required columns: ${missingColumns.join(', ')}`);
  }
  
  // Filter out any rows with missing values
  const cleanData = data.filter(row => {
    return requiredColumns.every(col => row[col] !== undefined && row[col] !== null && row[col] !== '');
  });
  
  return cleanData;
};

// Function to save the training data to localStorage
export const saveTrainingData = (data) => {
  localStorage.setItem('ewaste-training-data', JSON.stringify(data));
};

// Function to load the training data from localStorage
export const loadTrainingData = () => {
  const data = localStorage.getItem('ewaste-training-data');
  return data ? JSON.parse(data) : null;
};